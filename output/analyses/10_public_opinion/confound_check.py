"""Time-trend confound check for analysis.py outputs. Run with -I."""
import os
import numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
rows = []
for thr in (30, 50, 70):
    d = pd.read_csv(os.path.join(OUT, f"mistake_windows_thr{thr}.csv"), parse_dates=["t"])
    t_days = (d.t - pd.Timestamp("2009-01-20")).dt.days.values.astype(float)
    y = d.value.values.astype(float)
    r_t, p_t = stats.spearmanr(y, t_days)
    rows.append(dict(thr=thr, check="opinion vs days since inauguration", n=len(d), rho=round(r_t, 3), p=round(p_t, 4)))
    for m in ("pre_n_hi", "pre_hi_per_100_speeches", "post_n_hi"):
        x = d[m].values.astype(float)
        r_x, p_x = stats.spearmanr(x, t_days)
        # partial Spearman of opinion vs metric controlling for time: correlate rank residuals
        ry, rx, rt = stats.rankdata(y), stats.rankdata(x), stats.rankdata(t_days)
        def resid(a, b):
            A = np.column_stack([np.ones_like(b), b]); beta = np.linalg.lstsq(A, a, rcond=None)[0]
            return a - A @ beta
        ex, ey = resid(rx, rt), resid(ry, rt)
        pr = np.corrcoef(ex, ey)[0, 1]
        dfree = len(d) - 3
        tstat = pr * np.sqrt(dfree / max(1e-12, 1 - pr**2))
        p_partial = 2 * stats.t.sf(abs(tstat), dfree)
        rows.append(dict(thr=thr, check=f"{m} vs time", n=len(d), rho=round(r_x, 3), p=round(p_x, 4)))
        rows.append(dict(thr=thr, check=f"partial rho opinion~{m} | time", n=len(d), rho=round(pr, 3), p=round(p_partial, 4)))
out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv(os.path.join(OUT, "confound_time_check.csv"), index=False)
