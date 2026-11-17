import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import re, numpy as np, pandas as pd
from scipy import stats
REF=str(PROJECT) + "/output/references.csv"
SPI=str(PROJECT) + "/output/speeches_index.csv"
r=pd.read_csv(REF,low_memory=False)
sp=pd.read_csv(SPI)
r["dt"]=pd.to_datetime(r["date"])
r["q"]=r["rationale"].fillna("").str.contains("questioner_not_president")
C4=["war_direct","war_adjacent","aid_diplomacy_civil","incidental"]
d=r[(r.dt>="2009-01-01")&(r.dt<="2016-12-31")&r.category.isin(C4)&(~r.q)].copy()
d["per"]=np.select([d.dt.dt.year<=2011,d.dt.dt.year<=2014],["09-11","12-14"],"15-16")
END=re.compile(r"\b(?:withdraw\w*|drawdown|draw[- ]down|come home|coming home|bring\w* (?:\w+ ){0,3}home|return\w* home|troops? home|home by|end(?:s|ed|ing)? (?:of )?(?:the |our |combat |this |its |a )*(?:war|combat|mission|involvement|role|conflict|campaign))\b",re.I)
TRA=re.compile(r"\b(?:transition\w*|transfer\w*|train\w*|advis\w*|handover|hand over|hand-over|Afghan[- ]led|Afghan[- ]lead|Afghan security forces|Afghan forces)\b",re.I)
COM=re.compile(r"\b(?:combat\w*|surge\w*|fight\w*|fought|offensive\w*|insurgen\w*|battl\w*)\b",re.I)
d["end"]=d.passage.fillna("").map(lambda s: bool(END.search(s)))
d["tra"]=d.passage.fillna("").map(lambda s: bool(TRA.search(s)))
d["com"]=d.passage.fillna("").map(lambda s: bool(COM.search(s)))
d["iraq"]=d.passage.fillna("").str.contains(r"\bIraq",case=True)
print("END by period:", d.groupby("per").end.agg(['sum','size','mean']).round(3).to_dict('index'))
print("TRA by period:", d.groupby("per").tra.agg(['sum','size','mean']).round(3).to_dict('index'))
print("\n-- Iraq mentions among END hits, by year")
e=d[d.end]
print(e.groupby(e.dt.dt.year).agg(n=("end","size"),iraq=("iraq","sum")).to_string())
print("END hits with Iraq:", int(e.iraq.sum()), "of", len(e))
# end frame excluding Iraq-mentioning passages
d["end_noiraq"]=d.end & ~d.iraq
print("END excl Iraq by period:", d.groupby("per").end_noiraq.agg(['sum','size','mean']).round(3).to_dict('index'))
# speech concentration
print("\n-- speech concentration of END hits")
e=d[d.end].copy()
for lab,g in e.groupby("per"):
    vc=g.speech_id.value_counts()
    print(lab, "END hits", len(g), "distinct speeches", vc.size, "top5 share", round(vc.head(5).sum()/len(g),3), "top speeches", vc.head(3).to_dict())
m=d[d.dt.dt.to_period("M").astype(str)=="2012-05"]
print("\n2012-05 passages", len(m), "distinct speeches", m.speech_id.nunique(), "top speech share", round(m.speech_id.value_counts().iloc[0]/len(m),3))
print(m.speech_id.value_counts().head(3).to_dict())
print("speech titles of top 2012-05 speeches:")
for sid in m.speech_id.value_counts().head(3).index:
    print("  ", sid, sp.loc[sp.id.astype(str)==str(sid),"title"].values[:1])
# duplicate passages across speeches
dup=r[r.passage.duplicated(keep=False)].groupby("passage").speech_id.nunique()
print("\npassage texts repeated across >1 speech_id:", int((dup>1).sum()), "of", int(r.passage.duplicated(keep=False).sum()), "rows-with-dup-text")
d.to_pickle(str(HERE) + "/d.pkl")
