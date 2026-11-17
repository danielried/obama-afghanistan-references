"""Overlay of outside reaction (press, tweets) on what the President said, per key event.

Input: data/reactions.json = {"events": [{"date", "label", "items": [{"kind": "press"|"tweet", "stance", ...}]}]}
The items were gathered by web research and each was re-checked by a second pass; stance is a judgment label
(positive / negative / neutral / mixed toward the President's decision), not a measurement.
"""
import json
from datetime import date, timedelta
from pathlib import Path

WINDOW_DAYS = 14   # statements counted from the event date through this many days after
MIN_N = 3          # an event needs at least this many statements and press items to enter the correlation


def load(path):
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf8")).get("events", [])


def stance_index(items):
    """(positive - negative) / all items, in [-1, 1]; neutral and mixed count as 0. None if no items."""
    if not items:
        return None
    s = sum(1 if i.get("stance") == "positive" else -1 if i.get("stance") == "negative" else 0 for i in items)
    return round(s / len(items), 3)


def _counts(items):
    c = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}
    for i in items:
        c[i.get("stance") if i.get("stance") in c else "neutral"] += 1
    return c


def _rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
        for k in range(i, j + 1): r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    if n < 3: return None
    mx, my = sum(x) / n, sum(y) / n
    sx = sum((a - mx) ** 2 for a in x); sy = sum((b - my) ** 2 for b in y)
    if sx == 0 or sy == 0: return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) ** 0.5


def _corr(x, y):
    out = {"n": len(x), "pearson_r": None, "spearman_rho": None, "pearson_p": None, "spearman_p": None}
    r = pearson(x, y); rho = pearson(_rank(x), _rank(y)) if len(x) >= 3 else None
    out["pearson_r"] = None if r is None else round(r, 3); out["spearman_rho"] = None if rho is None else round(rho, 3)
    try:  # p-values only when scipy is installed
        from scipy import stats
        if r is not None: out["pearson_p"] = round(float(stats.pearsonr(x, y)[1]), 3)
        if rho is not None: out["spearman_p"] = round(float(stats.spearmanr(x, y)[1]), 3)
    except Exception:
        pass
    return out


def analyse(refs, events, window=WINDOW_DAYS):
    """refs need 'date', 'tone', 'tone_label', 'rationale'. Returns (rows per event, correlation dict)."""
    rows = []
    for e in sorted(events, key=lambda e: e["date"]):
        d0 = date.fromisoformat(e["date"]); d1 = (d0 + timedelta(days=window)).isoformat()
        st = [r for r in refs if r.get("date") and e["date"] <= r["date"] <= d1 and "questioner" not in (r.get("rationale") or "")]
        press = [i for i in e.get("items", []) if i.get("kind") == "press"]
        tw = [i for i in e.get("items", []) if i.get("kind") == "tweet"]
        rows.append({
            "date": e["date"], "label": e["label"], "window_end": d1, "n_statements": len(st),
            "statement_tone": round(sum(r["tone"] for r in st) / len(st), 3) if st else None,
            "statement_pos": sum(r["tone_label"] == "positive" for r in st),
            "statement_neg": sum(r["tone_label"] == "negative" for r in st),
            "n_press": len(press), "press_index": stance_index(press), "press_counts": _counts(press),
            "n_tweets": len(tw), "tweet_index": stance_index(tw), "tweet_counts": _counts(tw),
            "all_index": stance_index(press + tw), "dropped_unverified": e.get("dropped", 0), "items": e.get("items", []),
        })
    ok = [r for r in rows if r["n_statements"] >= MIN_N and r["n_press"] >= MIN_N]
    corr = {"window_days": window, "min_n": MIN_N,
            "statement_tone_vs_press_index": _corr([r["statement_tone"] for r in ok], [r["press_index"] for r in ok])}
    ok2 = [r for r in rows if r["n_statements"] >= MIN_N and (r["n_press"] + r["n_tweets"]) >= MIN_N]
    corr["statement_tone_vs_all_reaction_index"] = _corr([r["statement_tone"] for r in ok2], [r["all_index"] for r in ok2])
    return rows, corr
