"""Reviewer independent checks for 04_iraq_pairing (does not modify analyst files)."""
import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import re
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
SRC=str(PROJECT) + "/output/references.csv"
IDX=str(PROJECT) + "/output/speeches_index.csv"
df=pd.read_csv(SRC,dtype={"speech_id":str})
for c in ["passage","context_before","context_after","rationale","matched_terms","category","tone_label"]:
    df[c]=df[c].fillna("")
print("matched_terms examples:", df.matched_terms.head(3).tolist())
df=df[~df.rationale.str.contains("questioner_not_president")].copy()
idx=pd.read_csv(IDX,dtype=str)
print("index dup_of non-empty:", int((idx.dup_of.fillna("").str.strip()!="").sum()))
df["date"]=pd.to_datetime(df.date); df["post"]=df.date>=pd.Timestamp("2011-12-18")
win=(df.passage+" "+df.context_before+" "+df.context_after).str.lower()
df["pair"]=win.str.contains(r"\biraq") & win.str.contains("afghan")
camp=r"Campaign|Fundraiser|Debate|Victory Fund|Convention"
df["camp"]=df.speech_title.str.contains(camp,case=False)
cue=df.matched_terms.str.contains(r"two wars|Iraq and Afghanistan|wars in Iraq",case=False)
print("cue rows",int(cue.sum()),"paired among cue rows",int((cue&df.pair).sum()))
# 1. Speech-level pre/post: aggregate per speech, compare speech paired share (speech as unit)
sp=df.groupby(["speech_id","post"]).agg(n=("pair","size"),k=("pair","sum")).reset_index()
# 2. cluster bootstrap of pre-post difference by speech
rng=np.random.default_rng(0)
sids=df.speech_id.unique(); grp={s:g for s,g in df.groupby("speech_id")}
diffs=[]
for b in range(2000):
    pick=rng.choice(sids,len(sids),replace=True)
    g=pd.concat([grp[s] for s in pick])
    pre=g[~g.post].pair.mean(); post=g[g.post].pair.mean()
    diffs.append(100*(post-pre))
d0=100*(df[df.post].pair.mean()-df[~df.post].pair.mean())
print(f"overall post-pre diff {d0:.2f} pts; cluster-bootstrap 95% CI {np.percentile(diffs,2.5):.2f} to {np.percentile(diffs,97.5):.2f}; share of boot diffs<=0: {np.mean(np.array(diffs)<=0):.3f}")
# 3. non-cue rows only, clustered logit with post + campaign + time
d=df[~cue].copy()
X=pd.DataFrame({"const":1.0,"post":d.post.astype(float),"camp":d.camp.astype(float),
                "t":(d.date-pd.Timestamp("2009-01-20")).dt.days/365.25})
g=pd.factorize(d.speech_id)[0]
m=sm.Logit(d.pair.astype(float),X).fit(disp=0,cov_type="cluster",cov_kwds={"groups":g})
print("non-cue logit post OR %.3f p=%.4f ; camp OR %.3f ; t OR %.3f" % (np.exp(m.params.post),m.pvalues.post,np.exp(m.params.camp),np.exp(m.params.t)))
print("non-cue pre/post share", round(100*d[~d.post].pair.mean(),2), round(100*d[d.post].pair.mean(),2), "n", len(d))
# 4. full data logit with speech-type fixed effects
idxs=idx[["id","type"]].rename(columns={"id":"speech_id"})
d2=df.merge(idxs,on="speech_id",how="left")
d2["type"]=d2["type"].fillna("NA")
T=pd.get_dummies(d2["type"],drop_first=True,dtype=float)
X2=pd.concat([pd.DataFrame({"const":1.0,"post":d2.post.astype(float),"camp":d2.camp.astype(float),
    "t":(d2.date-pd.Timestamp("2009-01-20")).dt.days/365.25},index=d2.index),T],axis=1)
m2=sm.Logit(d2.pair.astype(float),X2).fit(disp=0,cov_type="cluster",cov_kwds={"groups":pd.factorize(d2.speech_id)[0]})
print("with type FE: post OR %.3f p=%.4f; camp OR %.3f" % (np.exp(m2.params.post),m2.pvalues.post,np.exp(m2.params.camp)))
print(d2.groupby(["type"]).pair.agg(["mean","size"]).round(3).to_string())
# 5. tone: paired vs unpaired, stratified by Iraq-in-passage
d["iraq_pass"]=d.passage.str.lower().str.contains(r"\biraq")
for lab,s in [("iraq in passage",d[d.iraq_pass]),("iraq only in context",d[~d.iraq_pass])]:
    a=s[s.pair].tone; b=s[~s.pair].tone
    print(lab, "paired n",len(a),"mean",round(a.mean(),3),"| unpaired n",len(b),"mean",round(b.mean(),3),"MWU p",stats.mannwhitneyu(a,b).pvalue if len(a)>2 and len(b)>2 else None)
