import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy import stats
HERE=Path(str(ANALYSES) + "/06_reaction_lean")
it=pd.read_csv(HERE/"review_items.csv",dtype=str,keep_default_na=False)
ev=pd.read_csv(HERE/"review_event_tone.csv",dtype={"date":str})
it=it[it.lean!="missing"].copy()
it["y"]=it.stance.map({"positive":1,"negative":-1,"neutral":0,"mixed":0}).astype(float)
it=it.merge(ev[["date","tone_noq"]].rename(columns={"tone_noq":"tone"}),on="date")
it["lean"]=pd.Categorical(it.lean,categories=["center","left","international","unknown","right"])
it["event"]=it.date
print("n",len(it))
# A: event FE with lean dummies (within-event lean contrast); cluster by event
m_fe=smf.ols("y ~ C(lean) + C(event)",data=it).fit(cov_type="cluster",cov_kwds={"groups":pd.factorize(it.event)[0]})
print("A event-FE lean (cluster):")
for k in m_fe.params.index:
    if "lean" in k: print(f"  {k} b={m_fe.params[k]:+.3f} se={m_fe.bse[k]:.3f} p={m_fe.pvalues[k]:.3f}")
# restrict to events with >=2 lean groups represented
multi=it.groupby("event").lean.nunique(); keep=multi[multi>=2].index
sub=it[it.event.isin(keep)]
print("events with >=2 lean groups:",len(keep),"items",len(sub))
m_fe2=smf.ols("y ~ C(lean, Treatment('center')) + C(event)",data=sub).fit()
print("B event-FE within multi-lean events (classical OLS):")
for k in m_fe2.params.index:
    if "lean" in k: print(f"  {k} b={m_fe2.params[k]:+.3f} p={m_fe2.pvalues[k]:.3f}")
# C: left vs center within-event count of items & stance
print(pd.crosstab(sub.lean,sub.y).to_string())
# D: interaction tone x lean (does tone slope differ by lean?), cluster by event
m_int=smf.ols("y ~ tone * C(lean, Treatment('center'))",data=it).fit(cov_type="cluster",cov_kwds={"groups":pd.factorize(it.event)[0]})
print("D tone x lean interaction (cluster):")
for k in m_int.params.index:
    if ":" in k or k=="tone": print(f"  {k} b={m_int.params[k]:+.3f} se={m_int.bse[k]:.3f} p={m_int.pvalues[k]:.3f}")
# E: wald joint test of interactions
names=[k for k in m_int.params.index if ":" in k]
R=np.zeros((len(names),len(m_int.params)))
for i,n in enumerate(names): R[i,list(m_int.params.index).index(n)]=1
w=m_int.wald_test(R,scalar=True); print("E joint interaction Wald p=",round(float(w.pvalue),3), "df",len(names))
# F: event-level: fraction of lean items with stance negative by event (left vs center), ignoring
# G: permutation of event tone across events, leaving lean structure -> how often |r| as large in left-subset
