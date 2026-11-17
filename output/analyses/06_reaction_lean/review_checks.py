import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import json
from pathlib import Path
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
ROOT=Path(str(PROJECT) + "")
refs=pd.read_csv(ROOT/"output/references.csv",dtype=str,keep_default_na=False)
print("rows",len(refs),"unique ref_id",refs.ref_id.nunique(),"unique passage",refs.passage.nunique())
print("category counts:\n",refs.category.value_counts().to_string())
print("rationale questioner flags:",refs.rationale.str.contains("questioner",case=False).sum())
refs["tone"]=pd.to_numeric(refs.tone,errors="coerce")
print("tone missing:",refs.tone.isna().sum())
d=json.loads((ROOT/"data/reactions.json").read_text())
events=d["events"]
from datetime import date,timedelta
rows=[]
for e in events:
    d0=date.fromisoformat(e["date"]); d1=(d0+timedelta(days=14)).isoformat()
    w=refs[(refs.date>=e["date"])&(refs.date<=d1)&(refs.tone.notna())]
    nq=w[~w.rationale.str.contains("questioner",case=False)]
    core=nq[nq.category.isin(["war_direct","war_adjacent"])]
    rows.append({"date":e["date"],"n_all":len(w),"n_noq":len(nq),"tone_noq":nq.tone.mean(),"n_core":len(core),"tone_core":core.tone.mean() if len(core) else np.nan,"n_speech_ids":nq.speech_id.nunique()})
ev=pd.DataFrame(rows); print(ev.to_string())
ev.to_csv(str(ANALYSES) + "/06_reaction_lean/review_event_tone.csv",index=False)
