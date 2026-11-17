import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
import pandas as pd, numpy as np, statsmodels.formula.api as smf, statsmodels.api as sm
from scipy import stats
ROOT=str(PROJECT) + ""
idx = pd.read_csv(f"{ROOT}/output/speeches_index.csv")
refs = pd.read_csv(f"{ROOT}/output/references.csv")
refs = refs.drop(columns=["date"], errors="ignore").merge(idx[["id","type","date","hit_count","text_len"]], left_on="speech_id", right_on="id", how="left")
refs["year"] = refs["date"].astype(str).str[:4].astype(int)
refs["score"] = refs["final_score_pct"].astype(float)
refs["vt"] = refs["rationale"].fillna("").str.contains("venue_title").astype(int)
print("year by type (passage mean):")
print(refs.groupby("type")["year"].agg(["count","mean","min","max"]).round(2).to_string())
# speech-level: mean score per speech, by type (one obs per speech) -> KW
sp = refs.groupby(["speech_id","type"]).agg(mscore=("score","mean"), n=("score","size"), hits=("hit_count","first")).reset_index()
samples=[g["mscore"].values for _,g in sp.groupby("type") if len(g)>=10]
H,p = stats.kruskal(*samples)
print(f"\nspeech-level KW on mean score by type (speeches with >=1 passage): H={H:.2f}, p={p:.3g}, k={len(samples)}")
print(sp.groupby("type")["mscore"].agg(["count","median"]).round(1).to_string())
# passage-level OLS with speech-clustered SE: score ~ type + year FE + log(hits)
d = refs.copy()
d["lhits"] = np.log(d["hit_count"].clip(lower=1))
d["type"] = pd.Categorical(d["type"])
m0 = smf.ols("score ~ C(type, Treatment('remarks'))", data=d).fit(cov_type="cluster", cov_kwds={"groups": d["speech_id"].astype("category").cat.codes})
m1 = smf.ols("score ~ C(type, Treatment('remarks')) + C(year) + lhits", data=d).fit(cov_type="cluster", cov_kwds={"groups": d["speech_id"].astype("category").cat.codes})
m2 = smf.ols("score ~ C(type, Treatment('remarks')) + C(year) + lhits + vt", data=d).fit(cov_type="cluster", cov_kwds={"groups": d["speech_id"].astype("category").cat.codes})
for nm,m in [("type only",m0),("type+year FE+log hits",m1),("+venue_title dummy",m2)]:
    keep=[k for k in m.params.index if k.startswith("C(type")]
    print(f"\n{nm}: R2={m.rsquared:.3f}")
    print(pd.DataFrame({"coef":m.params[keep],"se_cl":m.bse[keep],"p":m.pvalues[keep]}).round(4).to_string())
# rate sensitivity: drop top-3 speeches by passage count within each type
cnt = refs.groupby(["type","speech_id"]).size().reset_index(name="n")
top = cnt.sort_values("n",ascending=False).groupby("type").head(3)[["speech_id"]]
rd = refs[~refs.speech_id.isin(top.speech_id)]
def rate(df, t):
    sub = idx[idx.type==t]
    chars = sub.text_len.sum()
    k = (df.type==t).sum()
    return k, chars, k/chars*1e4
print("\ncrude per-10k rates (passage/text_len), all vs excluding top-3 speeches per type:")
for t in ["remarks","press_conference","statement","address","weekly_address","interview"]:
    k_all, ch_all, r_all = rate(refs, t)
    excl_chars = idx[(idx.type==t) & (~idx.id.isin(top.speech_id))].text_len.sum()
    k_ex = (rd.type==t).sum()
    print(f"{t:18s} all={r_all:.3f}  excl-top3={k_ex/excl_chars*1e4:.3f}  (k={k_ex})")
