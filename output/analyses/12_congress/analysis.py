import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
# Event study: Congressional Afghanistan-related actions vs Afghanistan passage mentions (Obama presidency speeches).
# Reads ONLY saved CSVs (votes.csv built from raw official files; project outputs). Fixed seed. Run with -I.
import numpy as np, pandas as pd, json, csv
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

BASE = str(ANALYSES) + "/12_congress"
PROJ = str(PROJECT) + "/output"
SEED = 20260116; B = 10000; W = 14
rng = np.random.default_rng(SEED)

votes = pd.read_csv(f"{BASE}/votes.csv", dtype={"roll": str})
votes["date"] = pd.to_datetime(votes["date"])
votes["margin_share"] = (votes.yea - votes.nay).abs() / (votes.yea + votes.nay)   # 0 = tie (close), 1 = unanimous
refs = pd.read_csv(f"{PROJ}/references.csv", usecols=["date","final_score_pct","rationale","tone"])
refs["date"] = pd.to_datetime(refs["date"])
refs["questioner"] = refs["rationale"].fillna("").str.contains("questioner", case=False)
spk = pd.read_csv(f"{PROJ}/speeches_index.csv")
spk = spk[spk["dup_of"].isna() & (spk["status"] == "ok")].copy()
spk["date"] = pd.to_datetime(spk["date"])
rxn = pd.read_csv(f"{PROJ}/reaction_events.csv", usecols=["date","label"])
rxn["date"] = pd.to_datetime(rxn["date"])

START, END = pd.Timestamp("2009-01-20"), pd.Timestamp("2017-01-20")
grid = pd.date_range(START, END, freq="D"); N = len(grid)
idx_of = {d: i for i, d in enumerate(grid)}
def day_idx(series): return np.array([idx_of[d] for d in series])

def daily_arrays(thr):
    m = refs[(refs.final_score_pct >= thr) & (~refs.questioner)]
    cnt = np.bincount(day_idx(m.date), minlength=N).astype(float)
    tsum = np.bincount(day_idx(m.date), weights=m.tone.values, minlength=N)
    tn = cnt.copy()
    sp = np.bincount(day_idx(spk.date), minlength=N).astype(float)
    return cnt, tsum, tn, sp

def window_sums(arr):  # centered window sum over [i-W, i+W]; NaN where window leaves grid
    cs = np.concatenate([[0], np.cumsum(arr)])
    out = np.full(N, np.nan)
    for i in range(W, N - W):
        out[i] = cs[i + W + 1] - cs[i - W]
    return out

def clusters_of(dates):
    """Merge event dates into clusters: new cluster when gap from previous vote > W days. Center = first date."""
    ds = sorted(set(dates)); cl = []
    for d in ds:
        if cl and (d - cl[-1][-1]).days <= W: cl[-1].append(d)
        else: cl.append([d])
    return cl

all_event_dates = sorted(set(votes.date))
def excluded_mask(extra_dates=()):
    """Grid days within +-W of any Congressional vote date (and any extra dates) are not eligible as null draws."""
    bad = np.zeros(N, bool)
    for e in list(all_event_dates) + list(extra_dates):
        i = idx_of.get(pd.Timestamp(e))
        if i is None: continue
        bad[max(0, i - W): min(N, i + W + 1)] = True
    return bad

def pool_for(center_i, mode, bad):
    lo, hi = W, N - W - 1
    cand = np.arange(lo, hi + 1)
    cand = cand[~bad[cand]]
    if mode == "same_year":
        y = grid[center_i].year
        cand = cand[np.array([grid[c].year == y for c in cand])]
    elif mode == "pm180":
        cand = cand[np.abs(cand - center_i) <= 180]
    return cand

