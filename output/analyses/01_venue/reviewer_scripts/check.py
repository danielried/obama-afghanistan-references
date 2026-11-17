import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import csv, sqlite3, re, sys
from collections import Counter, defaultdict
import statistics as st
ROOT=str(PROJECT) + ""
# independent parse with csv module (multi-line fields)
csv.field_size_limit(10**9)
with open(f"{ROOT}/output/references.csv", newline="", encoding="utf-8") as fh:
    rd = csv.DictReader(fh); rows = list(rd)
print("csv module rows:", len(rows))
with open(f"{ROOT}/output/speeches_index.csv", newline="", encoding="utf-8") as fh:
    idx = list(csv.DictReader(fh))
print("index rows:", len(idx), "dup_of nonempty:", sum(1 for r in idx if (r["dup_of"] or "").strip()))
types = {r["id"]: r["type"] for r in idx}
eras = {r["id"]: r["era"] for r in idx}
hits = {r["id"]: int(r["hit_count"] or 0) for r in idx}
# final == rule check
diff = sum(1 for r in rows if r["llm_score"].strip()=="" and abs(float(r["final_score_pct"])-round(float(r["rule_score"])))>0.51)
print("rows where final != round(rule) (no llm):", diff, " llm_score nonblank:", sum(1 for r in rows if r["llm_score"].strip()))
# speech-level hit_count vs refs count
cnt = Counter(r["speech_id"] for r in rows)
mism = sum(1 for sid,c in cnt.items() if hits.get(sid)!=c)
print("speeches where index hit_count != refs count:", mism, "of", len(cnt))
# group medians/hi share by type (not split), independent
by = defaultdict(list)
for r in rows:
    by[types[r["speech_id"]]].append(float(r["final_score_pct"]))
for t,v in sorted(by.items(), key=lambda x:-len(x[1])):
    print(f"type={t:18s} n={len(v):5d} median={st.median(v):6.1f} hi50={sum(x>=50 for x in v)/len(v):.3f}")
# era distribution per type (passage level)
print("\nera x type (passages):")
ct = defaultdict(Counter)
for r in rows: ct[types[r["speech_id"]]][eras[r["speech_id"]]] += 1
erasall = sorted({e for c in ct.values() for e in c})
print("type".ljust(18), erasall)
for t in ct: print(t.ljust(18), [ct[t].get(e,0) for e in erasall])
# speech-level: passages per speech by type and hit_count
print("\nhit_count quantiles by type (speeches with hits>0):")
for t in ["remarks","press_conference","statement","address","weekly_address","interview","other"]:
    h = [hits[s] for s in hits if types[s]==t and hits[s]>0]
    if h: print(t, len(h), "median hits", st.median(h), "max", max(h))
# concentration: top speeches share of passages per type
print("\ntop-3 speeches share of passages per type:")
for t in ["remarks","press_conference","statement","address","weekly_address","interview","other"]:
    c = Counter({s:n for s,n in cnt.items() if types.get(s)==t})
    tot = sum(c.values())
    if tot: print(t, tot, [ (r_title, n) for r_title,n in []], round(sum(n for _,n in c.most_common(3))/tot,3), c.most_common(3))
