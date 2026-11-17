"""06_reaction_lean: statement tone vs press reaction, split by outlet political lean.

Read-only on the project root. Reuses src/obama_afghan/reactions.py (analyse, stance_index, _corr).
Run: .venv/bin/python -I output/analyses/06_reaction_lean/analysis.py
"""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import importlib.util, json, sys, warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

warnings.filterwarnings("ignore")
ROOT = Path(str(PROJECT) + "")
OUT = Path(__file__).resolve().parent
RES = {}

# ---- reuse project logic ----
spec = importlib.util.spec_from_file_location("reactions", ROOT / "src/obama_afghan/reactions.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)

refs = pd.read_csv(ROOT / "output/references.csv", dtype=str, keep_default_na=False)
refs["tone"] = pd.to_numeric(refs["tone"], errors="coerce")
refs = refs.dropna(subset=["tone"])
refs_list = refs[["date", "tone", "tone_label", "rationale"]].to_dict("records")
events = R.load(ROOT / "data/reactions.json")
rows, corr_all = R.analyse(refs_list, events)
print(f"refs with tone: {len(refs_list)}  events: {len(events)}")

# validate reuse against shipped outputs
ev_csv = pd.read_csv(ROOT / "output/reaction_events.csv")
shipped = json.loads((ROOT / "output/reaction_correlation.json").read_text())
mine = pd.DataFrame(rows)
chk = ev_csv.merge(mine, on="date", suffixes=("_shipped", "_recalc"))
tone_diff = (chk["statement_tone_shipped"] - chk["statement_tone_recalc"]).abs().max()
n_diff = (chk["n_statements_shipped"] - chk["n_statements_recalc"]).abs().max()
print(f"reproduction check: max |statement_tone diff| = {tone_diff:.6f}, max |n_statements diff| = {n_diff}")
print("shipped overall press corr:", shipped["statement_tone_vs_press_index"])
print("recalc  overall press corr:", corr_all["statement_tone_vs_press_index"])
RES["reproduction"] = {"max_tone_diff": float(tone_diff), "max_n_diff": float(n_diff),
                       "overall_press_recalc": corr_all["statement_tone_vs_press_index"],
                       "overall_press_shipped": shipped["statement_tone_vs_press_index"]}

# ---- items ----
tone_by_date = {r["date"]: r["statement_tone"] for r in rows}
nst_by_date = {r["date"]: r["n_statements"] for r in rows}
recs = []
for e in events:
    for it in e["items"]:
        recs.append({"event_date": e["date"], "kind": it.get("kind"), "stance": it.get("stance"),
                     "lean": it.get("political_lean") or "missing", "weak": bool(it.get("weak_evidence")),
                     "item_type": it.get("item_type"), "outlet": it.get("outlet_or_author")})
items = pd.DataFrame(recs)
items["tone"] = items["event_date"].map(tone_by_date)
items["stance_num"] = items["stance"].map({"positive": 1, "negative": -1, "neutral": 0, "mixed": 0})
print("\nitems:", len(items), "| lean counts:\n", items.groupby(["lean", "kind"]).size().to_string())
miss = items[items.lean == "missing"]
RES["missing_lean"] = {"n": int(len(miss)), "events": sorted(miss.event_date.unique().tolist()),
                       "events_fully_missing": sorted(set(miss.event_date) - set(items[items.lean != "missing"].event_date))}
print("missing lean n:", len(miss), "events:", RES["missing_lean"]["events"])
print("events with no lean at all:", RES["missing_lean"]["events_fully_missing"])

# ---- 1. statement tone vs lean-specific press index ----
LEANS = ["left", "center", "right", "international", "unknown"]
ev_dates = sorted(tone_by_date)
split_rows = []
def lean_split(min_items, kind_filter="press"):
    out = {}
    for L in LEANS:
        sub = items[(items.lean == L) & (items.kind == kind_filter)] if kind_filter else items[items.lean == L]
        xs, ys, evs = [], [], []
        for d in ev_dates:
            if nst_by_date[d] < R.MIN_N: continue
            g = sub[sub.event_date == d]
            if len(g) < min_items: continue
            xs.append(tone_by_date[d]); ys.append(R.stance_index(g.to_dict("records"))); evs.append(d)
        c = R._corr(xs, ys) if len(xs) >= 3 else {"n": len(xs), "pearson_r": None, "spearman_rho": None, "pearson_p": None, "spearman_p": None}
        out[L] = {**c, "n_items": int(len(sub)), "events": evs}
    return out

split_main = lean_split(min_items=1)
split_min2 = lean_split(min_items=2)
split_all_kinds = lean_split(min_items=1, kind_filter=None)
RES["split_press_min1"] = split_main
RES["split_press_min2"] = split_min2
RES["split_all_kinds_min1"] = split_all_kinds
for name, d in [("press, >=1 item/event", split_main), ("press, >=2 items/event", split_min2), ("press+tweet, >=1", split_all_kinds)]:
    print(f"\n== {name} ==")
    for L in LEANS:
        c = d[L]
        print(f"{L:14s} items={c['n_items']:3d} n_events={c['n']:2d} r={c['pearson_r']} p={c['pearson_p']} rho={c['spearman_rho']} p={c['spearman_p']}")

# ---- 2. item-level model: stance ~ tone + lean ----
known = items[items.lean != "missing"].copy()
def fit_models(df, label):
    df = df.copy()
    cats = ["center"] + sorted(set(df["lean"]) - {"center"})
    lean_cat = pd.Categorical(df["lean"], categories=cats)
    assert not pd.isna(lean_cat).any(), "lean value outside categories"
    dummies = pd.get_dummies(lean_cat, drop_first=True, dtype=float)
    dummies.columns = [f"lean_{c}" for c in dummies.columns]
    X = pd.concat([df[["tone"]].reset_index(drop=True), dummies.reset_index(drop=True)], axis=1)
    X = X.astype(float)
    y = df["stance_num"].reset_index(drop=True).astype(float)
    groups = df["event_date"].reset_index(drop=True)
    n_clusters = groups.nunique()
    res = {"label": label, "n_items": int(len(df)), "n_clusters": int(n_clusters), "n_per_lean": df.lean.value_counts().to_dict()}
    # OLS, event-clustered SE
    Xc = sm.add_constant(X, has_constant="add")
    ols = sm.OLS(y, Xc).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(groups)[0]})
    res["ols_cluster"] = {k: {"coef": float(ols.params[k]), "se": float(ols.bse[k]), "p": float(ols.pvalues[k])} for k in ols.params.index}
    res["ols_cluster"]["_r2"] = float(ols.rsquared)
    ols_hc = sm.OLS(y, Xc).fit(cov_type="HC1")
    res["ols_hc1"] = {k: {"coef": float(ols_hc.params[k]), "se": float(ols_hc.bse[k]), "p": float(ols_hc.pvalues[k])} for k in ols_hc.params.index}
    # ordinal logit (no constant; thresholds estimated)
    yo = pd.Categorical(y.map({-1.0: "neg", 0.0: "zero", 1.0: "pos"}).astype(object), categories=["neg", "zero", "pos"], ordered=True)
    try:
        yn = (y.to_numpy() + 1).astype(int); Xn = X.to_numpy(dtype=float)
        om = OrderedModel(yn, Xn, distr="logit").fit(method="bfgs", disp=False, maxiter=2000)
        res["ordlogit_model"] = {k: {"coef": float(om.params[i]), "se": float(om.bse[i]), "p": float(om.pvalues[i])} for i, k in enumerate(X.columns)}
        try:
            omc = OrderedModel(yn, Xn, distr="logit").fit(method="bfgs", disp=False, maxiter=2000,
                                                          cov_type="cluster", cov_kwds={"groups": pd.factorize(groups)[0]})
            res["ordlogit_cluster"] = {k: {"coef": float(omc.params[i]), "se": float(omc.bse[i]), "p": float(omc.pvalues[i])} for i, k in enumerate(X.columns)}
        except Exception as ex:
            res["ordlogit_cluster"] = f"failed: {ex}"
    except Exception as ex:
        res["ordlogit_model"] = f"failed: {ex}"
    return res