def run_group(name, grp_votes, thr_arrays, extra_excl=(), drop_reaction=False, mode="same_year", label=""):
    cnt, tsum, tn, sp = thr_arrays
    Wcnt, Wsp, Wts, Wtn = window_sums(cnt), window_sums(sp), window_sums(tsum), window_sums(tn)
    cl = clusters_of(list(grp_votes.date))
    centers = []
    for c in cl:
        centers.append(idx_of[c[0]])
    centers = np.array(centers)
    keep = np.ones(len(centers), bool)
    if drop_reaction:
        rd = [pd.Timestamp(x) for x in rxn.date]
        for k, ci in enumerate(centers):
            if any(abs((grid[ci] - r).days) <= W for r in rd): keep[k] = False
    centers = centers[keep]
    if len(centers) == 0: return None
    bad = excluded_mask(extra_excl)
    pools = [pool_for(ci, mode, bad) for ci in centers]
    # observed
    obs_cnt = Wcnt[centers]; obs_sp = Wsp[centers]; obs_tsum = Wts[centers]; obs_tn = Wtn[centers]
    S_cnt_obs = obs_cnt.mean()
    S_rate_obs = obs_cnt.sum() / obs_sp.sum() if obs_sp.sum() > 0 else np.nan
    S_tone_obs = obs_tsum.sum() / obs_tn.sum() if obs_tn.sum() > 0 else np.nan
    # null: one random eligible day per cluster (stratified by year or +-180d), B draws
    draws = np.vstack([p[rng.integers(0, len(p), B)] for p in pools])   # (K, B)
    S_cnt_null = Wcnt[draws].mean(axis=0)
    S_rate_null = Wcnt[draws].sum(axis=0) / Wsp[draws].sum(axis=0)
    S_tone_null = Wts[draws].sum(axis=0) / Wtn[draws].sum(axis=0)
    def p_up(o, n): return (np.sum(n >= o) + 1) / (B + 1)
    def p_two(o, n):
        mu = n.mean(); return (np.sum(np.abs(n - mu) >= abs(o - mu)) + 1) / (B + 1)
    res = dict(group=name, label=label, n_votes=int(len(grp_votes)), n_clusters=int(len(centers)),
        n_votes_kept=int(keep.sum()) if False else None,
        mention_mean_per_window=float(S_cnt_obs), null_mean_per_window=float(S_cnt_null.mean()),
        excess_pct=float(100 * (S_cnt_obs - S_cnt_null.mean()) / S_cnt_null.mean()) if S_cnt_null.mean() > 0 else np.nan,
        p_mention_up=float(p_up(S_cnt_obs, S_cnt_null)), p_mention_two=float(p_two(S_cnt_obs, S_cnt_null)),
        rate_obs=float(S_rate_obs), rate_null_mean=float(S_rate_null.mean()), p_rate_up=float(p_up(S_rate_obs, S_rate_null)),
        tone_obs=float(S_tone_obs), tone_null_mean=float(np.nanmean(S_tone_null)), tone_n_obs=int(obs_tn.sum()),
        p_tone_up=float(p_up(S_tone_obs, S_tone_null)), p_tone_two=float(p_two(S_tone_obs, S_tone_null)))
    # per-cluster table
    base_mean = np.array([Wcnt[p].mean() for p in pools])
    tab = []
    for k, ci in enumerate(centers):
        tab.append(dict(group=name, label=label, center=grid[ci].date().isoformat(), n_votes=len(cl[k]) if k < len(cl) else None,
            obs_mentions_pm14=int(obs_cnt[k]), baseline_mean=round(float(base_mean[k]), 2), excess=round(float(obs_cnt[k] - base_mean[k]), 2),
            obs_speeches_pm14=int(obs_sp[k]), tone_mean=round(float(obs_tsum[k] / obs_tn[k]), 3) if obs_tn[k] > 0 else None, tone_n=int(obs_tn[k])))
    # daily profile: observed mean and null band per offset
    offs = np.arange(-W, W + 1)
    prof_obs = np.array([cnt[centers + o].mean() for o in offs])
    prof_null = np.stack([cnt[draws + o].mean(axis=0) for o in offs], axis=0)  # (2W+1, B)
    return res, tab, dict(offs=offs, obs=prof_obs, lo=np.percentile(prof_null, 5, axis=1), hi=np.percentile(prof_null, 95, axis=1))

def closeness_test(sel, thr_arrays, label):
    cnt = thr_arrays[0]; Wcnt = window_sums(cnt)
    bad = excluded_mask()
    ex = []
    for _, v in sel.iterrows():
        ci = idx_of[v.date]
        base = Wcnt[pool_for(ci, "same_year", bad)].mean()
        ex.append(Wcnt[ci] - base)
    ex = np.array(ex); ms = sel.margin_share.values
    rho, p = stats.spearmanr(ms, ex)
    # cluster-level: one value per cluster (min margin, mean excess) to limit overlap dependence
    cl = clusters_of(list(sel.date))
    cms, cex = [], []
    for c in cl:
        sub = sel[sel.date.isin(c)]
        ci = idx_of[c[0]]
        base = Wcnt[pool_for(ci, "same_year", bad)].mean()
        cms.append(sub.margin_share.min()); cex.append(Wcnt[ci] - base)
    rho_c, p_c = stats.spearmanr(cms, cex) if len(cl) >= 3 else (np.nan, np.nan)
    return dict(set=label, n_votes=int(len(sel)), rho_vote=float(rho), p_vote=float(p),
                n_clusters=len(cl), rho_cluster=float(rho_c), p_cluster=float(p_c))

