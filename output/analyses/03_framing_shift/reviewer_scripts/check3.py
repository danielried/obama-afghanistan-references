import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import re, numpy as np, pandas as pd
from scipy.stats import chi2_contingency
d=pd.read_pickle(str(HERE) + "/d.pkl")
rng=np.random.default_rng(7)
PER=["09-11","12-14","15-16"]
def tab(col, df):
    t=[[int(df[df.per==p][col].sum()), int((df.per==p).sum()-df[df.per==p][col].sum())] for p in PER]
    return chi2_contingency(np.array(t))[1]
def shares(col, df): return {p: round(float(df[df.per==p][col].mean()),3) for p in PER}
d["wd"]=d.category.eq("war_direct")
print("END all      ", shares("end",d), "p=%.3g"%tab("end",d))
print("END excl Iraq", shares("end_noiraq",d), "p=%.3g"%tab("end_noiraq",d))
# fast speech-cluster bootstrap: per-speech sums
def boot(col, B=3000):
    g=d.groupby("speech_id")
    S=g.apply(lambda x: pd.Series({"y12":x.loc[x.per=="12-14",col].sum(),"n12":(x.per=="12-14").sum(),
                                  "y09":x.loc[x.per=="09-11",col].sum(),"n09":(x.per=="09-11").sum()}),include_groups=False).to_numpy(float)
    m=len(S); out=[]
    for _ in range(B):
        idx=rng.integers(0,m,m); s=S[idx].sum(0)
        out.append(s[0]/s[1]-s[2]/s[3])
    out=np.array(out)
    obs=d[d.per=="12-14"][col].mean()-d[d.per=="09-11"][col].mean()
    return round(float(obs),4), np.round(np.percentile(out,[2.5,97.5]),4).tolist(), "frac_boot_le0=%.4f"%np.mean(out<=0)
print("cluster-boot 12-14 minus 09-11 END all:", boot("end"))
print("cluster-boot 12-14 minus 09-11 END excl Iraq:", boot("end_noiraq"))
print("cluster-boot 12-14 minus 09-11 TRA:", boot("tra"))
print("cluster-boot 12-14 minus 09-11 war_direct:", boot("wd"))
dd=d.drop_duplicates(subset=["passage"],keep="first")
print("\nDEDUPED passage text n:", len(dd), "from", len(d))
print("END dedup", shares("end",dd), "p=%.3g"%tab("end",dd))
print("TRA dedup", shares("tra",dd), "p=%.3g"%tab("tra",dd))
print("war_direct dedup", shares("wd",dd), "p=%.3g"%tab("wd",dd))
TRA_TERMS={"transition":r"transition\w*","transfer":r"transfer\w*","train":r"train\w*","advis":r"advis\w*","handover":r"hand[ -]?over","Afghan-lead":r"Afghan[- ]lead\w*","Afghan forces":r"Afghan (?:security )?forces"}
print("\nTRA term breakdown (passage hits) by period")
for k,p in TRA_TERMS.items():
    rx=re.compile(r"\b"+p+r"\b",re.I)
    hit=d.passage.fillna("").map(lambda s: bool(rx.search(s)))
    print(f"  {k:12s}", {q: int(hit[d.per==q].sum()) for q in PER})
