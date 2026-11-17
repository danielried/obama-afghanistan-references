"""08_casualties: monthly US military deaths (OEF/OFS, DoD via Wikipedia table) vs
Afghanistan high-likelihood mention volume and tone in Obama presidency speeches, 2009-2016.

Run: .venv/bin/python -I output/analyses/08_casualties/analysis.py
Reads (read-only): output/references.csv, speeches_index.csv
Reads (job folder): casualties_monthly_dod_wiki.csv
Writes: panel_monthly.csv, ccf.csv, adf.csv, granger.csv, sensitivity.csv, numbers.json, casualties_vs_rhetoric.png
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json
import os
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests, ccf
from statsmodels.tsa.vector_ar.var_model import VAR

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = str(PROJECT) + "/output"
HL_THRESH = 50          # high-likelihood threshold (project convention)
MAXLAG = 6
CCF_LAGS = 6

refs = pd.read_csv(os.path.join(PROJ, "references.csv"))
idx = pd.read_csv(os.path.join(PROJ, "speeches_index.csv"))
cas = pd.read_csv(os.path.join(HERE, "casualties_monthly_dod_wiki.csv"))

# ---- speech universe: drop duplicates, keep status ok
idx = idx[idx["dup_of"].isna()].copy()
idx["date"] = pd.to_datetime(idx["date"])
idx["ym"] = idx["date"].dt.to_period("M")
idx_ok = idx[idx["status"] == "ok"].copy()
dup_ids = set(pd.read_csv(os.path.join(PROJ, "speeches_index.csv")).query("dup_of.notna()")["id"])
refs = refs[~refs["speech_id"].isin(dup_ids)].copy()

refs["date"] = pd.to_datetime(refs["date"])
refs["ym"] = refs["date"].dt.to_period("M")
refs["questioner"] = refs["rationale"].fillna("").str.contains("questioner_not_president")
refs_nq = refs[~refs["questioner"]].copy()   # President's own words only

months = pd.period_range("2009-01", "2016-12", freq="M")

spk = idx_ok[(idx_ok["ym"] >= months[0]) & (idx_ok["ym"] <= months[-1])]
n_speech = spk.groupby("ym").size().reindex(months, fill_value=0)
words_k = (spk.groupby("ym")["text_len"].sum() / 1000.0).reindex(months, fill_value=0.0)


def panel(threshold):
    hl = refs_nq[(refs_nq["final_score_pct"] >= threshold)
                 & (refs_nq["ym"] >= months[0]) & (refs_nq["ym"] <= months[-1])]
    n_hl = hl.groupby("ym").size().reindex(months, fill_value=0)
    tone_m = hl.groupby("ym")["tone"].mean().reindex(months)
    tone_n = hl.groupby("ym")["tone"].count().reindex(months, fill_value=0)
    p = pd.DataFrame({
        "ym": months,
        "n_speeches": n_speech.values,
        "n_hl_passages": n_hl.values,
        "rate_per_speech": (n_hl / n_speech.replace(0, np.nan)).values,
        "rate_per_1000_words": (n_hl / words_k.replace(0, np.nan)).values,
        "mean_tone_hl": tone_m.values,
        "n_tone": tone_n.values,
    })
    p = p.merge(cas.assign(ym=pd.PeriodIndex(pd.to_datetime(
        dict(year=cas.year, month=cas.month, day=1)), freq="M"))[["ym", "us_deaths_oef_ofs_all_theaters"]],
        on="ym", how="left")
    p = p.rename(columns={"us_deaths_oef_ofs_all_theaters": "us_deaths"})
    return p


P = panel(HL_THRESH)
assert P["us_deaths"].notna().all(), "casualty merge incomplete"
P.assign(ym=P["ym"].astype(str)).to_csv(os.path.join(HERE, "panel_monthly.csv"), index=False)

numbers = {}
numbers["n_refs_total"] = int(len(refs))
numbers["n_questioner_flagged"] = int(refs["questioner"].sum())
numbers["n_speeches_ok_nondup_2009_2016"] = int(n_speech.sum())
numbers["n_hl_passages_nonq"] = int(P["n_hl_passages"].sum())
numbers["months_with_zero_hl"] = int((P["n_hl_passages"] == 0).sum())
numbers["months_with_no_tone"] = int(P["mean_tone_hl"].isna().sum())
numbers["total_us_deaths_2009_2016"] = int(P["us_deaths"].sum())

# ---- stationarity (ADF, constant; auto lag by AIC)
def adf(x):
    x = pd.Series(x).dropna()
    r = adfuller(x, autolag="AIC", regression="c")
    return {"stat": float(r[0]), "p": float(r[1]), "lags": int(r[2]), "n": int(r[3])}


tone_series = P["mean_tone_hl"].interpolate(limit_direction="both")  # LABELED: linear fill for tone-only months
adf_rows = []
for name, s in [("us_deaths", P["us_deaths"]), ("rate_per_speech", P["rate_per_speech"]),
                ("mean_tone_hl", P["mean_tone_hl"]), ("mean_tone_hl_interp", tone_series)]:
    s = s.astype(float)
    lvl = adf(s)
    d = adf(s.diff())
    adf_rows.append({"series": name, "level_stat": lvl["stat"], "level_p": lvl["p"], "level_lags": lvl["lags"],
                     "diff_stat": d["stat"], "diff_p": d["p"], "diff_lags": d["lags"]})
adf_df = pd.DataFrame(adf_rows)
adf_df.to_csv(os.path.join(HERE, "adf.csv"), index=False)

# ---- first-differenced series for cross-correlation and Granger
dcas = P["us_deaths"].astype(float).diff()
drate = P["rate_per_speech"].astype(float).diff()
dtone = tone_series.diff()

def ccf_table(x, y, label, maxlag=CCF_LAGS):
    """corr(x_t, y_{t+k}) for k in -maxlag..maxlag, pairwise complete. k>0 => x leads y."""
    rows = []
    n_band = None
    for k in range(-maxlag, maxlag + 1):
        if k >= 0:
            a, b = x.iloc[: len(x) - k] if k else x, y.iloc[k:]
        else:
            a, b = x.iloc[-k:], y.iloc[: len(y) + k]
        m = pd.concat([a.reset_index(drop=True), b.reset_index(drop=True)], axis=1).dropna()
        r, p = stats.pearsonr(m.iloc[:, 0], m.iloc[:, 1])
        rows.append({"pair": label, "lag": k, "n": len(m), "r": r, "p": p})
    return pd.DataFrame(rows)

ccf_all = pd.concat([
    ccf_table(dcas, drate, "dDeaths -> dRate (lag k: deaths_t vs rate_{t+k})"),
    ccf_table(dcas, dtone, "dDeaths -> dTone"),
    ccf_table(drate, dtone, "dRate -> dTone"),
])
ccf_all["bonferroni_p"] = np.minimum(ccf_all["p"] * len(ccf_all), 1.0)
ccf_all.to_csv(os.path.join(HERE, "ccf.csv"), index=False)

# Simple benchmark: lag-0 level correlation (not differenced) for reference
lvl_r = {}
for nm, a, b in [("deaths_vs_rate", P["us_deaths"], P["rate_per_speech"]),
                 ("deaths_vs_tone", P["us_deaths"], tone_series)]:
    m = pd.concat([a, b], axis=1).dropna()
    r, p = stats.spearmanr(m.iloc[:, 0], m.iloc[:, 1])
    lvl_r[nm] = {"spearman_rho": float(r), "p": float(p), "n": int(len(m))}
numbers["levels_spearman"] = lvl_r


# ---- Granger causality (first differences), lag selection by VAR AIC
def granger(y_name, x_name, dy, dx, maxlag=MAXLAG):
    d = pd.concat([dy.rename("y"), dx.rename("x")], axis=1).dropna().reset_index(drop=True)
    sel = VAR(d[["y", "x"]]).select_order(maxlags=maxlag)
    aic_lag = int(sel.aic) if sel.aic else 1
    aic_lag = max(1, aic_lag)
    res = grangercausalitytests(d[["y", "x"]], maxlag=maxlag)
    out = []
    for L in range(1, maxlag + 1):
        f = res[L][0]["ssr_ftest"]
        c = res[L][0]["ssr_chi2test"]
        out.append({"cause": x_name, "effect": y_name, "lag": L, "n": int(len(d) - L),
                    "F": float(f[0]), "p_F": float(f[1]), "p_chi2": float(c[1]),
                    "selected_by_aic": L == aic_lag})
    return pd.DataFrame(out)


gr = pd.concat([
    granger("dRate", "dDeaths", drate, dcas),
    granger("dDeaths", "dRate", dcas, drate),
    granger("dTone", "dDeaths", dtone, dcas),
    granger("dDeaths", "dTone", dcas, dtone),
])
gr.to_csv(os.path.join(HERE, "granger.csv"), index=False)

# Lag selected by AIC per direction
aic_sel = {}
for nm, dy, dx in [("deaths->rate", drate, dcas), ("rate->deaths", dcas, drate),
                   ("deaths->tone", dtone, dcas), ("tone->deaths", dcas, dtone)]:
    d = pd.concat([dy, dx], axis=1).dropna().reset_index(drop=True)
    try:
        aic_sel[nm] = int(VAR(d).select_order(maxlags=MAXLAG).selected_orders["aic"])
    except Exception as e:  # noqa
        aic_sel[nm] = f"error: {e}"
numbers["aic_selected_lag"] = aic_sel

# ---- sensitivity: thresholds 30/70, per-1000-words normalisation
sens = []
for thr in (30, 50, 70):
    Pt = panel(thr)
    dc = Pt["us_deaths"].astype(float).diff()
    for norm in ("rate_per_speech", "rate_per_1000_words"):
        dr = Pt[norm].astype(float).diff()
        m = pd.concat([dc, dr], axis=1).dropna()
        r0, p0 = stats.pearsonr(m.iloc[:, 0], m.iloc[:, 1])
        # Lag-1 cross-correlation: deaths_t vs rate_{t+1}
        a = dc.iloc[:-1].reset_index(drop=True)
        b = dr.iloc[1:].reset_index(drop=True)
        mm = pd.concat([a, b], axis=1).dropna()
        r1, p1 = stats.pearsonr(mm.iloc[:, 0], mm.iloc[:, 1])
        # Granger deaths->rate at lag 1 and 2
        g = granger(norm, "dDeaths", dr, dc, maxlag=2)
        sens.append({"threshold": thr, "norm": norm, "n_hl_total": int(Pt["n_hl_passages"].sum()),
                     "r_lag0_diff": float(r0), "p_lag0_diff": float(p0), "n_lag0": int(len(m)),
                     "r_deaths_t_rate_t+1": float(r1), "p_lag1": float(p1),
                     "granger_deaths_to_rate_lag1_p": float(g.loc[g.lag == 1, "p_F"].iloc[0]),
                     "granger_deaths_to_rate_lag2_p": float(g.loc[g.lag == 2, "p_F"].iloc[0])})
sens_df = pd.DataFrame(sens)
sens_df.to_csv(os.path.join(HERE, "sensitivity.csv"), index=False)

# ---- Chart
fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=False,
                       gridspec_kw={"height_ratios": [1.1, 1]})
x = P["ym"].dt.to_timestamp()
ax[0].bar(x, P["us_deaths"], width=20, color="#9aa5b1", label="US deaths (DoD, OEF/OFS all theaters)")
ax[0].set_ylabel("US deaths / month")
ax2 = ax[0].twinx()
ax2.plot(x, P["rate_per_speech"], color="#c0392b", lw=1.8, label="High-likelihood Afghan passages per speech")
ax2.set_ylabel("Passages per speech")
h1, l1 = ax[0].get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax[0].legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8)
ax[0].set_title("Monthly US deaths vs Afghanistan rhetoric (2009-2016)")

# Lagged CCF of first differences: deaths vs rate
c = ccf_all[ccf_all["pair"].str.startswith("dDeaths -> dRate")]
band = 1.96 / np.sqrt(c["n"].median())
ax[1].bar(c["lag"], c["r"], color=["#c0392b" if p < 0.05 else "#7f8c8d" for p in c["p"]])
ax[1].axhline(band, ls="--", color="k", lw=0.8)
ax[1].axhline(-band, ls="--", color="k", lw=0.8)
ax[1].axhline(0, color="k", lw=0.5)
ax[1].set_xlabel("Lag k (k>0: deaths lead rate by k months)")
ax[1].set_ylabel("r (first differences)")
ax[1].set_title("Cross-correlation of first differences (red = p<0.05 unadjusted; dashed = approx 95% band)")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "casualties_vs_rhetoric.png"), dpi=130)

# ---- print summary
numbers["adf"] = adf_df.to_dict(orient="records")
numbers["ccf_deaths_rate"] = c[["lag", "n", "r", "p"]].round(4).to_dict(orient="records")
numbers["granger"] = gr.round(5).to_dict(orient="records")
numbers["sensitivity"] = sens_df.round(4).to_dict(orient="records")
with open(os.path.join(HERE, "numbers.json"), "w") as f:
    json.dump(numbers, f, indent=1, default=float)

pd.set_option("display.width", 200)
print("N refs", numbers["n_refs_total"], "questioner", numbers["n_questioner_flagged"],
      "speeches", numbers["n_speeches_ok_nondup_2009_2016"], "HL nonq", numbers["n_hl_passages_nonq"])
print("zero-HL months", numbers["months_with_zero_hl"], "no-tone months", numbers["months_with_no_tone"])
print("total deaths", numbers["total_us_deaths_2009_2016"])
print(adf_df.round(4).to_string(index=False))
print(c[["lag", "n", "r", "p"]].round(4).to_string(index=False))
print(ccf_all[~ccf_all["pair"].str.startswith("dDeaths -> dRate")].round(4).to_string(index=False))
print(gr.round(4).to_string(index=False))
print("levels", lvl_r, "AIC lags", aic_sel)
print(sens_df.round(4).to_string(index=False))

# ---- Robustness: remove month-of-year seasonality and linear time trend (OLS residuals),
# then repeat differenced CCF + Granger deaths<->rate on the residual series.
import statsmodels.api as sm
t = np.arange(len(P), dtype=float)
moy = P["ym"].dt.month.values
D = pd.get_dummies(pd.Series(moy, name="m"), prefix="m", drop_first=True).astype(float)
X = sm.add_constant(pd.concat([pd.Series(t, name="t"), D], axis=1))
def resid(y):
    yy = pd.Series(y.values, dtype=float)
    ok = yy.notna().values
    m = sm.OLS(yy[ok].values, X[ok].values).fit()
    out = pd.Series(np.nan, index=yy.index)
    out[ok] = m.resid
    return out
r_dea = resid(P["us_deaths"])
r_rate = resid(P["rate_per_speech"])
# partial correlation of levels, controlling for trend + month-of-year
mm = pd.concat([r_dea, r_rate], axis=1).dropna()
pr, pp = stats.pearsonr(mm.iloc[:, 0], mm.iloc[:, 1])
numbers["robust_partial_levels_resid_r"] = {"r": float(pr), "p": float(pp), "n": int(len(mm))}
# first differences of residual series
rd_dea = r_dea.diff()
rd_rate = r_rate.diff()
cc_res = ccf_table(rd_dea, rd_rate, "resid dDeaths -> dRate")
cc_res.to_csv(os.path.join(HERE, "ccf_residual_robustness.csv"), index=False)
gr_res = granger("dRate_resid", "dDeaths_resid", rd_rate, rd_dea)
gr_res2 = granger("dDeaths_resid", "dRate_resid", rd_dea, rd_rate)
gr_res = pd.concat([gr_res, gr_res2])
gr_res.to_csv(os.path.join(HERE, "granger_residual_robustness.csv"), index=False)
numbers["robust_ccf_resid"] = cc_res[["lag", "n", "r", "p"]].round(4).to_dict(orient="records")
numbers["robust_granger_resid"] = gr_res.round(5).to_dict(orient="records")
print("ROBUST resid levels partial r", round(pr, 4), round(pp, 4), len(mm))
print(cc_res[["lag", "n", "r", "p"]].round(4).to_string(index=False))
print(gr_res.round(4).to_string(index=False))
with open(os.path.join(HERE, "numbers.json"), "w") as f:
    json.dump(numbers, f, indent=1, default=float)
