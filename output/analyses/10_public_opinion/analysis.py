"""10_public_opinion: Gallup/Pew Afghanistan opinion vs Obama passage volume/tone/frame (30-day windows).
Run: .venv/bin/python -I output/analyses/10_public_opinion/analysis.py
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json, os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = str(PROJECT) + ""
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
WIN = pd.Timedelta(days=30)
RNG = np.random.default_rng(0)
NPERM = 10000

# ---------- passages ----------
refs = pd.read_csv(os.path.join(BASE, "output/references.csv"))
idx = pd.read_csv(os.path.join(BASE, "output/speeches_index.csv"))
refs["date"] = pd.to_datetime(refs["date"])
idx["date"] = pd.to_datetime(idx["date"])
dup_ids = set(idx.loc[idx["dup_of"].notna(), "id"])
refs = refs[~refs["speech_id"].isin(dup_ids)]
questioner = refs["rationale"].fillna("").str.contains("questioner_not_president")
refs = refs[~questioner].copy()          # drop questioner passages (President's words only)
speeches = idx[~idx["id"].isin(dup_ids)].copy()
print(f"passages after dup+questioner filter: {len(refs)} (dropped questioner={int(questioner.sum())}, dup-speech refs removed)")
print(f"non-dup speeches in index: {len(speeches)}")

# ---------- polls ----------
mis = pd.read_csv(os.path.join(DATA, "gallup_mistake.csv"), parse_dates=["fieldwork_start", "fieldwork_end"])
app = pd.read_csv(os.path.join(DATA, "gallup_approval_obama_afghanistan.csv"), parse_dates=["fieldwork_start", "fieldwork_end"])
pew = pd.read_csv(os.path.join(DATA, "pew_right_decision.csv"), parse_dates=["fieldwork_start", "fieldwork_end"])

def mid(a, b):
    return a + (b - a) / 2

mis["t"] = [mid(a, b) for a, b in zip(mis.fieldwork_start, mis.fieldwork_end)]
app["t"] = [mid(a, b) for a, b in zip(app.fieldwork_start, app.fieldwork_end)]
pew["t"] = [mid(a, b) for a, b in zip(pew.fieldwork_start, pew.fieldwork_end)]

PRES_START = pd.Timestamp("2009-01-20")
PRES_END = pd.Timestamp("2017-01-20")

def covered(t):
    # full 30-day pre window must be inside presidency
    return (t - WIN) >= PRES_START and t <= PRES_END

def window_stats(t, start, end, thr):
    m = refs[(refs.date >= start) & (refs.date < end)]
    hi = m[m.final_score_pct >= thr]
    nsp = int(((speeches.date >= start) & (speeches.date < end)).sum())
    cats = hi.category.value_counts()
    n = len(hi)
    return dict(
        n_hi=n,
        n_hi_speeches=int(hi.speech_id.nunique()),
        n_speeches=nsp,
        hi_per_100_speeches=(100 * n / nsp) if nsp else np.nan,
        tone_mean=hi.tone.mean() if n else np.nan,
        tone_median=hi.tone.median() if n else np.nan,
        share_war_direct=(cats.get("war_direct", 0) / n) if n else np.nan,
        share_war_adjacent=(cats.get("war_adjacent", 0) / n) if n else np.nan,
        share_aid_civil=(cats.get("aid_diplomacy_civil", 0) / n) if n else np.nan,
    )

def build(polls, thr, label):
    rows = []
    for _, p in polls.iterrows():
        t = p.t.normalize()
        if not covered(t):
            continue
        pre = window_stats(t, t - WIN, t, thr)
        post = window_stats(t, t, t + WIN, thr)
        rows.append(dict(series=label, t=t.date(), value=p.get("pct_mistake", p.get("pct_approve", p.get("pct_right_decision")))),)
        for k, v in pre.items():
            rows[-1]["pre_" + k] = v
        for k, v in post.items():
            rows[-1]["post_" + k] = v
    return pd.DataFrame(rows)

def fmt(df):
    return df.round(3).to_string(index=False)

METRICS = ["n_hi", "hi_per_100_speeches", "tone_mean", "share_war_direct", "share_war_adjacent", "share_aid_civil"]

def corr_table(df, ycol, xprefix, label):
    out = []
    for m in METRICS:
        x = df[f"{xprefix}_{m}"]
        ok = x.notna() & df[ycol].notna()
        n = int(ok.sum())
        if n < 4:
            out.append(dict(test=label, metric=m, n=n, rho=np.nan, p_exact=np.nan, p_perm=np.nan)); continue
        rho, p = stats.spearmanr(df[ycol][ok], x[ok])
        y = df[ycol][ok].values; xx = x[ok].values
        ry = stats.rankdata(y); rx = stats.rankdata(xx)
        ryc = ry - ry.mean(); rxc = rx - rx.mean()
        den = np.sqrt((ryc**2).sum() * (rxc**2).sum())
        perms = np.array([RNG.permutation(ryc) for _ in range(NPERM)])
        rhos = (perms @ rxc) / den
        cnt = int((np.abs(rhos) >= abs(rho) - 1e-12).sum())
        out.append(dict(test=label, metric=m, n=n, rho=round(rho, 3), p_exact=round(p, 4), p_perm=round((cnt + 1) / (NPERM + 1), 4)))
    return pd.DataFrame(out)

# ---------- main run ----------
results = {}
for thr in (30, 50, 70):
    print(f"\n===== threshold {thr} (high-likelihood = final_score_pct >= {thr}) =====")
    mdf = build(mis, thr, "mistake")
    mdf = mdf.sort_values("t").reset_index(drop=True)
    # precompute opinion drop and rhetoric response (post minus pre) for the lag test
    mdf["opinion_drop"] = -(mdf["value"].diff())  # positive = opinion fell since previous poll (fieldwork order)
    for m in METRICS:
        mdf[f"resp_{m}"] = mdf[f"post_{m}"] - mdf[f"pre_{m}"]
    print(fmt(mdf[["t", "value", "pre_n_hi", "pre_hi_per_100_speeches", "pre_tone_mean", "post_n_hi", "post_hi_per_100_speeches", "post_tone_mean"]]))
    mdf.to_csv(os.path.join(OUT, f"mistake_windows_thr{thr}.csv"), index=False)

    # (a) contemporaneous: opinion at t vs preceding window
    ca = corr_table(mdf, "value", "pre", "A: opinion_t vs pre-window (contemporaneous)")
    # (b) lead: opinion at t vs following window (does rhetoric after poll track opinion)
    cb = corr_table(mdf, "value", "post", "B: opinion_t vs post-window (rhetoric t..t+30)")
    # (c) follow: opinion drop at t vs response (post - pre) -- drop needs previous poll; n = polls with prior poll
    dd = mdf.dropna(subset=["opinion_drop"]).copy()
    cc = corr_table(dd, "opinion_drop", "resp", "C: opinion drop (since prev poll) vs rhetoric change (post-pre)")
    res = pd.concat([ca, cb, cc], ignore_index=True)
    print(res.to_string(index=False))
    res.to_csv(os.path.join(OUT, f"correlations_thr{thr}.csv"), index=False)
    results[thr] = dict(mistake=mdf, corr=res)

# approval (Obama handling Afghanistan, Gallup) and Pew right decision: descriptive, small n
adf = build(app.rename(columns={"pct_approve": "pct_approve"}), 50, "approval").sort_values("t")
print("\nApproval-linked windows (thr 50):")
print(fmt(adf[["t", "value", "pre_n_hi", "pre_hi_per_100_speeches", "pre_tone_mean", "post_n_hi", "post_tone_mean"]]))
adf.to_csv(os.path.join(OUT, "approval_windows_thr50.csv"), index=False)
ca2 = corr_table(adf, "value", "pre", "approval: value vs pre-window")
cb2 = corr_table(adf, "value", "post", "approval: value vs post-window")
print(pd.concat([ca2, cb2]).to_string(index=False))
pdf_ = build(pew.assign(pct_right_decision=pew.pct_right_decision), 50, "pew_right").sort_values("t")
print("\nPew right-decision windows (thr 50):")
print(fmt(pdf_[["t", "value", "pre_n_hi", "pre_tone_mean"]]) if len(pdf_) else "no covered Pew points")

# ---------- chart ----------
m50 = results[50]["mistake"]
fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
ax[0].scatter(mis.t, mis.pct_mistake, color="#b03a2e", label="Gallup 'mistake' %")
ax[0].plot(mis.t, mis.pct_mistake, color="#b03a2e", alpha=0.3)
ax[0].scatter(app.t, app.pct_approve, color="#1f618d", marker="s", label="Gallup Obama approval, Afghanistan %")
ax[0].set_ylabel("percent")
ax[0].set_title("Afghanistan opinion (Gallup) vs Obama passage volume (30-day windows before each poll)")
ax[0].legend(fontsize=8, loc="lower left")
ax[0].axvspan(PRES_START, PRES_START, alpha=0)
ax[1].bar(m50.t, m50.pre_n_hi, width=20, color="#7d6608", alpha=0.6, label="high-likelihood passages, 30 days before poll (thr 50, questioner excl.)")
ax[1].set_ylabel("passages (n)")
ax[1].legend(fontsize=8, loc="upper right")
ax[1].set_xlabel("poll fieldwork midpoint")
fig.text(0.01, 0.005, "Sources: Gallup July 2021 topline (Q25 trend); Gallup 2010 articles. VADER tone not shown. n small (11 mistake polls in window).", fontsize=7)
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(os.path.join(OUT, "chart_opinion_vs_volume.png"), dpi=130)
print("saved chart")
