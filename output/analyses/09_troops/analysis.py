#!/usr/bin/env python3
"""09_troops: US troop levels in Afghanistan vs Obama-speech Afghanistan passage frames/volume.

Run:  .venv/bin/python -I output/analyses/09_troops/analysis.py
Inputs : raw/r44116_11.txt   (pdftotext of CRS R44116 v11, Table 1)
         raw/dl_3bf284.txt   (pdftotext of CRS RL33110, Amy Belasco, Mar 29 2011, Table A-1)
         output/references.csv, speeches_index.csv (READ-ONLY)
Outputs: troops_monthly_CRS_RL33110_TableA1.csv, troops_quarterly_CRS_R44116_Table1.csv,
         quarterly_panel.csv, monthly_panel.csv, results.json, troop_vs_rhetoric.png
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json
import math
import os
import re

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
REF = str(PROJECT) + "/output/references.csv"
IDX = str(PROJECT) + "/output/speeches_index.csv"
OUT = HERE
RETRIEVED = "2026-11-16"
RESULTS = {}

# ---------------------------------------------------------------- 1. outside data
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_monthly():
    """CRS RL33110 Table A-1, Afghanistan row, 2002-2010 (Sep). Flags: a=interpolated, b=CRS estimate."""
    lines = open(os.path.join(RAW, "dl_3bf284.txt"), encoding="utf-8", errors="replace").read().splitlines()
    start = max(i for i, l in enumerate(lines) if "Table A-1. Boots on the Ground in Iraq and Afghanistan by Month" in l)
    end = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("Sources: DOD, Joint Staff"))
    year = None
    rows = []
    for l in lines[start:end]:
        m = re.match(r"^\s+(20\d\d)\s*$", l)
        if m:
            year = int(m.group(1))
            continue
        if re.match(r"^Afghanistan\s", l) and year:
            toks = re.findall(r"[\d,]+[ab]?", l)
            for mi, t in enumerate(toks):
                flag = t[-1] if t[-1] in "ab" else ""
                val = int(t.rstrip("ab").replace(",", ""))
                rows.append({"year": year, "month": mi + 1, "troops_afg": val, "crs_flag": flag})
    df = pd.DataFrame(rows)
    # Source note: Aug 2009 interpolated (not reported), in addition to a-flagged Oct/Nov 2008
    df["note"] = ""
    df.loc[df["crs_flag"] == "a", "note"] = "CRS interpolated (DoD did not report)"
    df.loc[(df.year == 2009) & (df.month == 8), "note"] = "CRS interpolated (DoD did not report; per source note)"
    df.loc[df["crs_flag"] == "b", "note"] = "CRS estimate (DoD plan/average-strength assumption, per source note)"
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    return df


def parse_quarterly():
    """CRS R44116 v11 Table 1: U.S. Armed Forces in Afghanistan by fiscal quarter (troop levels from BOG reports)."""
    lines = open(os.path.join(RAW, "r44116_11.txt"), encoding="utf-8", errors="replace").read().splitlines()
    # body title (not the table-of-contents line, which carries dot leaders)
    t1 = next(i for i, l in enumerate(lines) if l.strip().startswith("Table 1. U.S. Armed Forces and Contractor Personnel in Afghanistan") and "...." not in l)
    rows = []
    for l in lines[t1:t1 + 80]:
        m = re.match(r"^\s*Q([1-4]) FY(\d{4})\s+([\d,]+)\s", l)
        if m:
            rows.append({"fy_q": int(m.group(1)), "fy": int(m.group(2)), "us_armed_forces_afg": int(m.group(3).replace(",", ""))})
    df = pd.DataFrame(rows)
    # Calendar quarter-end mapping (FY Oct-Sep; FYQ1=Oct-Dec, FYQ2=Jan-Mar, FYQ3=Apr-Jun, FYQ4=Jul-Sep)
    qend = {1: 12, 2: 3, 3: 6, 4: 9}
    df["snapshot_month"] = df.fy_q.map(qend)
    df["snapshot_year"] = np.where(df.fy_q == 1, df.fy - 1, df.fy)
    df["snapshot"] = pd.to_datetime(dict(year=df.snapshot_year, month=df.snapshot_month, day=1)) + pd.offsets.MonthEnd(0)
    df["cal_year"] = df.snapshot.dt.year
    df["cal_q"] = df.snapshot.dt.quarter
    df["period"] = df.cal_year.astype(str) + "Q" + df.cal_q.astype(str)
    return df


mon = parse_monthly()
qtr = parse_quarterly()
mon.drop(columns=["year", "month"]).assign(
    source="CRS RL33110 (Belasco, 2011-03-29) Table A-1; DoD Boots on the Ground monthly reports (in country)",
    retrieved=RETRIEVED,
)[["date", "troops_afg", "crs_flag", "note", "source", "retrieved"]].to_csv(
    os.path.join(OUT, "troops_monthly_CRS_RL33110_TableA1.csv"), index=False)
qtr.assign(source="CRS R44116 v11 (Peters, 2021-02-22) Table 1; DoD Boots on the Ground reports",
           retrieved=RETRIEVED)[["fy", "fy_q", "us_armed_forces_afg", "snapshot", "period", "source", "retrieved"]].to_csv(
    os.path.join(OUT, "troops_quarterly_CRS_R44116_Table1.csv"), index=False)
RESULTS["outside_data"] = {
    "monthly_rows_2002_2010": int(len(mon)),
    "monthly_range": [str(mon.date.min().date()), str(mon.date.max().date())],
    "quarterly_rows_FY07Q4_FY16Q4": int(len(qtr)),
    "quarterly_range_FY": [f"FY{qtr.fy.min()}Q{qtr.loc[qtr.fy == qtr.fy.min(), 'fy_q'].min()}", f"FY{qtr.fy.max()}Q{qtr.loc[qtr.fy == qtr.fy.max(), 'fy_q'].max()}"],
}

# Calendar-quarter troop series for 2009Q1..2016Q4 (2016Q4 unavailable: R44116 lists Q1 FY2017 as 'Not Yet Available')
q = qtr[(qtr.cal_year >= 2009) & (qtr.cal_year <= 2016)].sort_values("snapshot").copy()
q = q.set_index("period")
q["troops"] = q["us_armed_forces_afg"]

# ---------------------------------------------------------------- 2. references
refs = pd.read_csv(REF, dtype={"ref_id": str})
idx = pd.read_csv(IDX)
RESULTS["n_refs_raw"] = int(len(refs))
dup_ids = set(idx.loc[idx.dup_of.notna(), "id"])
refs = refs[~refs.speech_id.isin(dup_ids)].copy()
RESULTS["n_refs_after_dup_exclusion"] = int(len(refs))
refs["questioner"] = refs.rationale.fillna("").str.contains("questioner", case=False)
RESULTS["n_refs_questioner_flag"] = int(refs.questioner.sum())
refs["date"] = pd.to_datetime(refs.date)
refs["period"] = refs.date.dt.year.astype(str) + "Q" + refs.date.dt.quarter.astype(str)
refs["month"] = refs.date.dt.to_period("M").astype(str)
refs["text"] = (refs.passage.fillna("") + " " + refs.context_before.fillna("") + " " + refs.context_after.fillna(""))
refs["text_l"] = refs.text.str.lower()

# ---------------------------------------------------------------- 3. transparent frame keywords (regex, lowercase)
FRAMES = {
    "combat": r"\b(combat\w*|fight\w*|battle\w*|offensive\w*|surge\w*|insurgen\w*|taliban|al[- ]qaeda|militant\w*|casualt\w*|killed|enem\w*|attack\w*|firefight\w*)\b",
    "transition": r"\b(transition\w*|hand(?:ed|ing)? ?over|handover|afghan (?:national )?(?:security|army|police|forces|troops)|train(?:ing|ed|s)?|assum\w* (?:the )?(?:security )?responsibilit\w*|lead (?:security )?responsibilit\w*)\b",
    "withdrawal": r"\b(withdraw\w*|draw ?down\w*|come home|bring\w*(?: \w+){0,3} home|end (?:of )?(?:the )?(?:war|combat (?:mission|operations?))|responsibl\w* end|leave afghanistan|exit)\b",
}
for name, pat in FRAMES.items():
    refs[f"f_{name}"] = refs.text_l.str.contains(pat, regex=True)
refs["f_any"] = refs[[f"f_{k}" for k in FRAMES]].any(axis=1)

FRAME_SHARE_KEYS = list(FRAMES.keys())


def panel(df, key):
    """Aggregate by period key: volume, frame-share, category-share."""
    g = df.groupby(key)
    out = pd.DataFrame({
        "n_all": g.size(),
        "n_questioner": g.questioner.sum(),
        "n_nonq": g.apply(lambda x: (~x.questioner).sum()),
        "n_hl": g.apply(lambda x: ((x.final_score_pct >= 50) & (~x.questioner)).sum()),
        "n_war_direct": g.apply(lambda x: ((x.category == "war_direct") & (~x.questioner)).sum()),
    })
    base = df[(df.final_score_pct >= 50) & (~df.questioner)].groupby(key)
    nhl = base.size()
    for k in FRAME_SHARE_KEYS:
        out[f"share_{k}"] = base[f"f_{k}"].mean().reindex(out.index)
        out[f"n_{k}"] = base[f"f_{k}"].sum().reindex(out.index).fillna(0).astype(int)
    out["share_any_frame"] = base["f_any"].mean().reindex(out.index)
    out["n_hl"] = nhl.reindex(out.index).fillna(0).astype(int)
    out["share_war_direct_of_hl"] = base.apply(lambda x: (x.category == "war_direct").mean()).reindex(out.index)
    return out


# quarterly panel 2009Q1..2016Q4 (rhetoric) joined to troops
qp = panel(refs[(refs.date >= "2009-01-01") & (refs.date <= "2016-12-31")], "period")
qp = qp.join(q[["troops", "snapshot"]], how="left")
qp = qp.sort_index()
qp.to_csv(os.path.join(OUT, "quarterly_panel.csv"))

# monthly panel 2009-01..2010-09 (only months with CRS monthly troop data)
mp = panel(refs[(refs.date >= "2009-01-01") & (refs.date <= "2010-09-30")], "month")
mp.index = pd.PeriodIndex(mp.index, freq="M")
mtroops = mon.set_index(mon.date.dt.to_period("M"))["troops_afg"]
mp = mp.join(mtroops.rename("troops"), how="left").dropna(subset=["troops"])
mp.to_csv(os.path.join(OUT, "monthly_panel.csv"))

RESULTS["n_quarters_panel"] = int(len(qp))
RESULTS["n_quarters_with_troops"] = int(qp.troops.notna().sum())
RESULTS["n_months_monthly_panel"] = int(len(mp))
RESULTS["passages_per_quarter"] = qp[["n_all", "n_hl"]].describe().round(1).to_dict()

# ---------------------------------------------------------------- 4. statistics
def pear(x, y):
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0:
        return dict(n=int(len(x)), r=None, p=None, rho=None, p_rho=None)
    r, p = stats.pearsonr(x, y)
    rho, pr = stats.spearmanr(x, y)
    return dict(n=int(len(x)), r=round(float(r), 3), p=round(float(p), 4), rho=round(float(rho), 3), p_rho=round(float(pr), 4))


def acf1(x):
    x = x[~np.isnan(x)]
    return float(acf(x, nlags=1, fft=False)[1]) if len(x) > 3 else float("nan")


def n_eff_corr(x, y):
    """Bartlett-style effective-n adjustment for two autocorrelated series (lag-1 AR)."""
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    n = len(x)
    if n < 6:
        return None
    a, b = acf1(x), acf1(y)
    ab = a * b
    n_eff = n * (1 - ab) / (1 + ab) if (1 + ab) != 0 else n
    n_eff = max(3.0, n_eff)
    r = np.corrcoef(x, y)[0, 1]
    t = r * math.sqrt((n_eff - 2) / max(1e-12, 1 - r * r))
    p = 2 * stats.t.sf(abs(t), df=n_eff - 2)
    return dict(n=n, n_eff=round(float(n_eff), 2), r=round(float(r), 3), p_adj=round(float(p), 4))


lv = qp.dropna(subset=["troops"]).copy()
Y_SERIES = ["share_combat", "share_transition", "share_withdrawal", "share_any_frame", "n_hl", "n_all"]
X = lv.troops.values.astype(float)

levels, diffs, ccf = {}, {}, {}
dtroops = lv.troops.diff()
for y in Y_SERIES:
    yv = lv[y].astype(float).values
    levels[y] = pear(X, yv)
    dy = lv[y].astype(float).diff()
    diffs[y] = pear(dtroops.values, dy.values)
    # cross-correlation of first differences, lag k: k>0 => rhetoric change at t vs troop change at t-k (rhetoric lags)
    rows = []
    for k in range(-4, 5):
        if k >= 0:
            xa = dtroops.shift(k).values  # troop change at t-k
            ya = dy.values
        else:
            xa = dtroops.shift(k).values  # troop change at t+|k| (rhetoric leads troops)
            ya = dy.values
        res = n_eff_corr(xa, ya)
        rows.append({"lag_q": k, **(res or {})})
    ccf[y] = rows

# autocorrelation / Ljung-Box on the raw series (quarterly, 2009Q1-2016Q3)
ac = {}
for name, s in [("troops", lv.troops.astype(float)), ("share_combat", lv.share_combat.astype(float)),
                ("share_transition", lv.share_transition.astype(float)),
                ("share_withdrawal", lv.share_withdrawal.astype(float)), ("n_hl", lv.n_hl.astype(float))]:
    v = s.dropna().values
    lb = acorr_ljungbox(v, lags=[4], return_df=True)
    ac[name] = {"n": int(len(v)), "acf1": round(acf1(v), 3), "ljungbox_lag4_p": round(float(lb.lb_pvalue.iloc[0]), 4)}

# OLS on differences with Newey-West (HAC, 2 lags) for combat share and volume on Δtroops (contemporaneous and lagged)
import statsmodels.api as sm

ols = {}
for y in ["share_combat", "share_withdrawal", "share_transition", "n_hl"]:
    dd = pd.DataFrame({"dy": lv[y].astype(float).diff(), "dx0": dtroops, "dx1": dtroops.shift(1), "dx_lead1": dtroops.shift(-1)}).dropna()
    for spec in [["dx0"], ["dx1"], ["dx_lead1"]]:
        m = sm.OLS(dd.dy, sm.add_constant(dd[spec])).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
        ols[f"{y} ~ {spec[0]}"] = {"n": int(m.nobs), "beta": round(float(m.params[spec[0]]), 6),
                                   "p_HAC": round(float(m.pvalues[spec[0]]), 4), "r2": round(float(m.rsquared), 3),
                                   "dw": round(float(sm.stats.durbin_watson(m.resid)), 2)}

# sensitivity: thresholds 30 / 70 for high-likelihood set (combat share, volume)
sens = {}
for thr in [30, 50, 70]:
    sub = refs[(refs.date >= "2009-01-01") & (refs.date <= "2016-12-31")]
    base = sub[(sub.final_score_pct >= thr) & (~sub.questioner)]
    g = base.groupby("period")
    vol = g.size().reindex(qp.index).fillna(0)
    cmb = g["f_combat"].mean().reindex(qp.index)
    tmp = pd.DataFrame({"troops": qp.troops, "vol": vol, "cmb": cmb}).dropna(subset=["troops"])
    sens[f"thr{thr}"] = {"n_quarters": int(len(tmp)), "level_vol": pear(tmp.troops.values.astype(float), tmp.vol.values.astype(float)),
                         "level_combat_share": pear(tmp.troops.values.astype(float), tmp.cmb.values.astype(float)),
                         "diff_vol": pear(tmp.troops.diff().values, tmp.vol.diff().values),
                         "diff_combat_share": pear(tmp.troops.diff().values, tmp.cmb.diff().values)}
RESULTS["sensitivity_threshold"] = sens

# monthly check 2009-01..2010-09 (CRS monthly data; n small)
mlev = {}
mX = mp.troops.values.astype(float)
for y in ["share_combat", "share_withdrawal", "share_transition", "n_hl"]:
    mlev[y] = {"levels": pear(mX, mp[y].astype(float).values), "diffs": pear(mp.troops.diff().values, mp[y].astype(float).diff().values)}
RESULTS["monthly_2009_2010"] = mlev

# lead/lag: which direction? corr(Δshare_t, Δtroops_{t-1}) (rhetoric follows) vs corr(Δshare_t, Δtroops_{t+1}) (rhetoric leads)
RESULTS["levels_quarterly"] = levels
RESULTS["diffs_quarterly"] = diffs
RESULTS["ccf_diffs_quarterly"] = ccf
RESULTS["autocorrelation"] = ac
RESULTS["ols_hac_diffs"] = ols

# high-likelihood quarterly table for the report
table = lv[["troops", "n_hl", "n_all", "share_combat", "share_transition", "share_withdrawal", "share_any_frame"]].copy()
table.index.name = "period"
table.round(3).to_csv(os.path.join(OUT, "quarterly_table_for_report.csv"))
RESULTS["quarterly_table"] = table.round(3).reset_index().to_dict(orient="records")

# ---------------------------------------------------------------- 5. chart
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax1 = plt.subplots(figsize=(10, 5.2), dpi=130)
xs = np.arange(len(lv))
ax1.step(xs, lv.troops.values / 1000, where="mid", color="#1f4e79", lw=2.2, label="US armed forces in Afghanistan (k, quarter-end)")
ax1.set_ylabel("US troops in Afghanistan (thousands)", color="#1f4e79")
ax1.set_xticks(xs)
ax1.set_xticklabels(lv.index, rotation=60, fontsize=8)
ax2 = ax1.twinx()
ax2.bar(xs, lv.n_hl.values, alpha=0.25, color="#b5532b", label="high-likelihood passages (>=50%, non-questioner)")
ax2.plot(xs, lv.share_combat.values * 100, color="#b5532b", marker="o", lw=1.6, label="combat-frame share of HL passages (%)")
ax2.set_ylabel("passages / combat share (%)", color="#b5532b")
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
ax1.set_title("US troop levels vs Obama-speech Afghanistan rhetoric, calendar quarters 2009-2016", fontsize=11)
ax1.grid(alpha=0.2)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "troop_vs_rhetoric.png"))

with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(RESULTS, f, indent=2, default=str)
print(json.dumps(RESULTS, indent=1, default=str)[:20000])
