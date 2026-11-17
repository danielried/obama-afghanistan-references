"""05_salience_tone: monthly salience (high-likelihood passages per speech) vs mean VADER tone.

Run: .venv/bin/python -I output/analyses/05_salience_tone/analysis.py
Read-only on the project root. Writes only into this folder.
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = str(ANALYSES) + "/05_salience_tone"
REFS = str(PROJECT) + "/output/references.csv"
SPEECHES = str(PROJECT) + "/output/speeches_index.csv"
PRIMARY_THR = 50
SENS_THRS = [30, 70]
MAX_LAG = 3
rng = np.random.default_rng(20260116)


def monthly_panel(refs, speeches, thr, drop_questioner=True):
    r = refs.copy()
    is_q = r["rationale"].fillna("").str.contains("questioner", case=False)
    n_q = int(is_q.sum())
    if drop_questioner:
        r = r[~is_q]
    r["month"] = r["date"].str[:7]
    hi = r[r["final_score_pct"] >= thr]
    s = speeches[speeches["dup_of"].isna() & (speeches["status"] == "ok")].copy()
    s["month"] = s["date"].str[:7]
    months = pd.period_range(s["month"].min(), s["month"].max(), freq="M").astype(str)
    n_sp = s.groupby("month").size().reindex(months, fill_value=0)
    n_hi = hi.groupby("month").size().reindex(months, fill_value=0)
    tone_mean = hi.groupby("month")["tone"].mean().reindex(months)
    panel = pd.DataFrame({
        "n_speeches": n_sp, "n_hi": n_hi,
        "salience": n_hi / n_sp.replace(0, np.nan),
        "tone_mean": tone_mean,
    })
    panel.index.name = "month"
    return panel, n_q


def acf1(x):
    x = np.asarray(x, float)
    x = x - x.mean()
    return float(np.sum(x[:-1] * x[1:]) / np.sum(x * x))


def eff_n(n, rx, ry):
    # Bartlett-type correction for correlation between two AR(1)-like series.
    num = 1 - rx * ry
    den = 1 + rx * ry
    return max(3.0, n * num / den) if den != 0 else n


def pair_corr(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    if n < 4:
        return dict(n=n, pearson_r=np.nan, pearson_p=np.nan, spearman_rho=np.nan,
                    spearman_p=np.nan, n_eff=np.nan, pearson_p_eff=np.nan, spearman_p_eff=np.nan)
    pr, pp = stats.pearsonr(x, y)
    sr, sp = stats.spearmanr(x, y)
    ne = eff_n(n, acf1(x), acf1(y)) if np.std(x) > 0 and np.std(y) > 0 else np.nan
    if np.isfinite(ne) and ne > 3:
        t = pr * np.sqrt((ne - 2) / max(1e-12, 1 - pr ** 2))
        pp_eff = 2 * stats.t.sf(abs(t), df=ne - 2)
        # Spearman: same t approximation on rho
        ts = sr * np.sqrt((ne - 2) / max(1e-12, 1 - sr ** 2))
        sp_eff = 2 * stats.t.sf(abs(ts), df=ne - 2)
    else:
        pp_eff = sp_eff = np.nan
    return dict(n=n, pearson_r=pr, pearson_p=pp, spearman_rho=sr, spearman_p=sp,
                n_eff=ne, pearson_p_eff=pp_eff, spearman_p_eff=sp_eff)


def detrend(series):
    """Residuals after OLS on time index (linear trend removed); NaN kept."""
    y = series.values.astype(float)
    t = np.arange(len(y), dtype=float)
    m = np.isfinite(y)
    b = np.polyfit(t[m], y[m], 1)
    res = np.full_like(y, np.nan)
    res[m] = y[m] - np.polyval(b, t[m])
    return pd.Series(res, index=series.index)


def diff(series):
    return series.diff()


def lagged(x, y, k):
    """corr(x_t, y_{t+k}). k>0: salience leads tone; k<0: tone leads salience."""
    xv = x.values.astype(float)
    yv = y.values.astype(float)
    if k > 0:
        xs, ys = xv[:-k], yv[k:]
    elif k < 0:
        xs, ys = xv[-k:], yv[:k]
    else:
        xs, ys = xv, yv
    return pair_corr(xs, ys)


def block_perm_p(x, y, n_perm=5000, block=6):
    """Circular-shift permutation null for y (preserves y autocorrelation); block arg unused."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    if n < 6:
        return np.nan
    obs = abs(stats.pearsonr(x, y)[0])
    cnt = 0
    for _ in range(n_perm):
        # circular shift of y by random offset (preserves y's autocorrelation)
        s = rng.integers(0, n)
        ys = np.roll(y, s)
        if abs(stats.pearsonr(x, ys)[0]) >= obs:
            cnt += 1
    return (cnt + 1) / (n_perm + 1)


