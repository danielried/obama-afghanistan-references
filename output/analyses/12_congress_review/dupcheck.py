import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
# Review-only: find same-source near-duplicate speeches in speeches.db (read-only). Writes dup_pairs.csv here.
import sqlite3, re, pandas as pd
from datetime import date, timedelta
DB="file:" + str(PROJECT) + "/data/speeches.db?mode=ro"
c=sqlite3.connect(DB, uri=True)
df=pd.read_sql("select id,title,date,raw_text,status from speeches where status='ok'", c)
def sh(t,k=5,cap=4000):
    w=re.sub(r"[^a-z0-9 ]"," ",(t or "").lower()).split()[:cap]
    return {" ".join(w[i:i+k]) for i in range(max(0,len(w)-k+1))}
def jac(a,b): return len(a&b)/len(a|b) if a and b else 0.0
rows=[]
df["sh"]=df.raw_text.map(sh)
for d,g in df.groupby("date"):
    g=g.reset_index(drop=True)
    for i in range(len(g)):
        for j in range(i+1,len(g)):
            j_=jac(g.sh[i],g.sh[j])
            if j_>=0.3:
                rows.append(dict(a=g.id[i],b=g.id[j],date=d,title_a=g.title[i][:60],title_b=g.title[j][:60],jaccard=round(j_,3),len_a=len(g.raw_text[i]),len_b=len(g.raw_text[j])))
out=pd.DataFrame(rows); out.to_csv(str(ANALYSES) + "/12_congress_review/dup_pairs.csv",index=False)
print("pairs same-date jaccard>=0.3:",len(out))
print("pairs jaccard>=0.6:",(out.jaccard>=0.6).sum() if len(out) else 0)
print(out.head(20).to_string())
