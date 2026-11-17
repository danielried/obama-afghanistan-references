"""02_election: is 2012 (esp. Jan-Nov 6 2012) framed more around withdrawal than other years?
Read-only on the project root. Outputs go to this folder.
Run: .venv/bin/python -I output/analyses/02_election/analysis.py
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json, re, sys, warnings
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
OUT = Path(str(ANALYSES) + "/02_election")
REF = str(PROJECT) + "/output/references.csv"
IDX = str(PROJECT) + "/output/speeches_index.csv"
RES = {}  # everything reported goes here -> results.json

# ---------- 1. load ----------
ref = pd.read_csv(REF, dtype={"ref_id": str})
idx = pd.read_csv(IDX)
idx = idx[idx["dup_of"].isna() | (idx["dup_of"].astype(str).str.strip() == "")].copy()
idx["date"] = pd.to_datetime(idx["date"], errors="coerce")
idx = idx.dropna(subset=["date"])
idx["ym"] = idx["date"].dt.to_period("M")
idx["yr"] = idx["date"].dt.year
RES["n_speeches_nondup"] = int(len(idx))
RES["speeches_by_year"] = idx["yr"].value_counts().sort_index().to_dict()

ref["date"] = pd.to_datetime(ref["date"], errors="coerce")
ref["yr"] = ref["date"].dt.year
ref["ym"] = ref["date"].dt.to_period("M")
ref["questioner"] = ref["rationale"].fillna("").str.contains("questioner_not_president")
ref["passage"] = ref["passage"].fillna("")

# ---------- 2. period definitions ----------
def period(d):
    if pd.isna(d):
        return "na"
    y = d.year
    if y == 2012 and pd.Timestamp("2012-01-01") <= d <= pd.Timestamp("2012-11-06"):
        return "campaign_2012"
    if y == 2010 and pd.Timestamp("2010-01-01") <= d <= pd.Timestamp("2010-11-02"):
        return "midterm_2010"
    if y == 2014 and pd.Timestamp("2014-01-01") <= d <= pd.Timestamp("2014-11-04"):
        return "midterm_2014"
    return "non_election"

ref["period"] = ref["date"].apply(period)
idx["period"] = idx["date"].apply(period)

# ---------- 3. frame coding (lexical, on the President's passage text) ----------
WITHDRAW = re.compile(
    r"\b(end(?:ing)? (?:the|this|our) war|end (?:our|the) (?:combat|military)|coming home|come home|"
    r"bring(?:ing)? (?:our |the |them |troops |our troops |them home)*home|troops home|"
    r"draw(?:ing)? down|drawdown|responsibl\w* (?:end|leave|transition|withdraw)\w*|withdraw\w*|"
    r"transition\w*|hand(?:ing)? over|leave Afghanistan|combat mission ends?|bring the war to a close)\b",
    re.I)
ESCAL = re.compile(
    r"\b(surge|combat|fight\w*|counterinsurg\w*|insurgen\w*|Taliban|offensive|defeat\w*|attack\w*|"
    r"terror\w*|al[- ]?Qaeda|dismantl\w*|kill\w*|casualt\w*|train\w*|strateg\w*|enemy|disrupt\w*)\b", re.I)
# troops/forces are ambiguous (both frames); kept out of both to keep frames clean
ref["withdraw_frame"] = ref["passage"].str.contains(WITHDRAW)
ref["escal_frame"] = ref["passage"].str.contains(ESCAL)
ref["frame"] = np.select(
    [ref.withdraw_frame & ~ref.escal_frame, ref.escal_frame & ~ref.withdraw_frame, ref.withdraw_frame & ref.escal_frame],
    ["withdraw_only", "escal_only", "both"], default="neither")

# withdraw-specific words that the user named explicitly (for a narrow check)
NAMED = re.compile(r"\b(end the war|coming home|drawdown|responsibly end|transition)\b", re.I)
ref["named_frame"] = ref["passage"].str.contains(NAMED)

# ---------- 4. near-duplicate detection among the passage pool ----------
def toks(s):
    return re.findall(r"[a-z0-9']+", s.lower())

def shingles(s, k=8):
    t = toks(s)
    return {" ".join(t[i:i + k]) for i in range(max(0, len(t) - k + 1))}

pool = ref.reset_index(drop=True)
sh = [shingles(p) for p in pool["passage"]]
inv = defaultdict(list)
for i, S in enumerate(sh):
    for g in S:
        inv[g].append(i)
CAP = 150  # ignore boilerplate shingles appearing in more than CAP passages
parent = list(range(len(pool)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
pairs_checked = 0
for g, lst in inv.items():
    if len(lst) < 2 or len(lst) > CAP:
        continue
    for a in range(len(lst)):
        for b in range(a + 1, len(lst)):
            i, j = lst[a], lst[b]
            if find(i) == find(j):
                continue
            pairs_checked += 1
            J = len(sh[i] & sh[j]) / max(1, len(sh[i] | sh[j]))
            if J >= 0.5:
                parent[find(i)] = find(j)
pool["cluster"] = [find(i) for i in range(len(pool))]
cl_size = pool["cluster"].map(pool["cluster"].value_counts())
pool["near_dup_n"] = cl_size
pool["is_repeat"] = cl_size > 1
RES["near_dup_pairs_checked"] = int(pairs_checked)

# ---------- 5. high-likelihood subsets ----------
def hl(th):
    return pool[pool.final_score_pct >= th]

H = hl(50)
RES["n_passages_total"] = int(len(pool))
RES["n_hi50"] = int(len(H))
RES["n_hi50_nonquestioner"] = int((~H.questioner).sum())
RES["hi50_by_year"] = H.groupby("yr").size().to_dict()
RES["hi50_by_year_nonq"] = H[~H.questioner].groupby("yr").size().to_dict()
RES["hi50_by_year_speeches_with_hit"] = H.groupby("yr")["speech_id"].nunique().to_dict()
RES["questioner_by_year_hi50"] = H[H.questioner].groupby("yr").size().to_dict()

# speech-volume normalization: high-likelihood passages per non-dup speech in the year
spv = idx.groupby("yr").size()
hv = H.groupby("yr").size()
rate_year = (hv / spv.reindex(hv.index)).round(3)
RES["hi50_per_speech_by_year"] = rate_year.to_dict()
RES["speeches_per_month_mean_by_year"] = (idx.groupby(["yr", "ym"]).size().groupby("yr").mean().round(2)).to_dict()

# passage-level: distinct text, repeats, near-dups per year
rep = H.groupby("yr").agg(n=("ref_id", "size"), repeat_share=("is_repeat", "mean"),
                           distinct_clusters=("cluster", "nunique"))
RES["hi50_repeat_share_by_year"] = rep["repeat_share"].round(3).to_dict()
RES["hi50_distinct_clusters_by_year"] = rep["distinct_clusters"].to_dict()

# campaign window vs other
per = H.groupby("period").agg(n=("ref_id", "size"), repeat_share=("is_repeat", "mean"),
                               distinct=("cluster", "nunique"))
RES["hi50_by_period"] = per.round(3).to_dict(orient="index")

# speeches concentration in 2012 (is spike a few speeches?)
s12 = H[H.yr == 2012].groupby(["speech_id", "speech_title", "date"]).size().sort_values(ascending=False)
RES["top_speeches_2012"] = [{"title": a[1], "date": str(a[2])[:10], "n_hi": int(v)} for a, v in s12.head(10).items()]
RES["share_top5_speeches_2012"] = round(float(s12.head(5).sum() / s12.sum()), 3)
RES["n_speeches_with_hi_2012"] = int(len(s12))
s09 = H[H.yr == 2009].groupby("speech_id").size().sort_values(ascending=False)
RES["share_top5_speeches_2009"] = round(float(s09.head(5).sum() / s09.sum()), 3)
RES["n_speeches_with_hi_2009"] = int(len(s09))

# speech type mix by period (volume confound)
RES["speech_type_mix_by_period"] = pd.crosstab(idx["period"], idx["type"], normalize="index").round(3).to_dict(orient="index")

# ---------- 6. frame shares per year and period ----------
def frame_table(df, by):
    t = df.groupby(by).agg(n=("ref_id", "size"),
                           withdraw=("withdraw_frame", "mean"),
                           escal=("escal_frame", "mean"),
                           named=("named_frame", "mean"))
    t["withdraw_minus_escal"] = t["withdraw"] - t["escal"]
    return t.round(3)

HN = H[~H.questioner]
RES["frame_by_year_hi50_nonq"] = frame_table(HN, "yr").to_dict(orient="index")
RES["frame_by_period_hi50_nonq"] = frame_table(HN, "period").to_dict(orient="index")

# dedup-by-cluster version (one passage per near-dup cluster)
HU = HN.drop_duplicates("cluster")
RES["n_unique_clusters_hi50_nonq"] = int(len(HU))
RES["frame_by_year_unique"] = frame_table(HU, "yr").to_dict(orient="index")
RES["frame_by_period_unique"] = frame_table(HU, "period").to_dict(orient="index")

# ---------- 7. chi-square tests ----------
def chi(df, col_a, col_b):
    ct = pd.crosstab(df[col_a], df[col_b])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    return {"chi2": round(float(chi2), 2), "dof": int(dof), "p": float(p), "n": int(ct.values.sum())}

tests = {}
HN2 = HN.copy()
HN2["withdraw_lbl"] = HN2["withdraw_frame"].map({True: "W", False: "notW"})
HN2["escal_lbl"] = HN2["escal_frame"].map({True: "E", False: "notE"})
HN2["any_frame"] = HN2["frame"]
# restrict to frame-bearing passages for the withdraw-vs-escalation balance
FB = HN2[HN2.withdraw_frame | HN2.escal_frame].copy()
FB["wd_side"] = np.where(FB.withdraw_frame & ~FB.escal_frame, "W_only",
                 np.where(FB.escal_frame & ~FB.withdraw_frame, "E_only", "both"))
tests["withdraw_frame x year (all hi50 nonq)"] = chi(HN2, "yr", "withdraw_lbl")
tests["escal_frame x year (all hi50 nonq)"] = chi(HN2, "yr", "escal_lbl")
tests["withdraw_frame x period (all hi50 nonq)"] = chi(HN2, "period", "withdraw_lbl")
tests["withdraw_frame x year (unique clusters)"] = chi(HU.assign(withdraw_lbl=HU.withdraw_frame.map({True: "W", False: "notW"})), "yr", "withdraw_lbl")
tests["withdraw_frame x period (unique clusters)"] = chi(HU.assign(withdraw_lbl=HU.withdraw_frame.map({True: "W", False: "notW"})), "period", "withdraw_lbl")
# 2012 vs other years on withdrawal share (2x2)
def two_by_two(a, b):
    ct = pd.DataFrame({"yes": [a.sum(), b.sum()], "no": [len(a) - a.sum(), len(b) - b.sum()]}, index=["A", "B"])
    chi2, p, _, _ = stats.chi2_contingency(ct.values, correction=False)
    OR, pf = stats.fisher_exact(ct.values)
    return {"A_yes": int(a.sum()), "A_n": int(len(a)), "B_yes": int(b.sum()), "B_n": int(len(b)),
            "chi2": round(float(chi2), 2), "p_chi2": float(p), "p_fisher": float(pf), "OR_A_vs_B": round(float(OR), 3)}
y12 = HN2[HN2.yr == 2012]
oth = HN2[HN2.yr != 2012]
tests["2012 vs other years: withdraw share"] = two_by_two(y12.withdraw_frame, oth.withdraw_frame)
tests["2012 vs other years: escal share"] = two_by_two(y12.escal_frame, oth.escal_frame)
tests["2012 campaign vs non-election: withdraw"] = two_by_two(HN2[HN2.period == "campaign_2012"].withdraw_frame,
                                                              HN2[HN2.period == "non_election"].withdraw_frame)
tests["2012 campaign vs 2010+2014 midterm windows: withdraw"] = two_by_two(
    HN2[HN2.period == "campaign_2012"].withdraw_frame,
    HN2[HN2.period.isin(["midterm_2010", "midterm_2014"])].withdraw_frame)
tests["2012 campaign vs 2010+2014 midterm windows: escal"] = two_by_two(
    HN2[HN2.period == "campaign_2012"].escal_frame,
    HN2[HN2.period.isin(["midterm_2010", "midterm_2014"])].escal_frame)
tests["2012 campaign vs midterm windows: withdraw(unique clusters)"] = two_by_two(
    HU[HU.period == "campaign_2012"].withdraw_frame,
    HU[HU.period.isin(["midterm_2010", "midterm_2014"])].withdraw_frame)
tests["2012 campaign vs midterm windows: escal(unique clusters)"] = two_by_two(
    HU[HU.period == "campaign_2012"].escal_frame,
    HU[HU.period.isin(["midterm_2010", "midterm_2014"])].escal_frame)
tests["2012 campaign vs non-election: escal"] = two_by_two(HN2[HN2.period == "campaign_2012"].escal_frame,
                                                           HN2[HN2.period == "non_election"].escal_frame)
RES["tests"] = tests

# ---------- 8. logistic regression (passage level) ----------
# outcome: withdraw_frame; predictors: period (ref non_election), year FE, speech type
lr_df = HN2.copy()
lr_df["W"] = lr_df.withdraw_frame.astype(int)
lr_df["E"] = lr_df.escal_frame.astype(int)
lr_df["camp12"] = (lr_df.period == "campaign_2012").astype(int)
lr_df["mid"] = lr_df.period.isin(["midterm_2010", "midterm_2014"]).astype(int)
lr_df["yr_c"] = lr_df.yr.astype(str)
lr_df["type"] = lr_df.speech_id.map(idx.set_index("id")["type"]) if False else \
    lr_df.speech_id.str.replace("govinfo:", "", regex=False).map(
        idx.assign(sid=idx.id.str.replace("govinfo:", "", regex=False)).set_index("sid")["type"])
lr_df["type"] = lr_df["type"].fillna("other")
lr_df["repeat"] = lr_df.is_repeat.astype(int)

fits = {}
f1 = smf.logit("W ~ camp12 + mid", data=lr_df).fit(disp=0)
f2 = smf.logit("W ~ camp12 + mid + C(yr_c)", data=lr_df).fit(disp=0)
f3 = smf.logit("W ~ camp12 + mid + C(yr_c) + C(type) + repeat", data=lr_df).fit(disp=0)
for name, f in [("W_base", f1), ("W_year_FE", f2), ("W_year_FE_type_repeat", f3)]:
    fits[name] = {k: {"coef": round(float(f.params[k]), 3), "OR": round(float(np.exp(f.params[k])), 3),
                      "p": float(f.pvalues[k])} for k in f.params.index if k in ("camp12", "mid", "repeat", "Intercept")}
    fits[name]["n"] = int(f.nobs)
# escalation outcome
g3 = smf.logit("E ~ camp12 + mid + C(yr_c) + C(type) + repeat", data=lr_df).fit(disp=0)
fits["E_year_FE_type_repeat"] = {k: {"coef": round(float(g3.params[k]), 3), "OR": round(float(np.exp(g3.params[k])), 3),
                                    "p": float(g3.pvalues[k])} for k in g3.params.index if k in ("camp12", "mid", "repeat")}
fits["E_year_FE_type_repeat"]["n"] = int(g3.nobs)
# 2012-vs-rest year dummy model
lr_df["y12"] = (lr_df.yr == 2012).astype(int)
f4 = smf.logit("W ~ y12 + C(type) + repeat", data=lr_df).fit(disp=0)
fits["W_y12_vs_rest_type_repeat"] = {k: {"coef": round(float(f4.params[k]), 3), "OR": round(float(np.exp(f4.params[k])), 3),
                                        "p": float(f4.pvalues[k])} for k in ("y12", "repeat")}
fits["W_y12_vs_rest_type_repeat"]["n"] = int(f4.nobs)
RES["logit"] = fits

# ---------- 9. Poisson volume model: hi passages per speech-month, campaign vs not ----------
mon = idx.groupby("ym").size().rename("speeches").to_frame()
hmon = HN.groupby("ym").size().rename("hi")
mon = mon.join(hmon, how="left").fillna({"hi": 0})
mon = mon[mon.index.year.isin(range(2009, 2017))]
mon["yr"] = mon.index.year
mon["period"] = [period(pd.Timestamp(str(p) + "-15")) for p in mon.index]
mon["camp12"] = (mon.period == "campaign_2012").astype(int)
mon["mid"] = mon.period.isin(["midterm_2010", "midterm_2014"]).astype(int)
mod = smf.glm("hi ~ camp12 + mid + C(yr)", data=mon, family=sm.families.Poisson(),
              offset=np.log(mon.speeches.clip(lower=1))).fit(scale="X2")  # quasi-Poisson (overdispersed)
RES["poisson_hi_per_speech_month"] = {k: {"coef": round(float(mod.params[k]), 3), "rate_ratio": round(float(np.exp(mod.params[k])), 3),
                                          "p": float(mod.pvalues[k])} for k in ("camp12", "mid")}
RES["poisson_hi_per_speech_month"]["n_months"] = int(len(mon))
RES["poisson_hi_per_speech_month"]["dispersion_pearson"] = round(float(mod.pearson_chi2 / mod.df_resid), 3)
mon.to_csv(OUT / "monthly_counts.csv")

# ---------- 10. sensitivity: thresholds 30 / 70, context-window frame coding ----------
sens = {}
for th in (30, 50, 70):
    d = pool[(pool.final_score_pct >= th) & (~pool.questioner)]
    t = frame_table(d, "period").to_dict(orient="index")
    sens[f"th{th}"] = {"n": int(len(d)), "by_period": t,
                       "chi2_withdraw_period": chi(d.assign(wl=d.withdraw_frame.map({True: "W", False: "notW"})), "period", "wl")}
RES["sensitivity_threshold"] = sens

# frame with context (passage + context_before/after) as robustness
ctx = (pool.passage + " " + pool.context_before.fillna("") + " " + pool.context_after.fillna(""))
pool["withdraw_ctx"] = ctx.str.contains(WITHDRAW)
dH = pool[(pool.final_score_pct >= 50) & (~pool.questioner)]
RES["context_frame_by_period"] = dH.groupby("period")["withdraw_ctx"].mean().round(3).to_dict()
RES["context_frame_chi2_period"] = chi(dH.assign(wl=dH.withdraw_ctx.map({True: "W", False: "notW"})), "period", "wl")

# named-term-only check (user's explicit list)
RES["named_term_share_by_period"] = HN.groupby("period")["named_frame"].mean().round(3).to_dict()

# ---------- 11. chart ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
yrs = sorted(HN.yr.dropna().unique())
w_share = HN.groupby("yr")["withdraw_frame"].mean().reindex(yrs)
e_share = HN.groupby("yr")["escal_frame"].mean().reindex(yrs)
u_w = HU.groupby("yr")["withdraw_frame"].mean().reindex(yrs)
ax = axes[0]
ax.plot(yrs, w_share, marker="o", label="withdrawal frame (all passages)", color="#1f5fa8")
ax.plot(yrs, e_share, marker="s", label="escalation/combat frame (all)", color="#b5452b")
ax.plot(yrs, u_w, marker="^", ls="--", label="withdrawal frame (unique clusters)", color="#1f5fa8", alpha=0.5)
ax.set_title("Frame share per year, high-likelihood (>=50), non-questioner")
ax.set_ylabel("share of passages"); ax.set_xticks(yrs); ax.grid(alpha=0.3); ax.legend(fontsize=8)
ax.set_ylim(0, 1)
ax = axes[1]
m = mon.copy(); m["rate"] = m.hi / m.speeches.clip(lower=1)
xs = [p.to_timestamp() for p in m.index]
ax.bar(xs, m.rate, width=20, color=["#e0a100" if c else ("#7a7a7a" if mm else "#bbbbbb") for c, mm in zip(m.camp12, m.mid)])
ax.set_title("High-likelihood passages per speech, by month\n(gold=2012 campaign window, grey=2010/2014 midterm, light=other)", fontsize=10)
ax.set_ylabel("passages per speech in month")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "election_frame.png", dpi=130)

# ---------- 12. diagnostics: is the 2012 withdrawal frame event-driven? ----------
D = {}
W12 = HN2[HN2.period == "campaign_2012"]
D["campaign12_withdraw_by_month"] = W12.groupby(W12.date.dt.month).agg(n=("ref_id","size"), w=("withdraw_frame","mean")).round(3).to_dict(orient="index")
# event cluster: May 2012 (Kabul SPA signing May 1-2, Bagram address May 1, Chicago NATO summit May 20-21)
may = W12.date.dt.month == 5
D["campaign12_may_n"] = int(may.sum()); D["campaign12_may_withdraw_share"] = round(float(W12[may].withdraw_frame.mean()), 3)
D["campaign12_nonmay_n"] = int((~may).sum()); D["campaign12_nonmay_withdraw_share"] = round(float(W12[~may].withdraw_frame.mean()), 3)
D["campaign12_withdraw_hits_in_may"] = int(W12[may].withdraw_frame.sum())
D["campaign12_withdraw_hits_total"] = int(W12.withdraw_frame.sum())
# term decomposition of withdraw frame
def term_counts(df):
    c = Counter()
    for t in df.passage:
        for m in WITHDRAW.findall(t):
            c[m.lower() if isinstance(m, str) else str(m)] += 1
    return c
def term_hits(df):
    c = Counter()
    for t in df.passage:
        for m in WITHDRAW.finditer(t):
            c[m.group(0).lower()] += 1
    return c
D["withdraw_terms_2012_campaign"] = dict(term_hits(W12).most_common(12))
D["withdraw_terms_2012_nonmay"] = dict(term_hits(W12[~may]).most_common(12))
D["withdraw_terms_other_years"] = dict(term_hits(HN2[HN2.yr != 2012]).most_common(12))
D["withdraw_terms_midterms"] = dict(term_hits(HN2[HN2.period.isin(["midterm_2010","midterm_2014"])]).most_common(12))
# 'transition' alone
for lab, dd in [("2012_campaign", W12), ("2012_campaign_nonmay", W12[~may]), ("other_years", HN2[HN2.yr != 2012]), ("midterms", HN2[HN2.period.isin(["midterm_2010","midterm_2014"])])]:
    D[f"transition_share_{lab}"] = round(float(dd.passage.str.contains(r"\btransition\w*", case=False, regex=True).mean()), 3)
    D[f"named_share_{lab}"] = round(float(dd.named_frame.mean()), 3)
# withdraw frame excluding the 'transition' word (handover-of-security semantics)
WD_NOTRANS = re.compile(WITHDRAW.pattern.replace("transition\\w*|", ""), re.I)
D["withdraw_no_transition_share_by_period"] = {per_: round(float(g.passage.str.contains(WD_NOTRANS).mean()),3) for per_, g in HN2.groupby("period")}
D["withdraw_no_transition_share_by_year"] = {int(y_): round(float(g.passage.str.contains(WD_NOTRANS).mean()),3) for y_, g in HN2.groupby("yr")}
# 2012 campaign vs midterms, excluding May 2012 event cluster
camp_nomay = HN2[(HN2.period == "campaign_2012") & (HN2.date.dt.month != 5)]
D["tests_campaign_nonMay_vs_midterms_withdraw"] = two_by_two(camp_nomay.withdraw_frame, HN2[HN2.period.isin(["midterm_2010","midterm_2014"])].withdraw_frame)
D["tests_campaign_nonMay_vs_midterms_no_transition"] = two_by_two(camp_nomay.passage.str.contains(WD_NOTRANS), HN2[HN2.period.isin(["midterm_2010","midterm_2014"])].passage.str.contains(WD_NOTRANS))
D["tests_2012_nonMay_vs_other_years_withdraw"] = two_by_two(HN2[(HN2.yr==2012)&(HN2.date.dt.month!=5)].withdraw_frame, HN2[HN2.yr!=2012].withdraw_frame)
D["tests_2012_nonMay_vs_other_years_no_transition"] = two_by_two(HN2[(HN2.yr==2012)&(HN2.date.dt.month!=5)].passage.str.contains(WD_NOTRANS), HN2[HN2.yr!=2012].passage.str.contains(WD_NOTRANS))
# within-2012: campaign (Jan-Nov 6) vs post-election (Nov 7-Dec 31)
post = HN2[(HN2.yr==2012) & (HN2.date > pd.Timestamp("2012-11-06"))]
D["within2012_post_election_n"] = int(len(post))
D["within2012_post_election_withdraw_share"] = round(float(post.withdraw_frame.mean()),3) if len(post) else None
D["tests_2012_campaign_vs_postelection_withdraw"] = two_by_two(W12.withdraw_frame, post.withdraw_frame) if len(post) else None
# near-dup clusters in 2012 campaign: what are the repeated passages
rep12 = W12[W12.is_repeat].groupby("cluster").agg(k=("ref_id","size"), speeches=("speech_id","nunique"), ex=("passage","first"), dates=("date", lambda x: ",".join(sorted({str(d)[:10] for d in x})))).sort_values("k", ascending=False)
D["repeat_clusters_2012_campaign_top"] = [{"k": int(r.k), "n_speeches": int(r.speeches), "dates": r.dates, "text": r.ex[:160]} for _, r in rep12.head(8).iterrows()]
D["n_repeat_clusters_2012_campaign"] = int(len(rep12))
D["n_repeat_passages_2012_campaign"] = int(W12.is_repeat.sum())
# repeat share within campaign vs midterm, excluding May
D["repeat_share_campaign_nonmay"] = round(float(camp_nomay.is_repeat.mean()),3)
D["repeat_share_campaign_may"] = round(float(W12[may].is_repeat.mean()),3)
D["repeat_share_midterms"] = round(float(HN2[HN2.period.isin(["midterm_2010","midterm_2014"])].is_repeat.mean()),3)
# Poisson re-check excluding May 2012 month
mon2 = mon.copy(); mon2.loc[pd.Period("2012-05"), "camp12"] = 0
mon2 = mon2.drop(index=pd.Period("2012-05"))
mod2 = smf.glm("hi ~ camp12 + mid + C(yr)", data=mon2, family=sm.families.Poisson(), offset=np.log(mon2.speeches.clip(lower=1))).fit(scale="X2")
D["poisson_quasi_excl_may2012"] = {k: {"rr": round(float(np.exp(mod2.params[k])),3), "p": float(mod2.pvalues[k])} for k in ("camp12","mid")}
RES["diagnostics"] = D

# share of withdraw-frame campaign (non-May) passages that sit in repeated near-dup clusters
wf = camp_nomay[camp_nomay.withdraw_frame]
D["withdraw_frame_nonMay_campaign_n"] = int(len(wf))
D["withdraw_frame_nonMay_campaign_in_repeat_clusters"] = int(wf.is_repeat.sum())
D["withdraw_frame_nonMay_campaign_repeat_share"] = round(float(wf.is_repeat.mean()),3) if len(wf) else None
# same, excluding repeated clusters entirely (unique-cluster withdraw share non-May campaign vs midterms)
uq = camp_nomay[~camp_nomay.is_repeat]
D["withdraw_share_nonMay_campaign_excl_repeats"] = round(float(uq.withdraw_frame.mean()),3)
D["n_nonMay_campaign_excl_repeats"] = int(len(uq))
D["tests_nonMay_campaign_excl_repeats_vs_midterms_withdraw"] = two_by_two(uq.withdraw_frame, HN2[HN2.period.isin(["midterm_2010","midterm_2014"]) & ~HN2.is_repeat].withdraw_frame)
D["tests_nonMay_campaign_excl_repeats_vs_other_years_withdraw"] = two_by_two(uq.withdraw_frame, HN2[(HN2.yr!=2012) & ~HN2.is_repeat].withdraw_frame)
RES["diagnostics"] = D

# ---------- write ----------
def conv(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return str(o)
with open(OUT / "results.json", "w") as fh:
    json.dump(RES, fh, indent=1, default=conv)
print(json.dumps({k: RES[k] for k in ("diagnostics","poisson_hi_per_speech_month")}, indent=1, default=conv))