def analyse(panel, label):
    res = {"label": label}
    x_lvl = panel["salience"]
    y_lvl = panel["tone_mean"]
    res["levels"] = pair_corr(x_lvl.values, y_lvl.values)
    # Trend strength
    tt = np.arange(len(panel), dtype=float)
    res["trend_salience_slope_per_month"] = float(np.polyfit(tt[np.isfinite(x_lvl.values)], x_lvl.values[np.isfinite(x_lvl.values)], 1)[0])
    m = np.isfinite(y_lvl.values)
    res["trend_tone_slope_per_month"] = float(np.polyfit(tt[m], y_lvl.values[m], 1)[0])
    res["acf1_salience"] = acf1(x_lvl.dropna().values)
    res["acf1_tone"] = acf1(y_lvl.dropna().values)
    res["detrended"] = pair_corr(detrend(x_lvl).values, detrend(y_lvl).values)
    res["first_diff"] = pair_corr(diff(x_lvl).values, diff(y_lvl).values)
    res["first_diff_perm_p_circular"] = block_perm_p(diff(x_lvl).values, diff(y_lvl).values, n_perm=2000)
    dx = diff(x_lvl); dy = diff(y_lvl)
    res["lag_first_diff"] = {int(k): lagged(dx, dy, k) for k in range(-MAX_LAG, MAX_LAG + 1)}
    res["lag_detrended"] = {int(k): lagged(detrend(x_lvl), detrend(y_lvl), k) for k in range(-MAX_LAG, MAX_LAG + 1)}
    return res


def fmt(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = fmt(v)
        elif isinstance(v, (np.floating, float)):
            out[k] = None if not np.isfinite(v) else round(float(v), 4)
        elif isinstance(v, (np.integer,)):
            out[k] = int(v)
        else:
            out[k] = v
    return out


if __name__ == "__main__":
    refs = pd.read_csv(REFS)
    speeches = pd.read_csv(SPEECHES)
    print("refs", refs.shape, "speeches", speeches.shape)

    results = {}
    # Primary: threshold 50, questioner passages excluded
    panel, n_q = monthly_panel(refs, speeches, PRIMARY_THR, drop_questioner=True)
    panel.to_csv(os.path.join(OUT, "monthly_panel_thr50.csv"))
    results["primary"] = analyse(panel, "thr50_no_questioner")
    results["primary"]["n_questioner_rows_flagged_in_all_refs"] = n_q
    results["primary"]["months_total"] = int(len(panel))
    results["primary"]["months_with_hi_passage"] = int((panel["n_hi"] > 0).sum())
    results["primary"]["months_with_tone_defined"] = int(panel["tone_mean"].notna().sum())
    results["primary"]["total_hi_passages"] = int(panel["n_hi"].sum())
    results["primary"]["total_speeches_ok_nondup"] = int(panel["n_speeches"].sum())
    results["primary"]["zero_speech_months"] = int((panel["n_speeches"] == 0).sum())

    # Sensitivity: thresholds 30/70 and including questioner rows
    for thr in SENS_THRS:
        p, _ = monthly_panel(refs, speeches, thr, drop_questioner=True)
        results[f"sens_thr{thr}"] = analyse(p, f"thr{thr}_no_questioner")
        p.to_csv(os.path.join(OUT, f"monthly_panel_thr{thr}.csv"))
    p, _ = monthly_panel(refs, speeches, PRIMARY_THR, drop_questioner=False)
    results["sens_thr50_with_questioner"] = analyse(p, "thr50_with_questioner")

    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump({k: fmt(v) if isinstance(v, dict) else v for k, v in
                   ((kk, vv) for kk, vv in results.items())}, f, indent=2, default=str)

    # Chart
    pr = results["primary"]
    fig, axes = plt.subplots(3, 1, figsize=(10, 9))
    idx = pd.PeriodIndex(panel.index, freq="M").to_timestamp()
    axes[0].plot(idx, panel["salience"], color="#1f4e79", lw=1.2, label="salience (hi passages per speech)")
    axes[0].set_ylabel("hi / speech")
    ax2 = axes[0].twinx()
    ax2.plot(idx, panel["tone_mean"], color="#c0504d", lw=1.0, alpha=0.8, label="mean VADER tone")
    ax2.set_ylabel("mean tone")
    axes[0].set_title("Monthly salience (>=50%) and mean VADER tone of those passages")
    axes[1].scatter(detrend(panel["salience"]), detrend(panel["tone_mean"]), s=12, color="#1f4e79")
    axes[1].set_title(f"Detrended levels: r={pr['detrended']['pearson_r']:.2f}, n={pr['detrended']['n']}")
    axes[1].set_xlabel("salience residual"); axes[1].set_ylabel("tone residual")
    lags = list(range(-MAX_LAG, MAX_LAG + 1))
    rs = [pr["lag_first_diff"][k]["pearson_r"] for k in lags]
    axes[2].bar(lags, rs, color="#7f7f7f")
    axes[2].axhline(0, color="k", lw=0.6)
    axes[2].set_title("Lagged corr of first differences (k>0: salience leads tone)")
    axes[2].set_xlabel("lag k (months)"); axes[2].set_ylabel("Pearson r")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "salience_tone.png"), dpi=130)
    print("done")


