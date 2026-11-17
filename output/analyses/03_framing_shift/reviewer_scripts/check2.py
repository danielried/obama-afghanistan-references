import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import re, numpy as np, pandas as pd
from scipy.stats import chi2_contingency
d=pd.read_pickle(str(HERE) + "/d.pkl")
rng=np.random.default_rng(7)
def tab(col, df):
    t=[[int(df[df.per==p][col].sum()), int((df.per==p).sum()-df[df.per==p][col].sum())] for p in ["09-11","12-14","15-16"]]
    return chi2_contingency(np.array(t))[1]
def shares(col, df): return df.groupby("per")[col].mean().round(3).to_dict()
print("END all      ", shares("end",d), "p=%.3g"%tab("end",d))
print("END excl Iraq", shares("end_noiraq",d), "p=%.3g"%tab("end_noiraq",d))
# speech-cluster bootstrap of 12-14 minus 09-11 difference
spk=d.speech_id.unique()
grp={s:g for s,g in d.groupby("speech_id")}
def boot(col, B=2000):
    diffs=[]
    for _ in range(B):
        pick=rng.choice(spk,len(spk),replace=True)
        b=pd.concat([grp[s] for s in pick])
        a=b[b.per=="12-14"][col].mean(); c=b[b.per=="09-11"][col].mean()
        diffs.append(a-c)
    diffs=np.array(diffs)
    obs=d[d.per=="12-14"][col].mean()-d[d.per=="09-11"][col].mean()
    return round(obs,4), np.round(np.percentile(diffs,[2.5,97.5]),4).tolist()
print("cluster-boot diff 12-14 minus 09-11, END all:", boot("end"))
print("cluster-boot diff 12-14 minus 09-11, END excl Iraq:", boot("end_noiraq"))
print("cluster-boot diff 12-14 minus 09-11, TRA:", boot("tra"))
print("cluster-boot diff 12-14 minus 09-11, war_direct:", boot(None) if False else "")
d["wd"]=d.category.eq("war_direct")
print("cluster-boot diff 12-14 minus 09-11, war_direct:", boot("wd"))
# dedupe repeated passage text (keep first)
dd=d.drop_duplicates(subset=["passage"],keep="first")
print("\nDEDUPED passage text n:", len(dd), "from", len(d))
print("END dedup", shares("end",dd), "p=%.3g"%tab("end",dd))
print("TRA dedup", shares("tra",dd), "p=%.3g"%tab("tra",dd))
print("war_direct dedup", shares("wd",dd), "p=%.3g"%tab("wd",dd))
# transition term breakdown
TRA_TERMS={"transition":r"transition\w*","transfer":r"transfer\w*","train":r"train\w*","advis":r"advis\w*","handover":r"hand[ -]?over","Afghan-lead":r"Afghan[- ]lead\w*","Afghan forces":r"Afghan (?:security )?forces"}
print("\nTRA term breakdown (passage-level hits) by period")
for k,p in TRA_TERMS.items():
    rx=re.compile(r"\b"+p+r"\b",re.I)
    hit=d.passage.fillna("").map(lambda s: bool(rx.search(s)))
    print(f"  {k:12s}", {q: int(hit[d.per==q].sum()) for q in ["09-11","12-14","15-16"]})
