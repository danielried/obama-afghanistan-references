import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
# Review-only: which speech days drive each primary cluster window (read-only inputs).
import pandas as pd
P=str(PROJECT) + "/output"
B=str(ANALYSES) + "/12_congress"
r=pd.read_csv(f"{P}/references.csv",usecols=["date","speech_id","speech_title","final_score_pct","rationale"])
r["date"]=pd.to_datetime(r.date)
r=r[(r.final_score_pct>=50)&~r.rationale.fillna("").str.contains("questioner",case=False)]
v=pd.read_csv(f"{B}/cluster_table.csv")
ct=pd.read_csv(f"{B}/cluster_table.csv")
for g in ["afg_verified","supp_bill_level","withdraw_unverified","ndaa_dod_milestones"]:
    sub=ct[ct.group==g]
    print("==",g)
    for _,row in sub.iterrows():
        c=pd.Timestamp(row.center); lo,hi=c-pd.Timedelta(days=14),c+pd.Timedelta(days=14)
        w=r[(r.date>=lo)&(r.date<=hi)]
        top=w.groupby(["date","speech_title"]).size().sort_values(ascending=False).head(3)
        print(row.center, "obs",row.obs_mentions_pm14, "excess",row.excess, "| top days:", "; ".join(f"{k[0].date()} {k[1][:55]} ({n})" for k,n in top.items()))
