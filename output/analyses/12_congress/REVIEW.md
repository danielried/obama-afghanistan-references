# REVIEW: 12_congress (skeptical reviewer, 2026-11-16)

Scope: re-ran analysis.py; read code; checked inputs; spot-checked external sources. Analyst files not edited. Review scripts live in `output/analyses/12_congress_review/`.

## 1. Reproduction
Re-ran `venv/bin/python -I analysis.py`. All key numbers reproduce exactly (mention obs/null/excess, p_up, p_two, rate, tone, sensitivities, closeness rho/p). Only output files were rewritten (same values).

## 2. Code and data checks
- Filters: refs rows reference only status-ok speeches; 0 date mismatches vs speeches_index; 109 questioner rows excluded; 3,877 high-likelihood non-questioner rows (matches).
- Dedupe: `dup_of` is NULL for all 5,026 rows. The project dedupe only matches across sources and every row is govinfo, so it never ran. I checked same-date same-title pairs (124 rows): text Jaccard (5-gram) max 0.47, none >= 0.6. No real duplicates found, so impact is nil, but the "exclude non-empty dup_of" filter is vacuous. Minor.
- Tone: 0 NaN. Tone sums and counts are consistent.
- Null: one random eligible day per cluster, same calendar year, excluding +-14 of all 65 vote dates. Seeded, reproducible. Valid as a design. Caveats: no weekday or session-calendar matching; overlapping windows of neighboring clusters (gaps 15-28 days) are treated as independent.
- Leakage: none found. Congress votes are not used in mention counts.
- OCO vote (2015-06-09, roll 205 Senate) is in the 65-vote closeness set but in no event-study group. Silent omission; fine but should be stated.
- Cluster-table `n_votes` counts distinct dates, not votes. Label bug, no effect on key numbers.
- Closeness: vote-level tests share overlapping windows, so p-values are not independent. Cluster-level all-65 result (rho -0.0375, p=0.83, n=35 clusters, in closeness_results.csv) is omitted from the key.

## 3. Major issue: confounding by concurrent Afghan events (data-checked)
Per-cluster top days (confound.py, from references.csv, high-likelihood non-questioner):
- afg 2010-07-01 (excess +40.5): McChrystal resignation 2010-06-23 (20 passages) and Toronto presser 06-27 (25).
- withdraw 2011-07-06 (+38.8): drawdown address 2011-06-22 (27).
- NDAA 2012-05-18 (+76.3): Chicago NATO summit 2012-05-21 (33), Karzai meeting 05-20 (18).
- NDAA 2014-05-22 (+123.2): Bagram troops remarks 2014-05-25 (38), drawdown remarks 05-27 (37).
- NDAA 2015-10-01 (+53.9): Afghan strategy speech 2015-10-15 (64) at window edge.
- NDAA 2010-12-17 (+26.5): strategy review remarks 2010-12-16 (31).

The positive excesses come from a few policy-event days, not from the votes. The design cannot separate vote timing from Afghan news cycles. This does not change the null, but it means the test has no power and the headline per-group excesses are dominated by a handful of days.

Sensitivity added (review only, `cap_sens.py`): cap per-day mention count at 5, 10, 20 (analyst module imported read-only, same seed):
| group | cap5 excess | p_up | cap10 excess | p_up | cap20 excess | p_up |
|---|---|---|---|---|---|---|
| afg_verified | -10.1% | 0.691 | -8.5% | 0.654 | -5.8% | 0.593 |
| all_afghan | -10.4% | 0.807 | -7.3% | 0.721 | -4.5% | 0.632 |
| supp | -13.9% | 0.719 | -19.5% | 0.790 | -25.0% | 0.838 |
| withdraw | -5.8% | 0.624 | +0.3% | 0.492 | +4.1% | 0.408 |
| ndaa | +0.5% | 0.477 | +5.4% | 0.302 | +12.0% | 0.140 |
Still null. Excess shrinks toward zero for the verified-afg group; the sign is still negative. Supports the null.

## 4. Factual errors in RESULT / key text
- Finding says "no one-sided p is below 0.25". False: afg verified tone p_up = 0.189 (listed in key_numbers). Correct the text.
- Finding says "Spearman signs are weakly negative". The afg-verified vote-level rho is +0.086 (positive). Correct the text.
- "All-Afghan-related" headline includes 14 unverified McGovern/Jones/Kucinich amendments and 6 bill-level supplemental votes. 2010-07-22 (roll 219) is a cloture vote, not war-funding passage. NDAA/DoD milestones are not Afghanistan-specific. Say so next to the headline.

## 5. External spot-checks (WebFetch)
- Roll Call 2010-07-01 (fetched): McGovern 162-260, Lee 100-321, strip-war-funding 25-376. XML rolls 433, 432, 431 match exactly. Also McGovern June 2009 138-278 (XML roll 453 matches) and Kucinich March 2010 "65 votes" (XML roll 98 yea 65). MATCH.
- Himes (fetched): "356 to 65" (House defeated H.Con.Res.248). XML 2010 roll 98: yea 65, nay 356. MATCH (article does not label yea/nay; XML confirms).
- NPR 2011-03-17: fetch timed out. Unverified by fetch. XML roll 193 totals-by-vote: yea 93, nay 321. Analyst's snippet 321-93 agrees with XML. Not confirmed from source.
- Livable World McGovern-Jones 2011: fetched page gives no tally and no amendment number (says DOD authorization amendment, "incredibly close"). The analyst's "204-215" is not in the fetched page. XML roll 373 totals-by-vote: 204-215 (MATCH with XML only). Source attribution needs correction: the number cannot be traced to the cited page.
- All raw XML totals-by-vote blocks checked for 2010_098, 2011_193, 2011_373 (match votes.csv).

## 6. SOURCES.md completeness
- SOURCES claims House XML fetched for 2010 rolls "98,312,336,420-425,426-433,650". Raw directory has 2010 rolls 98, 186, 312, 336, 419-436, 650. fetch_house.py lists only 98, 186, 336, 426-430, 650. No script fetches 312, 419-425, 431-436 (431-433 are the three Afghan rolls, so their provenance is untraceable to a script). Also 2011_146 is in raw and in fetch_house but not in SOURCES. Provenance gap, does not change any votes.csv tally used.
- Senate menus and Roll Call: traceable. Congress.gov 403: documented.

## 7. Verdict
- Key numbers reproduce exactly.
- Null result holds; cap sensitivity keeps it null.
- Strength: keep null_result. Add the confounding caveat (sec 3) and fix the two factual errors (sec 4). Describe as "no detectable effect with this design", not "no effect".
- Confidence: moderate. Power is very low (7 verified clusters), and the verified-content set is small.

## Open items (not done)
- NPR and Livable fetches incomplete (NPR timeout; Livable lacks tally). Snippet-only attributions remain.
- Weekday-matched null not run.
