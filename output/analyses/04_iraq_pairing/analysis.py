"""Iraq-Afghanistan pairing analysis over output/references.csv (read-only input).
Run: .venv/bin/python -I output/analyses/04_iraq_pairing/analysis.py
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json, re, os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = str(PROJECT) + "/output/references.csv"
IDX = str(PROJECT) + "/output/speeches_index.csv"
OUT = str(ANALYSES) + "/04_iraq_pairing"
WITHDRAWAL = pd.Timestamp("2011-12-18")   # last US troops left Iraq (primary split)
ANNOUNCE = pd.Timestamp("2011-10-21")     # withdrawal announced (sensitivity split)

df = pd.read_csv(SRC, dtype={"speech_id": str})
for c in ["passage", "context_before", "context_after", "rationale", "category", "tone_label"]:
    df[c] = df[c].fillna("")
n_raw = len(df)

# --- exclusions -------------------------------------------------------------
# questioner passages are not the President's words; primary analysis excludes them
df["questioner"] = df.rationale.str.contains("questioner_not_president")
# speeches_index dup_of: check and drop duplicate speeches (none expected)
idx = pd.read_csv(IDX, dtype=str)
dups = set(idx.loc[idx.dup_of.notna() & (idx.dup_of.str.strip() != ""), "id"])
df["is_dup"] = df.speech_id.isin(dups)
df["date"] = pd.to_datetime(df.date)
df["year"] = df.date.dt.year
df["ym"] = df.date.dt.to_period("M")

# --- pairing definitions ----------------------------------------------------
win = (df.passage + " " + df.context_before + " " + df.context_after).str.lower()
df["win_iraq"] = win.str.contains(r"\biraq")
df["win_afg"] = win.str.contains(r"afghan")
df["paired_win"] = df.win_iraq & df.win_afg
pas = df.passage.str.lower()
df["paired_passage"] = pas.str.contains(r"\biraq") & pas.str.contains(r"afghan")
df["iraq_in_window"] = df.win_iraq
# framing cues inside the window
df["f_two_wars"] = win.str.contains(r"two wars|both wars|ending (?:the )?wars?|end (?:the )?wars?|wars? in iraq and afghanistan")
df["f_war_choice"] = win.str.contains(r"war of choice|war of necessity|dumb war|wrong war|bad war")
df["f_isil"] = win.str.contains(r"isil|isis|islamic state|daesh")
df["post"] = df.date >= WITHDRAWAL
df["post_ann"] = df.date >= ANNOUNCE

base = df[(~df.questioner) & (~df.is_dup)].copy()
print(f"raw rows={n_raw}; questioner={df.questioner.sum()}; dup-speech rows={df.is_dup.sum()}; analysis n={len(base)}")
print(f"speeches in analysis={base.speech_id.nunique()}")

def pct(x): return 100 * x.mean() if len(x) else np.nan

res = {"n_raw": n_raw, "n_questioner": int(df.questioner.sum()), "n_dup": int(df.is_dup.sum()),
       "n_analysis": int(len(base)), "n_speeches": int(base.speech_id.nunique())}

# --- overall pairing ----------------------------------------------------------
res["paired_win_n"] = int(base.paired_win.sum())
res["paired_win_pct"] = round(pct(base.paired_win), 2)
res["paired_passage_n"] = int(base.paired_passage.sum())
res["paired_passage_pct"] = round(pct(base.paired_passage), 2)
res["iraq_in_window_pct"] = round(pct(base.win_iraq), 2)

# --- by year table --------------------------------------------------------------
by_year = base.groupby("year").agg(n=("paired_win", "size"), paired=("paired_win", "sum"),
                                  paired_pct=("paired_win", lambda s: 100 * s.mean()),
                                  paired_passage_pct=("paired_passage", lambda s: 100 * s.mean()))
by_year.to_csv(f"{OUT}/pairing_by_year.csv")
print("\nBY YEAR\n", by_year.round(2).to_string())

by_ym = base.groupby("ym").agg(n=("paired_win", "size"), paired=("paired_win", "sum"))
by_ym["pct"] = 100 * by_ym.paired / by_ym.n
by_ym.to_csv(f"{OUT}/pairing_by_month.csv")

# --- Mann-Kendall (tau-b against time, plus classic S/Z with tie correction) -----
def mann_kendall(y):
    y = np.asarray(y, float); n = len(y); t = np.arange(n)
    S = 0.0
    for i in range(n - 1):
        S += np.sign(y[i + 1:] - y[i]).sum()
    _, counts = np.unique(y, return_counts=True)
    varS = (n * (n - 1) * (2 * n + 5) - np.sum(counts * (counts - 1) * (2 * counts + 5))) / 18.0
    z = (S - np.sign(S)) / np.sqrt(varS) if S != 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return S, z, p

my = by_year.paired_pct.values
S, z, p = mann_kendall(my)
res["mk_yearly_S"], res["mk_yearly_z"], res["mk_yearly_p"] = float(S), round(float(z), 3), round(float(p), 4)
tau, pt = stats.kendalltau(np.arange(len(my)), my)
res["kendall_yearly_tau"], res["kendall_yearly_p"] = round(float(tau), 3), round(float(pt), 4)

# monthly MK on months with >=1 passage (weights ignored; series is the monthly share)
mm = by_ym[by_ym.n >= 1].pct.values
Sm, zm, pm = mann_kendall(mm)
res["mk_monthly_n_months"] = int(len(mm)); res["mk_monthly_z"] = round(float(zm), 3); res["mk_monthly_p"] = round(float(pm), 4)

# --- period comparison ---------------------------------------------------------------
pre = base[~base.post]; post = base[base.post]
ct = pd.crosstab(base.post, base.paired_win)
chi2, pchi, _, _ = stats.chi2_contingency(ct)
res["pre_n"], res["post_n"] = int(len(pre)), int(len(post))
res["pre_paired_pct"], res["post_paired_pct"] = round(pct(pre.paired_win), 2), round(pct(post.paired_win), 2)
res["period_chi2"], res["period_chi2_p"] = round(float(chi2), 2), float(pchi)
res["period_fisher_p"] = float(stats.fisher_exact(ct.values)[1])
# sensitivity: announcement split
ct2 = pd.crosstab(base.post_ann, base.paired_win)
res["ann_split_pre_pct"] = round(pct(base[~base.post_ann].paired_win), 2)
res["ann_split_post_pct"] = round(pct(base[base.post_ann].paired_win), 2)
res["ann_split_chi2_p"] = float(stats.chi2_contingency(ct2)[1])

# 2009-2011 vs 2012-2016 yearly-share Mann-Whitney on monthly values
pre_m = by_ym[by_ym.index < pd.Period("2012-01", "M")].pct
post_m = by_ym[by_ym.index >= pd.Period("2012-01", "M")].pct
res["monthly_mwu_p"] = float(stats.mannwhitneyu(pre_m, post_m).pvalue)

# --- logistic: paired ~ time (years) + post, speech-clustered SEs -------------------
X = pd.DataFrame({"const": 1.0,
                  "t_years": (base.date - pd.Timestamp("2009-01-20")).dt.days / 365.25,
                  "post": base.post.astype(float)})
m1 = sm.Logit(base.paired_win.astype(float), X).fit(disp=0, cov_type="cluster",
                                                    cov_kwds={"groups": pd.factorize(base.speech_id)[0]})
m0 = sm.Logit(base.paired_win.astype(float), X[["const", "t_years"]]).fit(disp=0, cov_type="cluster",
                                                    cov_kwds={"groups": pd.factorize(base.speech_id)[0]})
res["logit_time_OR"] = round(float(np.exp(m0.params["t_years"])), 3)
res["logit_time_p"] = round(float(m0.pvalues["t_years"]), 4)
res["logit_post_OR"] = round(float(np.exp(m1.params["post"])), 3)
res["logit_post_CI"] = [round(float(np.exp(v)), 3) for v in m1.conf_int().loc["post"]]
res["logit_post_p"] = round(float(m1.pvalues["post"]), 4)
res["logit_time_adj_OR"] = round(float(np.exp(m1.params["t_years"])), 3)
res["logit_time_adj_p"] = round(float(m1.pvalues["t_years"]), 4)

# --- sensitivity: high-likelihood thresholds (30/50/70) -----------------------------
sens = {}
for thr in [30, 50, 70]:
    s = base[base.final_score_pct >= thr]
    if len(s) < 20: continue
    c = pd.crosstab(s.post, s.paired_win)
    sens[f"thr{thr}"] = {"n": int(len(s)), "pre_pct": round(pct(s[~s.post].paired_win), 2),
                         "post_pct": round(pct(s[s.post].paired_win), 2),
                         "chi2_p": float(stats.chi2_contingency(c)[1])}
res["threshold_sensitivity"] = sens

# --- tone: paired vs unpaired (VADER passage tone) ------------------------------------
pa = base[base.paired_win]; un = base[~base.paired_win]
u = stats.mannwhitneyu(pa.tone, un.tone)
res["tone_paired_mean"], res["tone_paired_median"] = round(pa.tone.mean(), 3), round(pa.tone.median(), 3)
res["tone_unpaired_mean"], res["tone_unpaired_median"] = round(un.tone.mean(), 3), round(un.tone.median(), 3)
res["tone_mwu_p"] = float(u.pvalue)
res["tone_paired_n"], res["tone_unpaired_n"] = len(pa), len(un)
# within post-period only
pa_p = base[base.paired_win & base.post]; un_p = base[(~base.paired_win) & base.post]
res["tone_post_paired_mean"] = round(pa_p.tone.mean(), 3); res["tone_post_unpaired_mean"] = round(un_p.tone.mean(), 3)
res["tone_post_mwu_p"] = float(stats.mannwhitneyu(pa_p.tone, un_p.tone).pvalue) if len(pa_p) > 2 else None
res["tone_post_paired_n"] = len(pa_p)
# tone label distribution
tl = pd.crosstab(base.paired_win, base.tone_label, normalize="index") * 100
res["tone_label_pct"] = {str(k): {c: round(float(v), 1) for c, v in row.items()} for k, row in tl.iterrows()}
res["tone_label_chi2_p"] = float(stats.chi2_contingency(pd.crosstab(base.paired_win, base.tone_label))[1])

# --- category: paired vs unpaired -----------------------------------------------------
cat = pd.crosstab(base.paired_win, base.category)
catp = cat.div(cat.sum(axis=1), axis=0) * 100
res["category_pct"] = {str(k): {c: round(float(v), 1) for c, v in row.items()} for k, row in catp.iterrows()}
res["category_chi2_p"] = float(stats.chi2_contingency(cat)[1])
res["category_n_paired"] = cat.loc[True].to_dict() if True in cat.index else {}
# score comparison
res["score_paired_mean"] = round(pa.final_score_pct.mean(), 2)
res["score_unpaired_mean"] = round(un.final_score_pct.mean(), 2)
res["score_mwu_p"] = float(stats.mannwhitneyu(pa.final_score_pct, un.final_score_pct).pvalue)

# --- framing cues -----------------------------------------------------------------------
fr = {}
for f in ["f_two_wars", "f_war_choice", "f_isil"]:
    sub = base[base.paired_win]
    fr[f] = {"paired_n": int(sub[f].sum()), "paired_pct": round(pct(sub[f]), 2),
             "unpaired_n": int(base[(~base.paired_win)][f].sum()),
             "unpaired_pct": round(pct(base[~base.paired_win][f]), 2)}
    if f == "f_isil":
        fr[f]["paired_pre_pct"] = round(pct(sub[~sub.post][f]), 2)
        fr[f]["paired_post_pct"] = round(pct(sub[sub.post][f]), 2)
res["framing_cues"] = fr
ex_two = base[base.paired_win & base.f_two_wars][["date", "speech_title", "passage"]].head(5)
ex_choice = base[base.f_war_choice][["date", "speech_title", "passage"]].head(5)
ex_two.to_csv(f"{OUT}/examples_two_wars.csv", index=False)
ex_choice.to_csv(f"{OUT}/examples_war_choice.csv", index=False)
# paired passage-level examples for transparency
base[base.paired_win].sample(min(25, int(base.paired_win.sum())), random_state=1)[
    ["date", "speech_title", "category", "passage"]].to_csv(f"{OUT}/paired_sample.csv", index=False)

# --- chart ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=150)
yrs = by_year.index.values
ax.bar(yrs, by_year.paired_pct, color="#7a8fa6", width=0.6, label="% of passages paired (Iraq and Afghan in window)")
ax.set_ylabel("% of Afghan passages with Iraq in window")
ax.set_xlabel("Year")
ax.axvline(2011 + 11.6 / 12, color="#b5543a", ls="--", lw=1.2)
ax.text(2011 + 11.8 / 12, ax.get_ylim()[1] * 0.92, "Iraq withdrawal\n(Dec 2011)", color="#b5543a", fontsize=8, va="top")
for x, y, nn in zip(yrs, by_year.paired_pct, by_year.n):
    ax.text(x, y + 0.4, f"n={nn}", ha="center", fontsize=7, color="#333")
ax.set_title("Iraq-Afghanistan pairing in Obama presidency passages (non-questioner, n=%d)" % len(base), fontsize=10)
ax.legend(fontsize=8, loc="upper right", frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/pairing_by_year.png")

with open(f"{OUT}/results.json", "w") as f:
    json.dump(res, f, indent=2, default=str)
print(json.dumps(res, indent=2, default=str))

# ===== second pass: campaign confound, tight framing regex =====================
camp_pat = r"Campaign|Fundraiser|Debate|Victory Fund|Reelection|Re-election|Democratic National|Convention"
base["campaign_title"] = base.speech_title.str.contains(camp_pat, case=False)
add = {}
add["campaign_title_n"] = int(base.campaign_title.sum())
add["campaign_title_speeches"] = int(base[base.campaign_title].speech_id.nunique())
# paired share among campaign-titled vs other, by period
for lab, sub in [("campaign", base[base.campaign_title]), ("noncampaign", base[~base.campaign_title])]:
    add[f"{lab}_paired_pct"] = round(pct(sub.paired_win), 2)
    add[f"{lab}_n"] = int(len(sub))
# period test excluding campaign titles
nc = base[~base.campaign_title]
c_nc = pd.crosstab(nc.post, nc.paired_win)
add["noncampaign_pre_pct"] = round(pct(nc[~nc.post].paired_win), 2)
add["noncampaign_post_pct"] = round(pct(nc[nc.post].paired_win), 2)
add["noncampaign_chi2_p"] = float(stats.chi2_contingency(c_nc)[1])
# period test excluding calendar 2012 (election year)
no12 = base[base.year != 2012]
c12 = pd.crosstab(no12.post, no12.paired_win)
add["excl2012_pre_pct"] = round(pct(no12[~no12.post].paired_win), 2)
add["excl2012_post_pct"] = round(pct(no12[no12.post].paired_win), 2)
add["excl2012_chi2_p"] = float(stats.chi2_contingency(c12)[1])
# 2012 monthly, to see if spike is campaign-timed
y12 = base[base.year == 2012].groupby(base.date.dt.month).paired_win.agg(["size", "mean"])
add["y2012_monthly_pct"] = {int(k): round(100 * v, 1) for k, v in y12["mean"].items()}
add["y2012_monthly_n"] = {int(k): int(v) for k, v in y12["size"].items()}
# tight framing regex (explicit 'two wars' phrasing) by period
tight = base.passage.str.lower().str.cat(base.context_before.str.lower() + " " + base.context_after.str.lower(), sep=" ")
tight_m = tight.str.contains(r"(?:end|ending|ended|close|closing)\s+(?:the\s+|both\s+|these\s+|our\s+)?(?:two|both)\s+wars|two wars|both wars")
base["f_two_wars_tight"] = tight_m
for lab, sub in [("pre", base[(~base.post) & base.paired_win]), ("post", base[base.post & base.paired_win])]:
    add[f"two_wars_tight_{lab}_paired_n"] = int(sub.f_two_wars_tight.sum())
    add[f"two_wars_tight_{lab}_paired_pct"] = round(pct(sub.f_two_wars_tight), 2)
add["two_wars_tight_paired_n"] = int((base.paired_win & base.f_two_wars_tight).sum())
add["two_wars_tight_unpaired_n"] = int((~base.paired_win & base.f_two_wars_tight).sum())
# tone: paired vs unpaired within category war_direct (controls for category mix)
wd = base[base.category == "war_direct"]
add["tone_wardirect_paired_mean"] = round(wd[wd.paired_win].tone.mean(), 3)
add["tone_wardirect_unpaired_mean"] = round(wd[~wd.paired_win].tone.mean(), 3)
add["tone_wardirect_mwu_p"] = float(stats.mannwhitneyu(wd[wd.paired_win].tone, wd[~wd.paired_win].tone).pvalue)
add["tone_wardirect_paired_n"] = int(wd.paired_win.sum())
# logistic with campaign + post + time, speech-clustered
X2 = pd.DataFrame({"const": 1.0, "post": base.post.astype(float),
                   "campaign": base.campaign_title.astype(float),
                   "t_years": (base.date - pd.Timestamp("2009-01-20")).dt.days / 365.25})
g = pd.factorize(base.speech_id)[0]
m2 = sm.Logit(base.paired_win.astype(float), X2).fit(disp=0, cov_type="cluster", cov_kwds={"groups": g})
add["logit_full_post_OR"] = round(float(np.exp(m2.params["post"])), 3)
add["logit_full_post_p"] = round(float(m2.pvalues["post"]), 4)
add["logit_full_campaign_OR"] = round(float(np.exp(m2.params["campaign"])), 3)
add["logit_full_campaign_p"] = round(float(m2.pvalues["campaign"]), 4)
add["logit_full_time_OR"] = round(float(np.exp(m2.params["t_years"])), 3)
add["logit_full_time_p"] = round(float(m2.pvalues["t_years"]), 4)
res["second_pass"] = add
with open(f"{OUT}/results.json", "w") as f:
    json.dump(res, f, indent=2, default=str)
print(json.dumps(add, indent=2, default=str))
