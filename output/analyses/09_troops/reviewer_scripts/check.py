import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import re, numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
A=str(ANALYSES) + "/09_troops/"
qp=pd.read_csv(A+"quarterly_panel.csv",index_col=0)
lv=qp.dropna(subset=["troops"]).copy()
lv["t"]=np.arange(len(lv))
print("n quarters", len(lv), lv.index[0], lv.index[-1])
# (a) level correlations vs time trend: partial r controlling for linear time
def partial(x,y,z):
    X=sm.add_constant(np.column_stack([z]))
    rx=sm.OLS(x,X).fit().resid; ry=sm.OLS(y,X).fit().resid
    r,p=stats.pearsonr(rx,ry); return round(r,3), round(p,4)
tr=lv.t.values.astype(float)
for y in ["share_combat","n_hl","n_all"]:
    print("partial r troops~",y,"| time:",partial(lv.troops.values.astype(float), lv[y].values.astype(float), tr))
# troop residual on time as alt regressor
print("time vs troops r", stats.pearsonr(tr, lv.troops.values))
print("time vs combat r", stats.pearsonr(tr, lv.share_combat.values))
# (b) surge confound: HL passages by quarter containing 'surge'
refs=pd.read_csv(str(PROJECT) + "/output/references.csv", dtype={"ref_id":str})
refs["questioner"]=refs.rationale.fillna("").str.contains("questioner",case=False)
refs["date"]=pd.to_datetime(refs.date); refs["period"]=refs.date.dt.year.astype(str)+"Q"+refs.date.dt.quarter.astype(str)
txt=(refs.passage.fillna("")+" "+refs.context_before.fillna("")+" "+refs.context_after.fillna("")).str.lower()
hl=refs[(refs.final_score_pct>=50)&(~refs.questioner)].copy()
ht=txt[hl.index]
for w in ["surge","offensive","killed","train","exit","withdraw","taliban"]:
    hl["has_"+w]=ht.str.contains(r"\b"+w).values
print("HL n", len(hl))
print(hl[[c for c in hl.columns if c.startswith("has_")]].mean().round(3).to_dict())
combat_pat=r"\b(combat\w*|fight\w*|battle\w*|offensive\w*|surge\w*|insurgen\w*|taliban|al[- ]qaeda|militant\w*|casualt\w*|killed|enem\w*|attack\w*|firefight\w*)\b"
hl["combat"]=ht.str.contains(combat_pat,regex=True).values
hl["combat_nosurge"]=ht.str.contains(combat_pat.replace("surge\\w*|",""),regex=True).values
g=hl.groupby("period")
s=pd.DataFrame({"cmb":g.combat.mean(),"cmb_ns":g.combat_nosurge.mean(),"surge":g.has_surge.mean(),"n":g.size()})
s=s.join(lv[["troops"]],how="inner")
print("level r combat (all):",stats.pearsonr(s.troops,s.cmb)[0].round(3), stats.pearsonr(s.troops,s.cmb)[1].round(4))
print("level r combat (no surge term):",stats.pearsonr(s.troops,s.cmb_ns)[0].round(3), stats.pearsonr(s.troops,s.cmb_ns)[1].round(4))
print("level r surge share vs troops:",stats.pearsonr(s.troops,s.surge)[0].round(3), stats.pearsonr(s.troops,s.surge)[1].round(4))
print(s.round(3).to_string())