def robustness():
    """Extra checks: log-salience, drop months with few hi passages, drop top-3 salience months."""
    refs = pd.read_csv(REFS)
    speeches = pd.read_csv(SPEECHES)
    panel, _ = monthly_panel(refs, speeches, PRIMARY_THR, drop_questioner=True)
    out = {}
    lp = panel.copy()
    lp["salience"] = np.log1p(lp["salience"])
    out["log1p_salience"] = analyse(lp, "log1p")
    fewer = panel.copy()
    fewer.loc[fewer["n_hi"] < 5, "tone_mean"] = np.nan
    out["min5_hi_per_month"] = analyse(fewer, "min5")
    top = panel["salience"].nlargest(3).index
    dropped = panel.drop(index=top)
    dropped_full = panel.copy()
    dropped_full.loc[top, ["salience", "tone_mean"]] = np.nan
    out["drop_top3_salience_months"] = analyse(dropped_full, "drop_top3")
    out["dropped_months"] = list(top)
    with open(os.path.join(OUT, "robustness.json"), "w") as f:
        json.dump({k: (fmt(v) if isinstance(v, dict) else v) for k, v in out.items()}, f, indent=2, default=str)
    for k, v in out.items():
        if isinstance(v, dict):
            print(k, "levels r", v["levels"]["pearson_r"], "p", v["levels"]["pearson_p"], "| fd r", v["first_diff"]["pearson_r"], "p", v["first_diff"]["pearson_p"], "p_eff", v["first_diff"]["pearson_p_eff"], "spearman fd", v["first_diff"]["spearman_rho"], v["first_diff"]["spearman_p"], "n_fd", v["first_diff"]["n"])
    print("dropped", list(top))


def category_check():
    """Does category / speech-type mix explain salience-tone co-movement? Writes category_check.json."""
    refs = pd.read_csv(REFS)
    speeches = pd.read_csv(SPEECHES)
    r = refs[~refs["rationale"].fillna("").str.contains("questioner", case=False)].copy()
    r["month"] = r["date"].str[:7]
    hi = r[r["final_score_pct"] >= PRIMARY_THR].copy()
    panel, _ = monthly_panel(refs, speeches, PRIMARY_THR, drop_questioner=True)
    share_wd = hi.assign(w=(hi["category"] == "war_direct").astype(float)).groupby("month")["w"].mean().reindex(panel.index)
    stype = speeches[speeches["dup_of"].isna() & (speeches["status"] == "ok")].copy()
    stype["month"] = stype["date"].str[:7]
    pc = stype[stype["type"] == "press_conference"].groupby("month").size().reindex(panel.index, fill_value=0)
    share_pc = pc / panel["n_speeches"].replace(0, np.nan)
    out = {}
    for nm, ser in [("war_direct_share", share_wd), ("press_conf_share_of_speeches", share_pc)]:
        out[nm + "_vs_salience"] = pair_corr(ser.values, panel["salience"].values)
        out[nm + "_vs_tone"] = pair_corr(ser.values, panel["tone_mean"].values)
    # Passage-level: tone by category among hi passages (word valence check)
    out["tone_by_category_hi"] = hi.groupby("category")["tone"].agg(["mean", "count"]).round(4).to_dict()
    ms = {}
    for m in ["2012-05", "2013-01", "2015-03"]:
        sub = hi[hi["month"] == m]
        ms[m] = {"n_hi": int(len(sub)), "category_counts": sub["category"].value_counts().to_dict(),
                 "speech_types": stype[stype["month"] == m]["type"].value_counts().to_dict(),
                 "mean_tone": round(float(sub["tone"].mean()), 4)}
    out["spike_months"] = ms
    with open(os.path.join(OUT, "category_check.json"), "w") as f:
        json.dump(fmt({k: v for k, v in out.items() if isinstance(v, dict) and "n" in v}) | {k: v for k, v in out.items() if not (isinstance(v, dict) and "n" in v)}, f, indent=2, default=str)
    for k, v in out.items():
        if isinstance(v, dict) and "n" in v:
            print(k, "r", round(v["pearson_r"], 3), "p", round(v["pearson_p"], 4), "rho", round(v["spearman_rho"], 3), "n", v["n"])
    print("spike months", json.dumps(ms, default=str))
    print("tone by cat", out["tone_by_category_hi"])


if __name__ == "__main__":
    robustness()
    category_check()
