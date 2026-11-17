import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json
from pathlib import Path
import pandas as pd, numpy as np
from scipy import stats
P = Path(str(PROJECT) + "")
d = json.loads((P/"data/reactions.json").read_text(encoding="utf8"))["events"]
rows=[]
for e in d:
    for i in e["items"]:
        rows.append(dict(event=e["date"], item_type=i["item_type"], stance=i["stance"], lean=i.get("political_lean"),
                         outlet=i.get("outlet_or_author"), idate=i.get("date"), url=i.get("url"), kind=i.get("kind")))
it = pd.DataFrame(rows)
print("kinds:", it.kind.value_counts().to_dict())
it["group"]=np.where(it.item_type=="news_report","news",np.where(it.item_type.isin(["opinion","editorial","analysis"]),"opinion",it.item_type))
print("\nlean x group (main groups):")
print(pd.crosstab(it[it.group.isin(["news","opinion"])].group, it[it.group.isin(["news","opinion"])].lean))
print("\nstance x lean (opinion only):")
print(pd.crosstab(it[it.group=="opinion"].lean, it[it.group=="opinion"].stance))
print("\nstance x lean (news only):")
print(pd.crosstab(it[it.group=="news"].lean, it[it.group=="news"].stance))
# date window check
ev=pd.DataFrame([dict(event=e["date"]) for e in d])
it["idate"]=pd.to_datetime(it.idate, errors="coerce")
it["ed"]=pd.to_datetime(it.event)
it["lag"]=(it.idate-it.ed).dt.days
print("\nitem lag days: min", it.lag.min(), "max", it.lag.max(), "missing", it.lag.isna().sum())
print("items with lag outside 0..14:", int(((it.lag<0)|(it.lag>14)).sum()))
print("\nduplicate URLs:", int(it.url.duplicated(keep=False).sum()))
print("duplicate outlet+event:", int(it.duplicated(["event","outlet"],keep=False).sum()))
# recompute event indices (news, opinion) and tone from reaction_events.csv
ev_csv=pd.read_csv(P/"output/reaction_events.csv")
print("\nreaction_events.csv cols:", list(ev_csv.columns)[:20])
smap={"positive":1,"negative":-1,"neutral":0,"mixed":0}
it["s"]=it.stance.map(smap)
rows=[]
tone=dict(zip(ev_csv.date, ev_csv.statement_tone))
for e_,g in it.groupby("event"):
    n=g[g.group=="news"]; o=g[g.group=="opinion"]
    rows.append(dict(event=e_, tone=tone[e_], n_news=len(n), news_idx=n.s.mean() if len(n) else np.nan,
                     n_op=len(o), op_idx=o.s.mean() if len(o) else np.nan))
ev2=pd.DataFrame(rows)
print(ev2.round(3).to_string(index=False))
m=ev2.dropna(subset=["news_idx"])
r,p=stats.pearsonr(m.tone,m.news_idx); print(f"\nnews r all {len(m)} events: r={r:.3f} p={p:.4f}")
for drop in m.event:
    mm=m[m.event!=drop]; rr,pp=stats.pearsonr(mm.tone,mm.news_idx)
    print(f"  drop {drop}: r={rr:.3f} p={pp:.4f}")
mm=m[m.n_news>=2]; rr,pp=stats.pearsonr(mm.tone,mm.news_idx); print(f"news n>=2 ({len(mm)}): r={rr:.3f} p={pp:.4f}")
# spearman
rho,ps=stats.spearmanr(m.tone,m.news_idx); print(f"spearman news: {rho:.3f} p={ps:.4f}")
# weighted by item count: item-level tone-stance pooled corr
