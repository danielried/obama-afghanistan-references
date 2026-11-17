"""11_approval: Obama job approval (UCSB-hosted weekly series) vs monthly Afghanistan passage volume and tone.
Run: .venv/bin/python -I output/analyses/11_approval/analysis.py
READ-ONLY on the project root.
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json, sqlite3, warnings
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
OUT = str(ANALYSES) + "/11_approval"
PROJ = str(PROJECT) + ""
RAW = f"{OUT}/raw/ucsb_obama_public_approval_raw.csv"
DB = f"{PROJ}/data/speeches.db"
REFS = f"{PROJ}/output/references.csv"
IDX = f"{PROJ}/output/speeches_index.csv"

# ---------- 1. approval series (weekly, UCSB page, Gallup-style) ----------
ap = pd.read_csv(RAW, header=0, index_col=False, usecols=range(8), dtype=str)
ap.columns = ["start", "end", "approve", "disapprove", "unsure", "blank", "dem", "ind"][: ap.shape[1]]
ap = ap.dropna(subset=["start", "end"])
for c in ["approve", "disapprove", "unsure"]:
    ap[c] = pd.to_numeric(ap[c], errors="coerce")
ap["start"] = pd.to_datetime(ap["start"], format="%m/%d/%Y")
ap["end"] = pd.to_datetime(ap["end"], format="%m/%d/%Y")
ap["mid"] = ap["start"] + (ap["end"] - ap["start"]) / 2
ap = ap.sort_values("start").reset_index(drop=True)
ap["month"] = ap["mid"].dt.to_period("M")
ap[["start", "end", "approve", "disapprove", "unsure"]].to_csv(f"{OUT}/approval_weekly_clean.csv", index=False)

apm = ap.groupby("month").agg(approve_mean=("approve", "mean"), approve_weeks=("approve", "size")).reset_index()

# ---------- 2. Afghanistan passages per month ----------
refs = pd.read_csv(REFS, usecols=["ref_id", "speech_id", "date", "final_score_pct", "rationale", "tone"])
refs["date"] = pd.to_datetime(refs["date"])
refs["month"] = refs["date"].dt.to_period("M")
refs["questioner"] = refs["rationale"].fillna("").str.contains("questioner", case=False)

# exposure: words per speech from the full texts (non-dup, status ok)
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
sp = pd.read_sql("select id, date, raw_text from speeches where status='ok' and (dup_of is null or dup_of='')", con)
con.close()
sp["words"] = sp["raw_text"].fillna("").str.split().str.len()
sp["date"] = pd.to_datetime(sp["date"])
sp["month"] = sp["date"].dt.to_period("M")
words_m = sp.groupby("month")["words"].sum().rename("words")
nspeech_m = sp.groupby("month")["id"].size().rename("n_speeches")
# drop speeches with missing dates if any
print("speeches with words:", len(sp), "total words:", int(sp.words.sum()))

def panel(thresh=50, include_questioner=False, months=None):
    r = refs.copy()
    if not include_questioner:
        r = r[~r.questioner]
    hi = r[r.final_score_pct >= thresh]
    g_hi = hi.groupby("month").agg(n_hi=("ref_id", "size"), tone_hi=("tone", "mean"))
    g_all = r.groupby("month").agg(n_all=("ref_id", "size"))
    m = pd.concat([words_m, nspeech_m, g_hi, g_all], axis=1).reset_index()
    m = m.rename(columns={"index": "month"})
    m = m.merge(apm, on="month", how="outer")
    m = m.sort_values("month").reset_index(drop=True)
    m[["n_hi", "n_all", "words", "n_speeches"]] = m[["n_hi", "n_all", "words", "n_speeches"]].fillna(0)
    m["rate_hi"] = m.n_hi / m.words * 1e4   # passages per 10k words of presidential text
    m["rate_all"] = m.n_all / m.words * 1e4
    m = m[(m.month >= pd.Period("2009-01", "M")) & (m.month <= pd.Period("2017-01", "M"))]
    if months is not None:
        m = m[m.month.isin(months)]
    m["d_approve"] = m.approve_mean.diff()
    m["d_rate_hi"] = m.rate_hi.diff()
    m["d_rate_all"] = m.rate_all.diff()
    return m.reset_index(drop=True)

PRIMARY_MONTHS = [p for p in pd.period_range("2009-02", "2016-12", freq="M")]
base = panel(50, False, PRIMARY_MONTHS)
# note: differencing done before subsetting in panel() was on full range; recompute diffs on subset
def add_diffs(m):
    m = m.copy()
    m["d_approve"] = m.approve_mean.diff()
    m["d_rate_hi"] = m.rate_hi.diff()
    m["d_rate_all"] = m.rate_all.diff()
    return m
base = add_diffs(base)
base.to_csv(f"{OUT}/monthly_panel_primary.csv", index=False)

# full range panel (sensitivity)
full = add_diffs(panel(50, False, None))
full.to_csv(f"{OUT}/monthly_panel_full_2009-01_2017-01.csv", index=False)

R = {}
def corr_pair(a, b):
    m = pd.concat([a, b], axis=1).dropna()
    n = len(m)
    if n < 4:
        return dict(n=n, pearson_r=np.nan, pearson_p=np.nan, spearman_rho=np.nan, spearman_p=np.nan)
    pr, pp = stats.pearsonr(m.iloc[:, 0], m.iloc[:, 1])
    sr, sp_ = stats.spearmanr(m.iloc[:, 0], m.iloc[:, 1])
    return dict(n=n, pearson_r=round(pr, 3), pearson_p=round(pp, 4), spearman_rho=round(sr, 3), spearman_p=round(sp_, 4))

# ---------- 3. levels ----------
R["levels"] = {
    "approve_vs_rate_hi": corr_pair(base.approve_mean, base.rate_hi),
    "approve_vs_rate_all": corr_pair(base.approve_mean, base.rate_all),
    "approve_vs_n_hi_raw_count": corr_pair(base.approve_mean, base.n_hi),
    "approve_vs_tone_hi": corr_pair(base.approve_mean, base.tone_hi),
}
# ---------- 4. first differences (contemporaneous) ----------
R["diff_contemporaneous"] = {
    "d_approve_vs_d_rate_hi": corr_pair(base.d_approve, base.d_rate_hi),
    "d_approve_vs_d_rate_all": corr_pair(base.d_approve, base.d_rate_all),
}
# ---------- 5. lags (cross-correlation of first differences) ----------
def lagged(a, b, k):
    # corr(a[t], b[t-k])
    return corr_pair(a, b.shift(k))
lag_rows = []
for k in range(0, 7):
    row = {"lag_months": k}
    x = lagged(base.d_approve, base.d_rate_hi, k)
    row.update({f"afg_leads_r": x["pearson_r"], f"afg_leads_p": x["pearson_p"], "n": x["n"]})
    y = lagged(base.d_rate_hi, base.d_approve, k)
    row.update({f"approve_leads_r": y["pearson_r"], f"approve_leads_p": y["pearson_p"]})
    lag_rows.append(row)
lag_df = pd.DataFrame(lag_rows)
lag_df.to_csv(f"{OUT}/lag_correlations.csv", index=False)
R["lag_table"] = lag_df.to_dict(orient="records")

# ---------- 6. stationarity ----------
def adf(s):
    s = s.dropna()
    stat, p, *_ = adfuller(s, autolag="AIC")
    return dict(stat=round(stat, 3), p=round(p, 4), n=len(s))
R["adf"] = {
    "approve_level": adf(base.approve_mean),
    "approve_diff": adf(base.d_approve),
    "rate_hi_level": adf(base.rate_hi),
    "rate_hi_diff": adf(base.d_rate_hi),
    "tone_hi_level": adf(base.tone_hi),
}

# ---------- 7. Granger (on first differences) ----------
def granger(caused, causing, maxlag=3):
    d = pd.concat([caused, causing], axis=1).dropna()
    d.columns = ["y", "x"]
    out = {}
    res = grangercausalitytests(d[["y", "x"]].values, maxlag=maxlag)
    for lag, r in res.items():
        f, p, df_denom, df_num = r[0]["ssr_ftest"]
        out[int(lag)] = dict(F=round(f, 3), p=round(p, 4), df_num=int(df_num), df_denom=int(df_denom))
    return dict(n=len(d), by_lag=out)
R["granger"] = {
    "afg_rate_hi_granger_causes_approval": granger(base.d_approve, base.d_rate_hi, 3),
    "approval_granger_causes_afg_rate_hi": granger(base.d_rate_hi, base.d_approve, 3),
}

# ---------- 8. sensitivity ----------
sens = {}
for thresh in [30, 50, 70]:
    b = add_diffs(panel(thresh, False, PRIMARY_MONTHS))
    sens[f"thresh_{thresh}"] = {
        "levels_r": corr_pair(b.approve_mean, b.rate_hi)["pearson_r"],
        "levels_p": corr_pair(b.approve_mean, b.rate_hi)["pearson_p"],
        "diff_lag0": corr_pair(b.d_approve, b.d_rate_hi),
        "diff_lag1_afg_leads": corr_pair(b.d_approve, b.d_rate_hi.shift(1)),
        "granger_afg_to_approve_lag1_p": granger(b.d_approve, b.d_rate_hi, 1)["by_lag"][1]["p"],
        "granger_afg_to_approve_lag2_p": granger(b.d_approve, b.d_rate_hi, 2)["by_lag"][2]["p"],
        "granger_approve_to_afg_lag1_p": granger(b.d_rate_hi, b.d_approve, 1)["by_lag"][1]["p"],
    }
b = add_diffs(panel(50, True, PRIMARY_MONTHS))
sens["incl_questioner_passages_thresh50"] = {
    "levels_r": corr_pair(b.approve_mean, b.rate_hi)["pearson_r"],
    "levels_p": corr_pair(b.approve_mean, b.rate_hi)["pearson_p"],
    "diff_lag0": corr_pair(b.d_approve, b.d_rate_hi),
}
b = add_diffs(panel(50, False, PRIMARY_MONTHS))
sens["all_passages_not_hi_thresh"] = {
    "levels_r_rate_all": corr_pair(b.approve_mean, b.rate_all)["pearson_r"],
    "levels_p_rate_all": corr_pair(b.approve_mean, b.rate_all)["pearson_p"],
    "diff_lag0_rate_all": corr_pair(b.d_approve, b.d_rate_all),
}
b = add_diffs(full)  # 2009-01 and 2017-01 partial months included
sens["full_range_incl_partial_months"] = {
    "levels": corr_pair(b.approve_mean, b.rate_hi),
    "diff_lag0": corr_pair(b.d_approve, b.d_rate_hi),
}
# outlier check: Jan 2013 peak is one Karzai press conference + joint statement (~154 passages)
b = panel(50, False, PRIMARY_MONTHS)
b.loc[b.month.astype(str) == "2013-01", "rate_hi"] = np.nan  # blank the month, keep the time index intact
b = add_diffs(b)
sens["exclude_2013_01_karzai_month"] = {
    "levels_r_rate_hi": corr_pair(b.approve_mean, b.rate_hi)["pearson_r"],
    "levels_p_rate_hi": corr_pair(b.approve_mean, b.rate_hi)["pearson_p"],
    "diff_lag0": corr_pair(b.d_approve, b.d_rate_hi),
}
R["sensitivity"] = sens

# tone: how many months with hi passages
R["months"] = {"primary_n": len(base), "months_with_zero_hi_passages": int((base.n_hi == 0).sum()),
               "months_with_no_approval": int(base.approve_mean.isna().sum()),
               "hi_passages_total_primary": int(base.n_hi.sum())}

# ---------- 9. validation of approval series against published Gallup values ----------
# Published values fetched 2026-11-16:
#  news.gallup.com/poll/151025 monthly 2016-2017 (approve %): Apr16 50, May16 51, Jun16 52, Jul16 51, Aug16 51,
#    Sep16 52, Oct16 54, Nov16 56, Dec16 56
#  news.gallup.com/poll/148394 / 149966 / 152123 text: Jan2011 49, May2011 50, Jun2011 46, Aug2011 41, Sep2011 41,
#    Feb2012 45, Aug2012 45
#  news.gallup.com/poll/113980 (daily 3-day) Jan 2017 approx 57
pub = {"2011-01": 49, "2011-05": 50, "2011-06": 46, "2011-08": 41, "2011-09": 41, "2012-02": 45, "2012-08": 45,
       "2016-04": 50, "2016-05": 51, "2016-06": 52, "2016-07": 51, "2016-08": 51, "2016-09": 52, "2016-10": 54,
       "2016-11": 56, "2016-12": 56}
ap_m = apm.copy(); ap_m["m"] = ap_m.month.astype(str)
val = []
for k, v in pub.items():
    row = ap_m[ap_m.m == k]
    val.append({"month": k, "published_gallup_pct": v,
                "ucsb_weekly_mean_pct": round(float(row.approve_mean.iloc[0]), 1) if len(row) else np.nan,
                "weeks": int(row.approve_weeks.iloc[0]) if len(row) else 0})
val_df = pd.DataFrame(val)
val_df["diff"] = val_df.ucsb_weekly_mean_pct - val_df.published_gallup_pct
val_df.to_csv(f"{OUT}/validation_vs_published_gallup.csv", index=False)
R["validation"] = {"n": len(val_df), "mean_abs_diff": round(float(val_df["diff"].abs().mean()), 2),
                   "max_abs_diff": round(float(val_df["diff"].abs().max()), 2)}
print(val_df.to_string(index=False))

# ---------- 10. chart ----------
fig, ax = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
x = base.month.dt.to_timestamp()
ax[0].plot(x, base.approve_mean, color="#1f4e79", lw=1.8, label="Approval (monthly mean of weekly, %)")
ax[0].set_ylabel("Approve %")
ax2 = ax[0].twinx()
ax2.bar(x, base.rate_hi, width=20, color="#c0504d", alpha=0.35, label="Afghan passages (>=50) per 10k words")
ax2.set_ylabel("Passages per 10k words")
h1, l1 = ax[0].get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax[0].legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
ax[0].set_title("Obama approval vs Afghanistan passage rate, Feb 2009 to Dec 2016")
ax[1].scatter(base.d_rate_hi, base.d_approve, s=18, color="#1f4e79")
ax[1].axhline(0, color="grey", lw=0.6); ax[1].axvline(0, color="grey", lw=0.6)
ax[1].set_xlabel("Change in Afghan passage rate (month over month)")
ax[1].set_ylabel("Change in approval (points)")
rr = R["diff_contemporaneous"]["d_approve_vs_d_rate_hi"]
ax[1].set_title(f"First differences, lag 0: r={rr['pearson_r']}, p={rr['pearson_p']}, n={rr['n']}")
fig.savefig(f"{OUT}/approval_vs_afghan.png", dpi=130)

with open(f"{OUT}/results.json", "w") as f:
    json.dump(R, f, indent=2, default=lambda o: None if (isinstance(o, float) and np.isnan(o)) else str(o))
print(json.dumps(R, indent=1, default=str))
