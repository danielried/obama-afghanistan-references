import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import pandas as pd, numpy as np, statsmodels.api as sm, math
from scipy import stats
ROOT=str(PROJECT) + ""
idx = pd.read_csv(f"{ROOT}/output/speeches_index.csv")
refs = pd.read_csv(f"{ROOT}/output/references.csv")
cnt = refs.groupby("speech_id").size()
idx["y"] = idx["id"].map(cnt).fillna(0).astype(int)
idx["L"] = idx["text_len"].astype(float)
def glm(df, label):
    df = df[df.L>0].copy()
    X = pd.get_dummies(df["type"]).astype(float).drop(columns=["remarks"])
    X = sm.add_constant(X, has_constant="add")
    m = sm.NegativeBinomial(df["y"].values, X.values, exposure=df["L"].values).fit(disp=0, maxiter=500)
    print(label, "n=",len(df))
    for i,name in enumerate(X.columns[1:],start=1):
        b,se=m.params[i],m.bse[i]
        print(f"  {name:18s} IRR={math.exp(b):.3f} [{math.exp(b-1.96*se):.3f},{math.exp(b+1.96*se):.3f}] p={2*stats.norm.sf(abs(b/se)):.3g}")
glm(idx, "ALL (analyst reproduction)")
# drop top-3 speeches by passage count per type
refs["type"]=refs["speech_id"].map(dict(zip(idx.id,idx.type)))
top = refs.groupby(["type","speech_id"]).size().reset_index(name="n").sort_values("n",ascending=False).groupby("type").head(3).speech_id
glm(idx[~idx.id.isin(top)], "EXCL top-3 passage speeches per type")
# independent crude: passage/text_len from index
try:
    import vaderSentiment
    print("vaderSentiment available")
except Exception as e:
    print("vaderSentiment not importable:", e)
