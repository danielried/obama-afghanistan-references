import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json, sys
from pathlib import Path
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from scipy import stats
ROOT=Path(str(PROJECT) + "")
HERE=Path(str(ANALYSES) + "/06_reaction_lean")
si=pd.read_csv(ROOT/"output/speeches_index.csv",dtype=str,keep_default_na=False)
print("speeches",len(si),"dup_of nonempty",(si.dup_of!="").sum())
refs=pd.read_csv(ROOT/"output/references.csv",dtype=str,keep_default_na=False)
refs["tone"]=pd.to_numeric(refs.tone,errors="coerce")
dupsp=set(si[si.dup_of!=""].id)
print("refs in dup_of speeches:",refs.speech_id.isin(dupsp).sum())
dd=refs[refs.duplicated("passage",keep=False)]
print("dup passage rows",len(dd),"same speech_id pairs:",dd.groupby("passage").speech_id.nunique().eq(1).sum(),"of",dd.passage.nunique())
# dedupe by passage text
ref_d=refs[~refs.speech_id.isin(dupsp)].drop_duplicates("passage")
print("after dedupe rows",len(ref_d))
ev=pd.read_csv(HERE/"review_event_tone.csv")
events=json.loads((ROOT/"data/reactions.json").read_text())["events"]
from datetime import date,timedelta
def tone_for(df, cat_filter=None, dedupe=False):
    out={}
    for e in events:
        d0=date.fromisoformat(e["date"]); d1=(d0+timedelta(days=14)).isoformat()
        w=df[(df.date>=e["date"])&(df.date<=d1)&(df.tone.notna())]
        w=w[~w.rationale.str.contains("questioner",case=False)]
        if cat_filter: w=w[w.category.isin(cat_filter)]
        out[e["date"]]=(w.tone.mean(), len(w))
    return out
def press_index(e):
    p=[i for i in e["items"] if i["kind"]=="press"]
    s=sum(1 if i["stance"]=="positive" else -1 if i["stance"]=="negative" else 0 for i in p)
    return s/len(p) if p else None, len(p)
base=tone_for(refs)
variants={"all_refs":base,"core_cats":tone_for(refs,["war_direct","war_adjacent"]),"dedup_nonDupSpeech":tone_for(ref_d)}
for name,t in variants.items():
    xs=[];ys=[];ns=[]
    for e in events:
        tm,n=t[e["date"]]; pi,npress=press_index(e)
        if n>=3 and npress>=3:
            xs.append(tm); ys.append(pi)
    r,p=stats.pearsonr(xs,ys); rho,pr=stats.spearmanr(xs,ys)
    print(f"{name}: n_events={len(xs)} r={r:.3f} p={p:.3f} rho={rho:.3f} p={pr:.3f}")
# item-level: lean composition by event
rows=[]
for e in events:
    for it in e["items"]:
        rows.append({"date":e["date"],"kind":it["kind"],"lean":it.get("political_lean") or "missing","stance":it["stance"]})
it=pd.DataFrame(rows)
print(pd.crosstab(it.date,it.lean).to_string())
it.to_csv(HERE/"review_items.csv",index=False)
