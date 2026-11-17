import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
A=str(ANALYSES) + "/09_troops/"
qp=pd.read_csv(A+"quarterly_panel.csv",index_col=0)
lv=qp.dropna(subset=["troops"]).copy()
lv["t"]=np.arange(len(lv))
dt=lv.troops.diff()
dd=pd.DataFrame({"dy":lv.share_combat.diff(),"dx1":dt.shift(1),"tt":lv.t}).dropna()
print("n",len(dd))
for lab,kw in [("HAC2",dict(cov_type="HAC",cov_kwds={"maxlags":2})),("HAC1",dict(cov_type="HAC",cov_kwds={"maxlags":1})),("HC3",dict(cov_type="HC3"))]:
    m=sm.OLS(dd.dy,sm.add_constant(dd[["dx1"]])).fit(**kw)
    print(lab,"dx1 beta",round(m.params["dx1"],7),"p",round(m.pvalues["dx1"],4))
m=sm.OLS(dd.dy,sm.add_constant(dd[["dx1","tt"]])).fit(cov_type="HAC",cov_kwds={"maxlags":2})
print("with time trend: dx1 beta",round(m.params["dx1"],7),"p",round(m.pvalues["dx1"],4))
# Holm across 12 specs as reported in results.json
import json
r=json.load(open(A+"results.json"))["ols_hac_diffs"]
ps=sorted([(v["p_HAC"],k) for k,v in r.items()])
m_=len(ps); adj=[]; run=0
for i,(p,k) in enumerate(ps):
    a=min(1,(m_-i)*p); run=max(run,a); adj.append((k,p,round(run,4)))
print("Holm adjusted:"); [print(x) for x in adj[:4]]
# permutation test of the dx1 spec (n=28): shuffle dx1 blocks is naive; use plain perm for indication
rng=np.random.default_rng(0); obs=np.corrcoef(dd.dx1,dd.dy)[0,1]
perm=[np.corrcoef(rng.permutation(dd.dx1.values),dd.dy.values)[0,1] for _ in range(20000)]
print("perm p (two-sided, iid shuffle)", round(np.mean(np.abs(perm)>=abs(obs)),4), "obs r", round(obs,3))
# sensitivity: dropping 2010 H1 (ramp-up) and 2014-16 small troop periods