m_main = fit_models(known, "known lean only (mixed=0)")
m_weak = fit_models(known[~known.weak], "known lean, excl weak_evidence")
m_missing = fit_models(items.assign(lean=items.lean.replace("missing", "missing")), "all 92 incl missing lean as category")
RES["models"] = {"main": m_main, "excl_weak": m_weak, "with_missing": m_missing}
for m in [m_main, m_weak]:
    print(f"\n== {m['label']} n={m['n_items']} clusters={m['n_clusters']} ==")
    print("n per lean:", m["n_per_lean"])
    for k, v in m["ols_cluster"].items():
        if k.startswith("_"): continue
        print(f"OLS-cluster {k:22s} b={v['coef']:+.3f} se={v['se']:.3f} p={v['p']:.3f}")
    for kk in ["ordlogit_model", "ordlogit_cluster"]:
        if isinstance(m.get(kk), dict):
            for k, v in m[kk].items():
                print(f"{kk} {k:22s} b={v['coef']:+.3f} se={v['se']:.3f} p={v['p']:.3f}")
        else:
            print(kk, m.get(kk))

# ---- 3. descriptive cell table ----
cells = items.groupby(["lean", "stance"]).size().unstack(fill_value=0)
RES["lean_stance_counts"] = {l: cells.loc[l].to_dict() for l in cells.index}
print("\nlean x stance:\n", cells.to_string())
RES["overall_press_index_split_check"] = None

(OUT / "results.json").write_text(json.dumps(RES, indent=2, default=str))

# ---- chart: lean-specific r with CI-free dot plot, n events labelled ----
fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=150)
labels, rs, ns, ps = [], [], [], []
for L in LEANS:
    c = split_main[L]
    labels.append(f"{L}\n(items={c['n_items']}, events={c['n']})")
    rs.append(c["pearson_r"] if c["pearson_r"] is not None else np.nan)
    ps.append(c["pearson_p"])
ys = np.arange(len(LEANS))[::-1]
ax.axvline(0, color="#999999", lw=0.8)
ax.axvline(corr_all["statement_tone_vs_press_index"]["pearson_r"], color="#444444", lw=0.8, ls="--")
ax.scatter(rs, ys, s=60, color="#2b6cb0", zorder=3)
for x, y, p in zip(rs, ys, ps):
    if not np.isnan(x):
        ax.annotate(f"r={x:.2f}" + (f", p={p:.2f}" if p is not None else ""), (x, y), xytext=(8, 0),
                    textcoords="offset points", va="center", fontsize=8, color="#222222")
ax.set_yticks(ys); ax.set_yticklabels(labels, fontsize=8)
ax.set_xlim(-1.05, 1.05)
ax.set_xlabel("Pearson r: statement tone vs lean-specific press index (events)", fontsize=8)
ax.set_title("Statement tone vs press reaction, by outlet lean\n(dashed = all-press r=%.2f; descriptive, cells tiny)" %
             corr_all["statement_tone_vs_press_index"]["pearson_r"], fontsize=9, loc="left")
ax.grid(axis="x", color="#eeeeee", lw=0.6); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "lean_split_correlation.png")
print("\nwrote", OUT / "results.json", "and chart")
