"""03_framing_shift: monthly category and lexical-frame shares, change points, comparison to announcements.
Run: .venv/bin/python -I output/analyses/03_framing_shift/analysis.py
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import os, re, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REF = str(PROJECT) + "/output/references.csv"
SPI = str(PROJECT) + "/output/speeches_index.csv"
EVT = str(PROJECT) + "/output/reaction_events.csv"
rng = np.random.default_rng(20260116)
B_PERM = 499
ALPHA = 0.05
MIN_SEG = 30          # min passages on each side of a split
CATS4 = ["war_direct", "war_adjacent", "aid_diplomacy_civil", "incidental"]

# ---- lexical frames (matched against passage text, case-insensitive) ----
FRAMES = {
    "combat": r"\b(?:combat\w*|surge\w*|fight\w*|fought|offensive\w*|insurgen\w*|battl\w*)\b",
    "transition": r"\b(?:transition\w*|transfer\w*|train\w*|advis\w*|handover|hand over|hand-over|"
                  r"Afghan[- ]led|Afghan[- ]lead|Afghan security forces|Afghan forces)\b",
    "end": r"\b(?:withdraw\w*|drawdown|draw[- ]down|come home|coming home|bring\w* (?:\w+ ){0,3}home|"
           r"return\w* home|troops? home|home by|end(?:s|ed|ing)? (?:of )?(?:the |our |combat |this |its |a )*"
           r"(?:war|combat|mission|involvement|role|conflict|campaign))\b",
}
FRAME_RX = {k: re.compile(v, re.I) for k, v in FRAMES.items()}

# ---- load ----
r = pd.read_csv(REF, low_memory=False)
sp = pd.read_csv(SPI)
dup_ids = set(sp.loc[sp.dup_of.notna() & (sp.dup_of.astype(str).str.strip() != ""), "id"].astype(str))
n_dup_drop = int(r.speech_id.isin(dup_ids).sum())
r = r[~r.speech_id.isin(dup_ids)].copy()
r["dt"] = pd.to_datetime(r["date"])
r["questioner"] = r["rationale"].fillna("").str.contains("questioner_not_president")
r["para_idx"] = r["para_idx"].astype(int)
r = r[(r.dt >= "2009-01-01") & (r.dt <= "2016-12-31")]          # 2017 partial month excluded
r = r[r.category.isin(CATS4)].copy()
for k, rx in FRAME_RX.items():
    r["frame_" + k] = r["passage"].fillna("").map(lambda s: bool(rx.search(s)))
r = r.sort_values(["dt", "speech_id", "para_idx", "char_start"], kind="mergesort").reset_index(drop=True)
r["mon"] = (r.dt.dt.year - 2009) * 12 + (r.dt.dt.month - 1)

ev = pd.read_csv(EVT)
ev["dt"] = pd.to_datetime(ev["date"])

print(f"dup-speech rows dropped: {n_dup_drop}; 4-category passages 2009-2016: {len(r)}; "
      f"questioner-flagged among them: {int(r.questioner.sum())}")
print("category counts:", r.category.value_counts().to_dict())
for k in FRAMES:
    print(f"frame {k}: n={int(r['frame_'+k].sum())} ({r['frame_'+k].mean():.3f})")

# ---- spot check frame regex on a few matches ----
rng_s = np.random.default_rng(1)
for k in FRAMES:
    hits = r[r["frame_" + k]]
    for _, row in hits.sample(min(3, len(hits)), random_state=1).iterrows():
        m = FRAME_RX[k].search(row.passage)
        print(f"  [{k}] match='{m.group(0)}' | ...{row.passage[max(0,m.start()-60):m.end()+60]!r}"[:260])

# ---- monthly table (main sample: non-questioner) ----
def monthly(df):
    g = df.groupby("mon")
    t = pd.DataFrame({"n": g.size()})
    for c in CATS4:
        t[c] = g.apply(lambda x: int((x.category == c).sum()), include_groups=False)
    for k in FRAMES:
        t["frame_" + k] = g["frame_" + k].sum().astype(int)
    t = t.reindex(range(96), fill_value=0)
    return t

def frame_table_shares(t):
    out = t.copy()
    for c in CATS4:
        out["share_" + c] = out[c] / out["n"].replace(0, np.nan)
    for k in FRAMES:
        out["share_frame_" + k] = out["frame_" + k] / out["n"].replace(0, np.nan)
    return out

main = r[~r.questioner]
tm = frame_table_shares(monthly(main))
tm.index = [f"{2009 + i // 12}-{i % 12 + 1:02d}" for i in tm.index]
tm.to_csv(os.path.join(HERE, "monthly_shares.csv"))
print("monthly n (main): min", int(tm.n.min()), "median", float(tm.n.median()), "max", int(tm.n.max()),
      "months with n<10:", int((tm.n < 10).sum()))

# ---- segmentation machinery (passage-level binary indicators, ordered by date) ----
def _f(s, n):
    s = np.asarray(s, float); n = np.asarray(n, float)
    out = np.zeros_like(s)
    a = s > 0; out[a] += s[a] * np.log(s[a] / n[a])
    b = (n - s) > 0; out[b] += (n - s)[b] * np.log((n - s)[b] / n[b])
    return out

def best_split(yy, mm):
    N = len(yy)
    if N < 2 * MIN_SEG:
        return None
    cs = np.concatenate([[0], np.cumsum(yy)])
    t = np.arange(1, N)
    sl, nl = cs[t], t
    sr, nr = cs[-1] - sl, N - t
    ok = (nl >= MIN_SEG) & (nr >= MIN_SEG) & (mm[t - 1] != mm[t])   # split only at a month boundary
    if not ok.any():
        return None
    stat = _f(sl, nl) + _f(sr, nr) - _f([cs[-1]], [N])[0]
    stat = np.where(ok, stat, -np.inf)
    j = int(np.argmax(stat))
    return float(stat[j]), int(t[j])

def binseg(y, mon, lo, hi, found, depth=0, max_depth=4):
    if depth >= max_depth:
        return
    bs = best_split(y[lo:hi], mon[lo:hi])
    if bs is None:
        return
    stat, t = bs
    null = np.empty(B_PERM)
    for b in range(B_PERM):
        null[b] = best_split(rng.permutation(y[lo:hi]), mon[lo:hi])[0]
    p = (1 + np.sum(null >= stat)) / (B_PERM + 1)
    if p <= ALPHA:
        found.append({"idx": lo + t, "lr": stat, "p": float(p), "depth": depth})
        binseg(y, mon, lo, lo + t, found, depth + 1, max_depth)
        binseg(y, mon, lo + t, hi, found, depth + 1, max_depth)

def pettitt(y):
    """Pettitt (1979) for binary x: U_t = cumsum of V_i, V_i = sum_j sign(x_i - x_j)."""
    n = len(y)
    n1 = int(y.sum()); n0 = n - n1
    V = np.where(y == 1, n0, -n1).astype(float)
    U = np.cumsum(V)
    K = np.max(np.abs(U[:-1]))
    t = int(np.argmax(np.abs(U[:-1])))   # break after index t
    p = min(1.0, 2 * np.exp(-6 * K ** 2 / (n ** 3 + n ** 2)))
    return {"t": t, "K": float(K), "p": float(p)}

def analyse(df, label):
    """df: passages ordered by date. Returns dict of breaks per series."""
    mon = df["mon"].to_numpy()
    dates = df["dt"].to_numpy()
    out = {}
    series = {("cat_" + c): (df.category == c).to_numpy().astype(int) for c in CATS4}
    series.update({("frame_" + k): df["frame_" + k].to_numpy().astype(int) for k in FRAMES})
    for name, y in series.items():
        found = []
        binseg(y, mon, 0, len(y), found)
        found.sort(key=lambda d: d["idx"])
        pt = pettitt(y)
        res = {
            "overall_rate": float(y.mean()),
            "binseg": [{"date": str(pd.Timestamp(dates[d["idx"]]).date()), "lr": round(d["lr"], 2),
                        "p_perm": round(d["p"], 4)} for d in found],
            "pettitt": {"date": str(pd.Timestamp(dates[pt["t"] + 1]).date()) if pt["t"] + 1 < len(dates) else None,
                        "K": round(pt["K"], 2), "p_approx": round(pt["p"], 6)},
            "n": int(len(y)),
        }
        out[name] = res
        print(f"[{label}] {name}: n={len(y)} rate={y.mean():.3f} | binseg="
              f"{[(b['date'], b['p_perm']) for b in res['binseg']]} | Pettitt={res['pettitt']}")
    return out

# ---- main + sensitivity ----
subsets = {
    "main_nonquestioner": main,
    "incl_questioner": r,
    "main_score_ge30": main[main.final_score_pct >= 30],
    "main_score_ge50": main[main.final_score_pct >= 50],
    "main_score_ge70": main[main.final_score_pct >= 70],
}
results = {}
for lab, df in subsets.items():
    df = df.sort_values(["dt", "speech_id", "para_idx", "char_start"], kind="mergesort").reset_index(drop=True)
    df["mon"] = (df.dt.dt.year - 2009) * 12 + (df.dt.dt.month - 1)
    results[lab] = analyse(df, lab)
    results[lab]["_n_passages"] = int(len(df))

# ---- compare breaks with announcements (main subset, pooled break dates) ----
span_start = pd.Timestamp("2009-01-20"); span_end = pd.Timestamp("2016-12-31")
main_breaks = sorted({pd.Timestamp(b["date"]) for s, v in results["main_nonquestioner"].items()
                      if isinstance(v, dict) and "binseg" in v for b in v["binseg"]})
ev_dates = list(ev.dt)
def n_within(dates, W):
    return sum(any(abs((d - e).days) <= W for e in ev_dates) for d in dates)
span_days = (span_end - span_start).days
comparison = {"n_breaks_pooled_main": len(main_breaks), "breaks": [str(d.date()) for d in main_breaks]}
for W in (30, 60):
    obs = n_within(main_breaks, W)
    K = len(main_breaks)
    sims = []
    for _ in range(10000):
        rd = [span_start + pd.Timedelta(days=int(x)) for x in rng.integers(0, span_days, K)]
        sims.append(n_within(rd, W))
    sims = np.array(sims)
    p = (1 + np.sum(sims >= obs)) / (len(sims) + 1)
    comparison[f"window_{W}d"] = {"breaks_within_window_of_an_event": int(obs), "null_mean": round(float(sims.mean()), 2),
                                  "p_mc_ge": round(float(p), 4)}
    print(f"break-event match +/-{W}d: observed {obs} of {K} breaks; null mean {sims.mean():.2f}; p={p:.4f}")
# nearest break per event
near = []
for _, e in ev.iterrows():
    if not main_breaks:
        break
    ed = e["dt"]
    d = min(main_breaks, key=lambda b: abs((b - ed).days))
    near.append({"event": str(ed.date()), "label": e.label[:70], "nearest_break": str(d.date()),
                 "days": int((d - ed).days)})
comparison["nearest_break_per_event"] = near
for x in near:
    print(f"  event {x['event']} nearest break {x['nearest_break']} ({x['days']:+d} d) | {x['label']}")

# ---- period summary (main sample) with chi-square across 3 periods ----
from scipy.stats import chi2_contingency
PERIODS = {"2009-2011": (0, 36), "2012-2014": (36, 72), "2015-2016": (72, 96)}
period_rows = []
MEASURES = [("cat_" + c, "category", c) for c in CATS4] + [("frame_" + k, "frame", k) for k in FRAMES]
for name, kind, key in MEASURES:
    row = {"measure": name}
    tab = []
    for pl, (ma, mb) in PERIODS.items():
        sub = main[(main.mon >= ma) & (main.mon < mb)]
        if kind == "category":
            k = int((sub.category == key).sum())
        else:
            k = int(sub["frame_" + key].sum())
        n = len(sub)
        row[pl] = f"{k}/{n} = {k / n:.3f}"
        tab.append([k, n - k])
    chi2, pv, _, _ = chi2_contingency(np.array(tab))
    row["chi2_p_3periods"] = float(pv)
    period_rows.append(row)
    print(f"period {name}: " + " | ".join(f"{pl} {row[pl]}" for pl in PERIODS) + f" | chi2 p={pv:.3g}")
pd.DataFrame(period_rows).to_csv(os.path.join(HERE, "period_shares.csv"), index=False)
results["period_summary"] = period_rows

# ---- chart ----
t = tm.copy()
t["war_direct_roll6"] = t["war_direct"].rolling(6, min_periods=1).sum() / t["n"].rolling(6, min_periods=1).sum()
for k in FRAMES:
    t[f"{k}_roll6"] = t["frame_" + k].rolling(6, min_periods=1).sum() / t["n"].rolling(6, min_periods=1).sum()
x = pd.to_datetime(t.index)
fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
ax = axes[0]
ax.plot(x, t["war_direct_roll6"], color="#1f4e79", lw=2, label="war_direct share (6-mo pooled)")
ax.plot(x, t["share_war_direct"], color="#1f4e79", lw=0.8, alpha=0.35, marker="o", ms=2.5, ls="none", label="monthly share")
ax.set_ylabel("share of category passages"); ax.set_ylim(0, 1); ax.legend(loc="lower left", fontsize=8, frameon=False)
ax.set_title("War-direct share of Afghanistan passages, monthly (main sample, non-questioner)", fontsize=10, loc="left")
ax = axes[1]
colors = {"combat": "#b03a2e", "transition": "#1e8449", "end": "#7d3c98"}
for k in FRAMES:
    ax.plot(x, t[f"{k}_roll6"], color=colors[k], lw=2, label=f"{k} frame (6-mo pooled)")
ax.set_ylabel("share of passages with frame"); ax.set_ylim(0, 0.6); ax.legend(loc="upper right", fontsize=8, frameon=False)
for a in axes:
    for b in main_breaks:
        a.axvline(b, color="black", lw=1.1, alpha=0.7)
    for e in ev_dates:
        a.axvline(e, color="grey", lw=0.8, ls="--", alpha=0.6)
axes[1].set_xlabel("month (solid black = detected break; dashed grey = announcement)")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "framing_shift.png"), dpi=150)

with open(os.path.join(HERE, "results.json"), "w") as f:
    json.dump({"results": results, "comparison": comparison,
               "frame_regex": FRAMES, "params": {"B_PERM": B_PERM, "ALPHA": ALPHA, "MIN_SEG": MIN_SEG}},
              f, indent=1, default=str)
print("wrote", os.path.join(HERE, "results.json"))
