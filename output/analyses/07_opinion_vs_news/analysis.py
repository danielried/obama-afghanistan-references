"""07 opinion vs news: do opinion/editorial/analysis reaction items track statement tone differently
than news_report items?  Read-only on the project root. Outputs written to this folder.

Run: .venv/bin/python -I output/analyses/07_opinion_vs_news/analysis.py
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJ = Path(str(PROJECT) + "")
OUT = Path(__file__).resolve().parent
WINDOW = 14
RNG = np.random.default_rng(20260116)
N_PERM = 10000
STANCE = {"positive": 1, "negative": -1, "neutral": 0, "mixed": 0}
OPINION_TYPES = {"opinion", "editorial", "analysis"}
lines = []  # text log that becomes part of RESULT.md numbers


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


# ---------- 1. items ----------
ev_json = json.loads((PROJ / "data/reactions.json").read_text(encoding="utf8"))["events"]
rows = []
for e in ev_json:
    for i in e["items"]:
        rows.append({
            "event": e["date"], "label": e["label"], "kind": i.get("kind"), "item_type": i.get("item_type"),
            "stance": i.get("stance"), "stance_researcher": i.get("stance_researcher"),
            "stance_agree": i.get("stance_agree"), "weak_evidence": i.get("weak_evidence"),
            "political_lean": i.get("political_lean"), "outlet": i.get("outlet_or_author"),
        })
items = pd.DataFrame(rows)
csv_items = pd.read_csv(PROJ / "output/reaction_items.csv")
assert len(csv_items) == len(items)
assert (csv_items["item_type"].values == items["item_type"].values).all()
assert (csv_items["stance"].values == items["stance"].values).all()
log(f"items: {len(items)} (json == reaction_items.csv on item_type and stance: True)")
log("item_type counts:", items["item_type"].value_counts().to_dict())
log("stance (final) counts:", items["stance"].value_counts().to_dict())
log(f"stance_researcher != final stance: {(items.stance != items.stance_researcher).sum()}; weak_evidence: {int(items.weak_evidence.sum())}")

items["group"] = np.where(items.item_type == "news_report", "news",
                 np.where(items.item_type.isin(OPINION_TYPES), "opinion",
                 np.where(items.item_type == "tweet", "tweet", "other")))  # poll
items["stance_num"] = items.stance.map(STANCE)
items["stance_num_res"] = items.stance_researcher.map(STANCE)
items["is_opinion"] = (items.group == "opinion").astype(int)
log("group counts:", items.group.value_counts().to_dict())

# ---------- 2. statement tone per event (recompute from references.csv) ----------
refs = pd.read_csv(PROJ / "output/references.csv", usecols=["date", "speech_id", "tone", "rationale",
                                                           "final_score_pct", "ref_id"])
refs["questioner"] = refs.rationale.fillna("").str.contains("questioner")
ev_csv = pd.read_csv(PROJ / "output/reaction_events.csv")


def tone_in_window(df, d0):
    d1 = (date.fromisoformat(d0) + timedelta(days=WINDOW)).isoformat()
    sel = df[(df.date >= d0) & (df.date <= d1) & (~df.questioner)]
    return sel


base = []
for d0 in sorted(items.event.unique()):
    sel = tone_in_window(refs, d0)
    base.append({"event": d0, "n_stmt_recomputed": len(sel), "tone_recomputed": sel.tone.mean()})
base = pd.DataFrame(base)
chk = ev_csv[["date", "n_statements", "statement_tone"]].rename(columns={"date": "event"}).merge(base, on="event")
chk["diff"] = (chk.statement_tone - chk.tone_recomputed).abs()
log("statement_tone check vs reaction_events.csv (max abs diff):", round(chk["diff"].max(), 6),
    "| n match:", bool((chk.n_statements == chk.n_stmt_recomputed).all()))

# tone per event for all 13 events (for event table)
tone_all = {r.date: r.statement_tone for r in ev_csv.itertuples()}
tone_map = dict(zip(chk.event, chk.statement_tone))

# sensitivity: restrict statements to high-likelihood passages (final_score_pct thresholds)
sens_tone = {}
for thr in (30, 50, 70):
    m = {}
    for d0 in sorted(items.event.unique()):
        sel = tone_in_window(refs, d0)
        sel = sel[sel.final_score_pct >= thr]
        m[d0] = sel.tone.mean() if len(sel) >= 3 else np.nan
    sens_tone[thr] = m

# ---------- 3. per-event indices by group ----------
def idx(sub, col="stance_num"):
    if len(sub) == 0:
        return np.nan
    return sub[col].sum() / len(sub)


def pos_neg_idx(sub, col="stance_num"):
    return idx(sub, col)


ev_rows = []
for d0, g in items.groupby("event", sort=True):
    news = g[g.group == "news"]; op = g[g.group == "opinion"]
    ev_rows.append({
        "event": d0, "label": g.label.iloc[0], "statement_tone": tone_map[d0],
        "n_news": len(news), "news_index": idx(news), "news_neg_share": (news.stance == "negative").mean() if len(news) else np.nan,
        "n_opinion": len(op), "opinion_index": idx(op), "opinion_neg_share": (op.stance == "negative").mean() if len(op) else np.nan,
        "n_other": int((g.group.isin(["other", "tweet"])).sum()),
        "all_index_main": idx(g[g.group.isin(["news", "opinion"])]),
    })
ev = pd.DataFrame(ev_rows)
log("\nper-event table (main groups news + opinion; polls/tweets excluded):")
log(ev[["event", "statement_tone", "n_news", "news_index", "n_opinion", "opinion_index", "n_other"]].round(3).to_string(index=False))


def corr_block(x, y, label, min_n=2):
    m = pd.notna(x) & pd.notna(y)
    x2, y2 = np.asarray(x[m], float), np.asarray(y[m], float)
    out = {"label": label, "n_events": int(m.sum())}
    if len(x2) >= 3 and np.std(x2) > 0 and np.std(y2) > 0:
        r, pr = stats.pearsonr(x2, y2); rho, ps = stats.spearmanr(x2, y2)
        out.update(pearson_r=round(r, 3), pearson_p=round(pr, 3), spearman_rho=round(rho, 3), spearman_p=round(ps, 3))
    else:
        out.update(pearson_r=np.nan, pearson_p=np.nan, spearman_rho=np.nan, spearman_p=np.nan)
    return out


# per-event correlations; need >=1 item of the group (a group with 1 item has index in {-1,0,1})
corrs = []
corrs.append(corr_block(ev.statement_tone, ev.news_index, "news (any n>=1)"))
corrs.append(corr_block(ev.statement_tone, ev.opinion_index, "opinion (any n>=1)"))
ev_n2n = ev[(ev.n_news >= 2)]
corrs.append(corr_block(ev_n2n.statement_tone, ev_n2n.news_index, "news (n>=2)"))
ev_o2 = ev[(ev.n_opinion >= 2)]
corrs.append(corr_block(ev_o2.statement_tone, ev_o2.opinion_index, "opinion (n>=2)"))
corr_df = pd.DataFrame(corrs)
log("\nper-event correlations (statement_tone vs group index):")
log(corr_df.to_string(index=False))

# group index difference (paired where both exist)
both = ev[(ev.n_news > 0) & (ev.n_opinion > 0)]
log(f"\nevents with both news and opinion items: {len(both)}; mean(news_index - opinion_index) = "
    f"{(both.news_index - both.opinion_index).mean():.3f}")
if len(both) >= 3:
    t = stats.ttest_rel(both.news_index, both.opinion_index)
    w = stats.wilcoxon(both.news_index, both.opinion_index) if (both.news_index != both.opinion_index).any() else None
    log(f"paired t p={t.pvalue:.3f}; wilcoxon p={(w.pvalue if w else float('nan')):.3f}")

# group-level stance distribution (level difference, not tone-tracking)
gx = items[items.group.isin(["news", "opinion"])]
ct = pd.crosstab(gx.group, gx.stance)
log("\nstance by group (news vs opinion):\n" + ct.to_string())
chi = stats.chi2_contingency(ct.values)
neg_tab = [[int((gx[gx.group == g].stance == "negative").sum()), int((gx[gx.group == g].stance != "negative").sum())] for g in ["news", "opinion"]]
fe = stats.fisher_exact(neg_tab)
log(f"chi2 (4 stances x 2 groups): chi2={chi[0]:.2f} df={chi[2]} p={chi[1]:.4f}")
log(f"negative share: news={neg_tab[0][0]}/{sum(neg_tab[0])}={neg_tab[0][0]/sum(neg_tab[0]):.3f}; "
    f"opinion={neg_tab[1][0]}/{sum(neg_tab[1])}={neg_tab[1][0]/sum(neg_tab[1]):.3f}; Fisher p={fe[1]:.4f}")
for g in ["news", "opinion"]:
    s_ = gx[gx.group == g].stance_num
    log(f"mean stance_num {g}: {s_.mean():.3f} (n={len(s_)})")
mw = stats.mannwhitneyu(gx[gx.group == "news"].stance_num, gx[gx.group == "opinion"].stance_num)
log(f"Mann-Whitney news vs opinion stance_num p={mw.pvalue:.4f}")

# ---------- 4. item-level model ----------
mdf = items[items.group.isin(["news", "opinion"])].copy()
mdf["statement_tone"] = mdf.event.map(tone_map)
mdf = mdf.dropna(subset=["statement_tone"])
mdf["cl"] = mdf.event
log(f"\nitem model sample: n={len(mdf)} items, clusters={mdf.event.nunique()} events; opinion items={int(mdf.is_opinion.sum())}")


def fit(df, label):
    f = "stance_num ~ statement_tone * is_opinion"
    m = smf.ols(f, data=df).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df.cl)[0]},
                                use_t=True)
    ci = m.conf_int().loc["statement_tone:is_opinion"]
    row = {"model": label, "n_items": len(df), "n_clusters": df.cl.nunique(),
           "b_tone": m.params["statement_tone"], "se_tone": m.bse["statement_tone"], "p_tone": m.pvalues["statement_tone"],
           "b_opinion": m.params["is_opinion"], "p_opinion": m.pvalues["is_opinion"],
           "b_interaction": m.params["statement_tone:is_opinion"], "se_interaction": m.bse["statement_tone:is_opinion"],
           "p_interaction_cluster": m.pvalues["statement_tone:is_opinion"],
           "ci_lo": ci[0], "ci_hi": ci[1], "r2": m.rsquared}
    return m, row


main_m, main_row = fit(mdf, "main: news+opinion, stance -1/0/+1 (mixed=0), final stance")
log("\nMAIN model summary:")
log(str(main_m.summary().tables[1]))
model_rows = [main_row]

# permutation over events: permute event-level statement_tone across the event clusters
obs = main_row["b_interaction"]
ev_tones = mdf.groupby("event").statement_tone.first()
perm_stats = []
events_list = ev_tones.index.tolist()
vals = ev_tones.values.copy()
for _ in range(N_PERM):
    p = RNG.permutation(vals)
    tm = dict(zip(events_list, p))
    x = mdf.event.map(tm).values
    X = np.column_stack([np.ones(len(mdf)), x, mdf.is_opinion.values, x * mdf.is_opinion.values])
    y = mdf.stance_num.values
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    perm_stats.append(b[3])
perm_stats = np.array(perm_stats)
perm_p = (np.sum(np.abs(perm_stats) >= abs(obs)) + 1) / (N_PERM + 1)
log(f"event-level permutation p (interaction, two-sided, {N_PERM} perms): {perm_p:.4f}")
model_rows[0]["p_interaction_perm_event"] = perm_p

# separate slopes for each group (within-group models)
for g in ["news", "opinion"]:
    sub = mdf[mdf.group == g]
    m_g = smf.ols("stance_num ~ statement_tone", data=sub).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sub.cl)[0]}, use_t=True)
    log(f"within-group slope {g}: n={len(sub)} clusters={sub.cl.nunique()} b={m_g.params['statement_tone']:.3f} "
        f"se={m_g.bse['statement_tone']:.3f} p={m_g.pvalues['statement_tone']:.3f}")

# sensitivity models
sens = []
_, r = fit(mdf, "A. news+opinion, final stance (base)"); sens.append(r)
d2 = mdf[mdf.stance_num.notna()].copy()
d2 = d2.dropna(subset=["stance_num_res"]).copy(); d2["stance_num"] = d2.stance_num_res
_, r = fit(d2, "B. first-pass researcher stance"); sens.append(r)
d3 = mdf[mdf.weak_evidence == False].copy()  # noqa: E712
_, r = fit(d3, "C. drop weak_evidence items"); sens.append(r)
d4 = mdf[mdf.stance != "mixed"].copy()
_, r = fit(d4, "D. drop mixed stance items"); sens.append(r)
d5 = items[items.group.isin(["news", "opinion", "other", "tweet"])].copy()
d5["statement_tone"] = d5.event.map(tone_map); d5 = d5.dropna(subset=["statement_tone"]); d5["cl"] = d5.event
d5["is_opinion"] = d5.is_opinion.astype(int)
_, r = fit(d5, "E. include polls+tweets as non-opinion (is_opinion=opinion only)"); sens.append(r)
for thr in (30, 50, 70):
    d6 = mdf.copy(); d6["statement_tone"] = d6.event.map(sens_tone[thr]); d6 = d6.dropna(subset=["statement_tone"])
    if d6.cl.nunique() >= 3:
        _, r = fit(d6, f"F{thr}. statement tone from passages with final_score_pct>={thr}"); sens.append(r)
    else:
        log(f"threshold {thr}: <3 clusters with >=3 passages; skipped")
# leave-one-event-out on the interaction
loo = []
for e_ in mdf.event.unique():
    d7 = mdf[mdf.event != e_]
    _, r = fit(d7, f"LOEO drop {e_}")
    loo.append((e_, r["b_interaction"], r["p_interaction_cluster"]))
sens_df = pd.DataFrame(sens + [dict(model=f"LOEO drop {e_}", n_items=np.nan, b_interaction=b, p_interaction_cluster=p) for e_, b, p in loo])
sens_df.to_csv(OUT / "model_sensitivity.csv", index=False)
log("\nSensitivity (interaction coefficient):")
log(sens_df[["model", "n_items", "n_clusters", "b_interaction", "se_interaction", "p_interaction_cluster"]].round(3).to_string(index=False))

pd.DataFrame(model_rows).to_csv(OUT / "model_main.csv", index=False)
corr_df.to_csv(OUT / "per_event_correlations.csv", index=False)
ev.round(4).to_csv(OUT / "per_event_indices.csv", index=False)
mdf[["event", "label", "item_type", "group", "outlet", "stance", "stance_num", "statement_tone", "political_lean"]].to_csv(
    OUT / "item_model_data.csv", index=False)

# ---------- 5. chart ----------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axes[0]
for col, lab, color, mk in [("news_index", "news_report", "#1f6f8b", "o"), ("opinion_index", "opinion/editorial/analysis", "#c0392b", "s")]:
    sub = ev[ev[col].notna()]
    ax.scatter(sub.statement_tone, sub[col], s=28 + 14 * (sub["n_news" if col == "news_index" else "n_opinion"]),
               color=color, marker=mk, alpha=0.75, label=lab, edgecolor="white", linewidth=0.6)
ax.axhline(0, color="#888", lw=0.8, ls=":")
ax.set_xlabel("statement tone (VADER mean of Afghan passages in 14-day window)")
ax.set_ylabel("stance index (pos - neg) / n")
ax.set_title("Per-event reaction index vs statement tone")
ax.legend(frameon=False, fontsize=8, loc="lower right")
ax2 = axes[1]
cnt = ev[["event", "n_news", "n_opinion"]].copy()
cnt["lbl"] = cnt.event.str[:7]
xx = np.arange(len(cnt))
ax2.bar(xx - 0.2, cnt.n_news, 0.4, color="#1f6f8b", label="news_report")
ax2.bar(xx + 0.2, cnt.n_opinion, 0.4, color="#c0392b", label="opinion-type")
ax2.set_xticks(xx); ax2.set_xticklabels(cnt.lbl, rotation=60, fontsize=7)
ax2.set_ylabel("items"); ax2.set_title("Items per event (n is small)")
ax2.legend(frameon=False, fontsize=8)
fig.suptitle("07 opinion vs news: n=%d items, %d events; not significant at event level" % (len(mdf), mdf.event.nunique()), fontsize=10)
fig.tight_layout()
fig.savefig(OUT / "chart.png", dpi=140)

# ---------- 6. write numbers ----------
(OUT / "numbers_log.txt").write_text("\n".join(lines) + "\n", encoding="utf8")
log("done")
