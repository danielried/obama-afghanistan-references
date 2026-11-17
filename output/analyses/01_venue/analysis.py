#!/usr/bin/env python3
"""01_venue: Afghanistan passages by speech type (venue) -- score, category mix, VADER tone, mentions per 10k chars.

Read-only on the project root. Run with:
  .venv/bin/python -I output/analyses/01_venue/analysis.py
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import itertools
import json
import math
import re
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

ROOT = Path(str(PROJECT) + "")
OUT = Path(__file__).resolve().parent
DB = ROOT / "data" / "speeches.db"
MIN_N = 10                      # minimum passages per group for tests
THRESH = 50                     # primary "high-likelihood" threshold (final_score_pct >= 50)
SENS = [30, 50, 70]

# --- paragraph labelling, mirrors src/obama_afghan/splitter.py and detect.py (read-only copy) ---
_PARA = re.compile(r"\n\s*\n|\r\n\s*\r\n")
_EDITOR = re.compile(r"^\s*(?:NOTE|Note):")
_QUESTIONER = re.compile(r"^\s*(?:Q\.|Audience Member|Audience member|Moderator|Reporter|Question)[ :.]")


def para_spans(text):
    spans, pos = [], 0
    seps = list(_PARA.finditer(text))
    if not seps and text.count("\n") > 3:
        seps = list(re.finditer(r"\n", text))
    for m in seps + [None]:
        end = m.start() if m else len(text)
        if text[pos:end].strip():
            spans.append((pos, end))
        pos = m.end() if m else len(text)
    return spans


def label_paras(text):
    out = []
    for ps, pe in para_spans(text):
        head = text[ps:ps + 40]
        lab = "editor" if _EDITOR.match(head) else "questioner" if _QUESTIONER.match(head) else "speaker"
        out.append((lab, ps, pe))
    return out


def poisson_ci(k, expo, alpha=0.05):
    rate = k / expo
    lo = 0.0 if k == 0 else stats.chi2.ppf(alpha / 2, 2 * k) / 2
    hi = stats.chi2.ppf(1 - alpha / 2, 2 * (k + 1)) / 2
    return rate, lo / expo, hi / expo   # count CI -> rate CI per exposure unit


def kw_eta2(H, k, n):
    return max(0.0, (H - k + 1) / (n - k))


def cramers_v(chi2, n, shape):
    return math.sqrt(chi2 / (n * (min(shape) - 1)))


def pairwise(df, col, groups, tag):
    rows = []
    for a, b in itertools.combinations(groups, 2):
        x = df.loc[df.g == a, col].dropna().values
        y = df.loc[df.g == b, col].dropna().values
        U, p = stats.mannwhitneyu(x, y, alternative="two-sided")
        rows.append({"outcome": tag, "a": a, "b": b, "n_a": len(x), "n_b": len(y),
                     "median_a": float(np.median(x)), "median_b": float(np.median(y)),
                     "U_a": float(U), "p": float(p), "rank_biserial_a_vs_b": 2 * U / (len(x) * len(y)) - 1})
    out = pd.DataFrame(rows)
    out["p_holm"] = multipletests(out["p"], method="holm")[1]
    return out


def main():
    # ---------------- load ----------------
    idx_all = pd.read_csv(ROOT / "output/speeches_index.csv")
    dup = idx_all["dup_of"].notna() & (idx_all["dup_of"].astype(str).str.strip() != "")
    idx = idx_all[~dup].copy()
    print(f"speeches index: {len(idx_all)} rows, dup_of non-empty excluded: {int(dup.sum())}, kept: {len(idx)}")

    refs = pd.read_csv(ROOT / "output/references.csv")
    print(f"references.csv rows: {len(refs)}")
    refs = refs[refs["speech_id"].isin(idx["id"])].copy()
    print(f"refs in kept speeches: {len(refs)}")

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    raw = dict(con.execute("select id, raw_text from speeches"))
    con.close()

    # ---------------- paragraph labels per speech ----------------
    plabs = {}
    chars = {}          # sid -> {'speaker': n, 'questioner': n, 'editor': n}
    len_match = 0
    for sid in idx["id"]:
        text = raw.get(sid) or ""
        pl = label_paras(text)
        plabs[sid] = pl
        c = {"speaker": 0, "questioner": 0, "editor": 0}
        for lab, ps, pe in pl:
            c[lab] += pe - ps
        chars[sid] = c
    idx["raw_len"] = idx["id"].map(lambda s: len(raw.get(s) or ""))
    len_match = float((idx["raw_len"] == idx["text_len"]).mean())
    print(f"index text_len == len(raw_text): {len_match:.4f}")

    # ---------------- ref-level speaker label ----------------
    def ref_info(row):
        pl = plabs[row.speech_id]
        p = int(row.para_idx)
        if p >= len(pl):
            return pd.Series({"para_label": "NA", "in_para": False})
        lab, ps, pe = pl[p]
        inside = ps <= int(row.char_start) and int(row.char_end) <= pe
        return pd.Series({"para_label": lab, "in_para": inside})

    info = refs.apply(ref_info, axis=1)
    refs = pd.concat([refs, info], axis=1)
    print("para_label counts:", refs["para_label"].value_counts().to_dict())
    print(f"passage span inside labelled paragraph: {refs['in_para'].mean():.4f}")
    xt = pd.crosstab(refs["para_label"] == "questioner", refs["rationale"].fillna("").str.contains("questioner_not_president"))
    print("crosstab computed questioner vs rationale flag:\n", xt.to_string())

    refs = refs.merge(idx[["id", "type", "title", "date"]], left_on="speech_id", right_on="id", how="left")
    refs["score"] = refs["final_score_pct"].astype(float)
    refs["tone"] = refs["tone"].astype(float)
    refs["cat"] = refs["category"].replace({"unrelated": "non_war_or_background",
                                            "political_background": "non_war_or_background"})

    def group_of(row):
        if row["type"] in ("press_conference", "interview"):
            return f"{row['type']}|{'questioner' if row['para_label'] == 'questioner' else 'president'}"
        return row["type"]

    refs["g"] = refs.apply(group_of, axis=1)
    # questioner-labelled passages in other venue types (kept in their type, reported only)
    other_q = refs[(refs["para_label"] == "questioner") & (~refs["type"].isin(["press_conference", "interview"]))]
    print("questioner-labelled passages in non-press/interview types:", other_q["type"].value_counts().to_dict())
    print("editor-labelled passages (should be 0):", int((refs["para_label"] == "editor").sum()))

    # ---------------- group summary ----------------
    cnt = refs["g"].value_counts()
    keep = [g for g in cnt.index if cnt[g] >= MIN_N]
    dropped = {g: int(cnt[g]) for g in cnt.index if cnt[g] < MIN_N}
    print("groups kept (n>=%d):" % MIN_N, {g: int(cnt[g]) for g in keep})
    print("groups dropped (n<%d):" % MIN_N, dropped)
    d = refs[refs["g"].isin(keep)].copy()

    summ = d.groupby("g").agg(
        n=("score", "size"),
        score_median=("score", "median"),
        score_mean=("score", "mean"),
        tone_median=("tone", "median"),
        tone_mean=("tone", "mean"),
        n_speeches=("speech_id", "nunique"),
        war_share=("cat", lambda s: s.isin(["war_direct", "war_adjacent"]).mean()),
        hi50_share=("score", lambda s: (s >= THRESH).mean()),
    ).reset_index()
    summ.to_csv(OUT / "group_summary.csv", index=False)
    print("\nGROUP SUMMARY\n", summ.round(3).to_string(index=False))

    results = {"n_refs_kept": int(len(d)), "groups": keep, "dropped_groups": dropped}

    # ---------------- Kruskal-Wallis + pairwise ----------------
    for col, tag in [("score", "war_likelihood_score"), ("tone", "vader_tone")]:
        samples = [d.loc[d.g == g, col].dropna().values for g in keep]
        H, p = stats.kruskal(*samples)
        N = sum(len(s) for s in samples)
        eta2 = kw_eta2(H, len(keep), N)
        print(f"\nKRUSKAL {tag}: H={H:.3f}, df={len(keep)-1}, p={p:.3g}, eta2_H={eta2:.4f}, N={N}")
        results[f"kw_{tag}"] = {"H": float(H), "df": len(keep) - 1, "p": float(p), "eta2_H": float(eta2), "N": int(N)}
        pw = pairwise(d, col, keep, tag)
        pw.to_csv(OUT / f"pairwise_{tag}.csv", index=False)
        sig = pw[pw["p_holm"] < 0.05]
        print(f"pairwise {tag}: {len(pw)} tests, Holm p<0.05: {len(sig)}")
        print(pw.round(4).to_string(index=False))

    # ---------------- category mix ----------------
    ct = pd.crosstab(d["g"], d["cat"])
    chi2, pc, dof, expd = stats.chi2_contingency(ct)
    V = cramers_v(chi2, ct.values.sum(), ct.shape)
    low_exp = float((expd < 5).mean())
    print(f"\nCATEGORY chi2={chi2:.2f}, dof={dof}, p={pc:.3g}, Cramer V={V:.4f}, share cells expected<5={low_exp:.3f}")
    print(ct.to_string())
    ct.to_csv(OUT / "category_crosstab.csv")
    results["category_chi2"] = {"chi2": float(chi2), "dof": int(dof), "p": float(pc), "cramers_v": float(V),
                                "share_cells_expected_lt5": low_exp, "collapsed": "unrelated+political_background"}

    # ---------------- high-likelihood share, sensitivity 30/50/70 ----------------
    sens_rows = []
    for t in SENS:
        hi = (d["score"] >= t).astype(int)
        tab = pd.crosstab(d["g"], hi)
        c2, pp, dd, _ = stats.chi2_contingency(tab)
        V2 = cramers_v(c2, tab.values.sum(), tab.shape)
        shares = (d.assign(hi=hi).groupby("g")["hi"].mean()).round(4).to_dict()
        sens_rows.append({"threshold": t, "chi2": c2, "dof": dd, "p": pp, "cramers_v": V2, "shares": shares})
        print(f"\nHI>={t}: chi2={c2:.2f}, dof={dd}, p={pp:.3g}, V={V2:.4f}")
        print({k: round(v, 3) for k, v in shares.items()})
    results["hi_share_sensitivity"] = sens_rows
    pd.DataFrame([{k: v for k, v in r.items() if k != "shares"} for r in sens_rows]).to_csv(
        OUT / "hi_share_sensitivity.csv", index=False)

    # ---------------- questioner vs president scoring (circularity check) ----------------
    q = d[d["g"].str.endswith("|questioner")]
    p_ = d[d["g"].str.endswith("|president") & d["type"].isin(["press_conference", "interview"])]
    if len(q) >= 3:
        U, pq = stats.mannwhitneyu(q["score"], p_["score"], alternative="two-sided")
        print(f"\nquestioner vs president (press+interview) score: n={len(q)} vs {len(p_)}, "
              f"median {q['score'].median()} vs {p_['score'].median()}, p={pq:.3g}")
        results["questioner_vs_president_score"] = {"n_q": int(len(q)), "n_p": int(len(p_)),
                                                    "median_q": float(q["score"].median()),
                                                    "median_p": float(p_["score"].median()), "p": float(pq)}

    # ---------------- sensitivity: remove venue-linked score features ----------------
    # venue_title (+4) keys on speech TITLE words (troops, Bagram, NATO, Afghanistan, ...) -> venue-dependent by design.
    # Approximation: subtract 4 from passages whose rationale has venue_title (clip 0..100).
    d["vt"] = d["rationale"].fillna("").str.contains("venue_title")
    d["score_novt"] = (d["score"] - 4 * d["vt"]).clip(0, 100)
    vt_share = d.groupby("g")["vt"].mean().round(3).to_dict()
    print("\nvenue_title bonus share by group:", vt_share)
    s_samples = [d.loc[d.g == g, "score_novt"].values for g in keep]
    Hn, pn = stats.kruskal(*s_samples)
    print(f"KW score without venue_title bonus: H={Hn:.2f}, p={pn:.3g}, eta2_H={kw_eta2(Hn, len(keep), len(d)):.4f}")
    med_novt = d.groupby("g")["score_novt"].median().to_dict()
    print("median score without venue_title bonus:", med_novt)
    results["sensitivity_no_venue_title"] = {"vt_share": vt_share, "H": float(Hn), "p": float(pn),
                                             "eta2_H": float(kw_eta2(Hn, len(keep), len(d))), "medians": med_novt}
    # president-only venue comparison (drops questioner groups, whose -18 penalty is built into the score)
    pres_groups = [g for g in keep if not g.endswith("|questioner")]
    Hp, pp_ = stats.kruskal(*[d.loc[d.g == g, "score"].values for g in pres_groups])
    print(f"KW score, questioner groups excluded (k={len(pres_groups)}): H={Hp:.2f}, p={pp_:.3g}")
    results["sensitivity_president_only"] = {"groups": pres_groups, "H": float(Hp), "p": float(pp_)}

    # ---------------- mentions per 10k chars ----------------
    units = []
    per_speech_refs = refs.groupby("speech_id").size()
    for _, r in idx.iterrows():
        sid, t = r["id"], r["type"]
        nref = int(per_speech_refs.get(sid, 0))
        if t in ("press_conference", "interview"):
            rr = refs[refs["speech_id"] == sid]
            n_q = int((rr["para_label"] == "questioner").sum())
            n_p = int((rr["para_label"] == "speaker").sum())
            units.append({"speech_id": sid, "type": t, "unit": f"{t}|president", "count": n_p,
                          "chars": chars[sid]["speaker"]})
            units.append({"speech_id": sid, "type": t, "unit": f"{t}|questioner", "count": n_q,
                          "chars": chars[sid]["questioner"]})
        units.append({"speech_id": sid, "type": t, "unit": t, "count": nref, "chars": int(r["raw_len"])})
    U_df = pd.DataFrame(units)
    rate_rows = []
    for u, grp in U_df.groupby("unit"):
        k = int(grp["count"].sum()); ex = float(grp["chars"].sum())
        if ex <= 0:
            continue
        rate, lo, hi_ = poisson_ci(k, ex / 1e4)
        rate_rows.append({"unit": u, "speeches": int(grp["speech_id"].nunique()), "passages": k,
                          "chars": int(ex), "per_10k_chars": rate, "ci_lo": lo, "ci_hi": hi_})
    rates = pd.DataFrame(rate_rows).sort_values("per_10k_chars", ascending=False)
    rates.to_csv(OUT / "rates_per_10k_chars.csv", index=False)
    print("\nRATES per 10k chars\n", rates.round(3).to_string(index=False))
    results["rates"] = rates.round(4).to_dict(orient="records")

    # speech-level NB GLM by type (whole-type, exposure = text_len), reference = remarks
    sp = idx[["id", "type", "raw_len"]].rename(columns={"raw_len": "text_len"}).copy()
    sp["y"] = sp["id"].map(per_speech_refs).fillna(0).astype(int)
    sp = sp[sp["text_len"] > 0]
    types = [t for t in sp["type"].value_counts().index if (sp["type"] == t).sum() >= 1]
    base = "remarks"
    X = pd.get_dummies(sp["type"], drop_first=False).astype(float)
    X = X.drop(columns=[base])
    X = sm.add_constant(X, has_constant="add")
    nb_full = sm.NegativeBinomial(sp["y"].values, X.values, exposure=sp["text_len"].values).fit(disp=0, maxiter=500)
    nb_null = sm.NegativeBinomial(sp["y"].values, np.ones((len(sp), 1)), exposure=sp["text_len"].values).fit(disp=0, maxiter=500)
    LR = 2 * (nb_full.llf - nb_null.llf)
    dfk = X.shape[1] - 1
    p_lr = stats.chi2.sf(LR, dfk)
    print(f"\nNB GLM speech-level (exposure=text_len), base={base}: alpha={nb_full.params[-1]:.4f}, "
          f"LR={LR:.2f}, df={dfk}, p={p_lr:.3g}, n speeches={len(sp)}, passages={int(sp['y'].sum())}")
    irr = []
    for i, name in enumerate(X.columns[1:], start=1):
        b = nb_full.params[i]; se = nb_full.bse[i]
        irr.append({"type": name, "IRR_vs_remarks": math.exp(b), "ci_lo": math.exp(b - 1.96 * se),
                    "ci_hi": math.exp(b + 1.96 * se), "p": 2 * stats.norm.sf(abs(b / se))})
    irr = pd.DataFrame(irr)
    irr_holm = irr.copy(); irr_holm["p_holm"] = multipletests(irr["p"], method="holm")[1]
    irr_holm.to_csv(OUT / "nb_glm_irr_vs_remarks.csv", index=False)
    print(irr_holm.round(4).to_string(index=False))
    results["nb_glm"] = {"alpha": float(nb_full.params[-1]), "LR": float(LR), "df": int(dfk), "p": float(p_lr),
                         "n_speeches": int(len(sp)), "passages": int(sp["y"].sum()), "base": base}
    results["nb_irr"] = irr_holm.round(5).to_dict(orient="records")

    # KW on per-speech rate across whole types (includes zero-hit speeches)
    sp["rate"] = sp["y"] / sp["text_len"] * 1e4
    kw_samples = [sp.loc[sp.type == t, "rate"].values for t in types if (sp.type == t).sum() >= MIN_N]
    kw_types = [t for t in types if (sp.type == t).sum() >= MIN_N]
    H2, p2 = stats.kruskal(*kw_samples)
    print(f"KW per-speech rate across types (n>={MIN_N}): H={H2:.2f}, df={len(kw_types)-1}, p={p2:.3g}")
    results["kw_speech_rate"] = {"H": float(H2), "df": len(kw_types) - 1, "p": float(p2), "types": kw_types}

    # ---------------- chart ----------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    order = sorted(keep, key=lambda g: d.loc[d.g == g, "score"].median())
    axes[0].boxplot([d.loc[d.g == g, "score"].values for g in order], vert=False, showfliers=False)
    axes[0].set_yticks(range(1, len(order) + 1))
    axes[0].set_yticklabels([f"{g} (n={int((d.g == g).sum())})" for g in order], fontsize=8)
    axes[0].axvline(THRESH, ls="--", lw=0.8, color="grey")
    axes[0].set_xlabel("war-likelihood score (final_score_pct)")
    axes[0].set_title("Score by venue group (dashed = 50)")
    rr = rates.sort_values("per_10k_chars")
    y = np.arange(len(rr))
    axes[1].errorbar(rr["per_10k_chars"], y,
                     xerr=[rr["per_10k_chars"] - rr["ci_lo"], rr["ci_hi"] - rr["per_10k_chars"]],
                     fmt="o", color="black", ecolor="grey", capsize=3)
    axes[1].set_yticks(y)
    axes[1].set_yticklabels(rr["unit"], fontsize=8)
    axes[1].set_xlabel("Afghanistan passages per 10k chars (exact Poisson 95% CI)")
    axes[1].set_title("Mention rate by venue unit")
    fig.suptitle("01_venue: Afghanistan passages by speech type (rule-based scores, not ground truth)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "chart_venue.png", dpi=130)

    with open(OUT / "results.json", "w") as fh:
        json.dump(results, fh, indent=2, default=str)
    print("\nwrote", OUT / "results.json")


if __name__ == "__main__":
    main()
