import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
# Review-only sensitivity: cap per-day mention counts (reduces single-speech-day domination). Imports analyst module read-only.
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(ANALYSES) + "/12_congress")
import analysis as A   # module-level code only loads CSVs; main block not executed
base = A.daily_arrays(50)
rows = []
for cap in (5, 10, 20):
    cnt, tsum, tn, sp = base
    arr = (np.minimum(cnt, cap), tsum, np.minimum(cnt, cap), sp)
    A.rng = np.random.default_rng(A.SEED)   # same seed each run
    for g in ("afg_verified", "supp_bill_level", "withdraw_unverified", "ndaa_dod_milestones", "all_afghan_related"):
        grp = {"afg_verified": A.votes[A.votes.group=="afg"], "supp_bill_level": A.votes[A.votes.group=="supp"],
               "withdraw_unverified": A.votes[A.votes.group=="withdraw_unverified"], "ndaa_dod_milestones": A.votes[A.votes.group=="ndaa_dod"],
               "all_afghan_related": A.votes[A.votes.group.isin(["afg","supp","withdraw_unverified"])]}[g]
        res = A.run_group(g, grp, arr, label=f"review cap{cap}")[0]
        rows.append({k: res[k] for k in ("group","label","n_clusters","mention_mean_per_window","null_mean_per_window","excess_pct","p_mention_up","p_mention_two")})
df = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(df.round(4).to_string())
df.to_csv(str(ANALYSES) + "/12_congress_review/cap_sensitivity.csv", index=False)