if __name__ == "__main__":
    print("votes:", len(votes), "groups:", votes.group.value_counts().to_dict())
    print("refs rows:", len(refs), "questioner rows:", int(refs.questioner.sum()), "speeches ok (non-dup):", len(spk))
    base_arr = daily_arrays(50)
    print("daily total mentions (thr50, non-questioner):", int(base_arr[0].sum()), "speeches:", int(base_arr[3].sum()))

    groups = {
        "afg_verified": votes[votes.group == "afg"],
        "supp_bill_level": votes[votes.group == "supp"],
        "withdraw_unverified": votes[votes.group == "withdraw_unverified"],
        "ndaa_dod_milestones": votes[votes.group == "ndaa_dod"],
        "all_afghan_related": votes[votes.group.isin(["afg", "supp", "withdraw_unverified"])],
    }
    out_rows, tabs, profiles = [], [], {}
    for g, sub in groups.items():
        r = run_group(g, sub, base_arr, label="primary thr50, same-year null")
        if r is None: continue
        res, tab, prof = r
        out_rows.append(res); tabs += tab; profiles[g] = prof
    # Sensitivity: thresholds 30 / 70
    for thr in (30, 70):
        arr = daily_arrays(thr)
        for g in ("afg_verified", "all_afghan_related"):
            r = run_group(g, groups[g], arr, label=f"sens thr{thr}")
            if r: out_rows.append(r[0])
    # Sensitivity: drop windows overlapping reaction_events dates; also exclude those dates from null pool
    rx = list(rxn.date)
    for g in groups:
        r = run_group(g, groups[g], base_arr, extra_excl=rx, drop_reaction=True, label="sens drop reaction-overlap (+pool excl)")
        if r: out_rows.append(r[0])
    # Sensitivity: null within +-180 days instead of same calendar year
    for g in ("afg_verified", "all_afghan_related"):
        r = run_group(g, groups[g], base_arr, mode="pm180", label="sens null +-180d")
        if r: out_rows.append(r[0])

    res_df = pd.DataFrame(out_rows)
    res_df.to_csv(f"{BASE}/event_study_results.csv", index=False)
    pd.DataFrame(tabs).to_csv(f"{BASE}/cluster_table.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(res_df[["group","label","n_votes","n_clusters","mention_mean_per_window","null_mean_per_window","excess_pct","p_mention_up","p_mention_two","rate_obs","rate_null_mean","p_rate_up","tone_obs","tone_null_mean","tone_n_obs","p_tone_up"]].round(4).to_string())
    print(pd.DataFrame(tabs)[tabs and ["group","center","n_votes","obs_mentions_pm14","baseline_mean","excess","obs_speeches_pm14","tone_mean","tone_n"]].to_string() if False else pd.DataFrame(tabs).to_string())

    # Close-vote test
    cv = []
    cv.append(closeness_test(votes, base_arr, "all 65 votes"))
    cv.append(closeness_test(votes[votes.group.isin(["afg","supp","withdraw_unverified"])], base_arr, "afghan-related (afg+supp+withdraw)"))
    cv.append(closeness_test(votes[votes.group == "afg"], base_arr, "afg_verified only"))
    cv_df = pd.DataFrame(cv); cv_df.to_csv(f"{BASE}/closeness_results.csv", index=False)
    print(cv_df.round(4).to_string())

    # Figure: event profiles (4 groups) + closeness scatter
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    names = [g for g in ["afg_verified", "supp_bill_level", "withdraw_unverified", "ndaa_dod_milestones"] if g in profiles]
    for ax, g in zip(axes.flat, names):
        p = profiles[g]
        ax.fill_between(p["offs"], p["lo"], p["hi"], color="#bbbbbb", alpha=0.6, label="null 5-95% (same-year draws)")
        ax.plot(p["offs"], p["obs"], color="#1f4e79", lw=2, marker="o", ms=3, label="observed (cluster mean)")
        ax.axvline(0, color="k", lw=0.8, ls="--")
        ax.set_title(g, fontsize=10); ax.set_xlabel("days from cluster start"); ax.set_ylabel("Afghanistan passages/day")
    axes.flat[0].legend(fontsize=7, loc="upper left")
    ax = axes.flat[4]
    m = votes[votes.group.isin(["afg","supp","withdraw_unverified"])].copy()
    Wc = window_sums(base_arr[0]); bad = excluded_mask()
    m["excess"] = [Wc[idx_of[d]] - Wc[pool_for(idx_of[d], "same_year", bad)].mean() for d in m.date]
    ax.scatter(m.margin_share, m.excess, s=22, c="#1f4e79")
    ax.set_xlabel("margin share |yea-nay|/(yea+nay)  (0 = closest)"); ax.set_ylabel("excess passages in [-14,+14]")
    ax.set_title("Afghanistan-related votes: closeness vs excess", fontsize=10)
    axes.flat[5].axis("off")
    fig.suptitle("Congressional Afghanistan-related actions vs Obama Afghanistan passages (high-likelihood, non-questioner)", fontsize=10)
    fig.tight_layout(); fig.savefig(f"{BASE}/event_study.png", dpi=130)
    print("wrote event_study.png")
