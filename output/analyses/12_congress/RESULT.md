# 12_congress: Congressional Afghanistan actions and presidential Afghanistan mentions, 2009-2016

## Question
Do Congressional actions on the Afghanistan war (war-funding supplementals, Afghanistan-specific votes, withdrawal amendments, war-powers resolutions, NDAA/DoD-appropriations milestones) coincide with more or different Afghanistan passages in Obama's presidency speeches? Do close votes draw more mentions?

## Data
- Votes: 65 roll calls, built only from saved official files (clerk.house.gov roll XML; senate.gov vote menus). See votes.csv and SOURCES.md.
  - afg (Afghanistan-specific, content verified by title or secondary source): 10 votes.
  - supp (2009 and 2010 war-funding supplementals, bill-level, content not verified): 6.
  - withdraw_unverified (House McGovern / Jones / Kucinich amendments; XML gives author only): 14.
  - ndaa_dod (final passage or conference of NDAA and DoD appropriations): 34.
  - oco (Senate Reed Amdt 1521, OCO limit): 1.
- Mentions: references.csv, passages with final_score_pct >= 50, excluding questioner-flagged rows (rationale). 3,877 passages. Speech denominators: 5,023 status-ok, non-duplicate speeches.
- Tone: the project's VADER `tone` column (word valence, not stance).

## Method
- Votes merged into clusters when within 14 days of the previous vote. Window: [-14, +14] days around cluster start.
- Null: for each cluster, one random day from the same calendar year (also +-180 days as sensitivity), excluding any day within 14 days of any Congressional vote. 10,000 draws, seed 20260116.
- Statistics: mean passages per window (also pooled rate per speech, and pooled tone). p_up = one-sided upper tail, p_two = two-sided.
- Close-vote test: margin share |yea-nay|/(yea+nay) (0 = closest) vs excess passages per vote window (observed minus same-year mean). Spearman, per vote and per cluster.

## Numbers (from analysis.py output)
| Group | votes / clusters | Mean passages per window (obs / null) | Excess | p_up | p_two | Rate p_up | Tone obs / null (n) | Tone p_up |
|---|---|---|---|---|---|---|---|---|
| afg (verified) | 10 / 7 | 37.0 / 49.6 | -25.4% | 0.758 | 0.460 | 0.830 | 0.247 / 0.158 (259) | 0.189 |
| supp (bill-level) | 6 / 4 | 35.3 / 63.4 | -44.4% | 0.889 | 0.249 | 0.966 | 0.169 / 0.170 (141) | 0.491 |
| withdraw_unverified | 14 / 10 | 36.2 / 42.7 | -15.3% | 0.665 | 0.615 | 0.789 | 0.079 / 0.132 (362) | 0.715 |
| ndaa_dod | 34 / 28 | 37.1 / 38.9 | -4.7% | 0.576 | 0.799 | 0.678 | 0.160 / 0.156 (1039) | 0.493 |
| all Afghan-related | 30 / 18 | 35.8 / 47.3 | -24.3% | 0.888 | 0.241 | 0.949 | 0.149 / 0.150 (644) | 0.523 |

Sensitivity (p_up for mentions):
- Threshold 30: afg 0.784; all Afghan-related 0.867. Threshold 70: afg 0.778; all Afghan-related 0.838.
- Drop windows overlapping the 13 reaction_events dates (and exclude them from null): afg 0.827 (6 clusters); all Afghan-related 0.869 (16 clusters).
- Null within +-180 days instead of same year: afg 0.675; all Afghan-related 0.871.

Close-vote Spearman (negative = closer votes draw more excess):
- All 65 votes: rho -0.113, p 0.369. Cluster level (35 clusters): rho -0.038, p 0.831.
- Afghan-related 30 votes: rho -0.211, p 0.263. Cluster level (18): rho -0.330, p 0.181.
- afg verified 10 votes: rho +0.086, p 0.813. Cluster level (7): rho -0.429, p 0.337.

## Finding
No Congressional Afghanistan action in 2009-2016 is associated with a statistically detectable change in Afghanistan passage volume, rate or tone in the [-14,+14] windows. Every group shows a negative mean excess (-5% to -44%), and no one-sided p-value is below 0.25. Close votes do not attract more mentions: the Spearman signs are weakly negative (closer votes slightly more mentions) but none is significant. This is a null result. Power is very low (7 verified-Afghanistan clusters), so only large effects could be detected.

## Caveats
1. Power: the verified Afghanistan set has 10 votes, 7 clusters. A null is expected at this n.
2. Content verification: 6 supplemental and 14 McGovern/Jones/Kucinich rows are not verified against bill or amendment text. Only the 10 afg rows are verified (XML title, Senate menu title, or a secondary source). Kucinich 2011 roll 530 and 2011 roll 498 were not checked against any second source.
3. House H.R.4899 (FY2010 supplemental): the July 1, 2010 Afghanistan votes are rolls 431-433 (verified by Roll Call tallies). The House passage of the war-funding portion is not identified, so no House final-passage row is included for it.
4. Excluded as non-Afghanistan war-powers votes: 2011 rolls 411 and 412 (Libya), 2014 roll 452 and 2015 roll 370 (Iraq and Syria). No 2013 House war-powers vote on Afghanistan was found in the index.
5. VADER tone is word valence, not stance. Tone n per window is thin for some clusters (see cluster_table.csv).
6. Windows overlap across clusters, and mention counts are heavily influenced by speech volume (normalized rate reported alongside).
7. Multiple tests: 5 groups x 3 metrics. None are significant, so no correction changes conclusions.
8. Questioner passages are removed using the rationale flag (109 rows). Undetected questioner paragraphs may remain.
9. congress.gov was unreachable (403). Roll tallies come from clerk and senate.gov XML.

## Files
- analysis.py (re-run: .venv/bin/python -I .../12_congress/analysis.py)
- build_votes.py, fetch_house.py (fetch side), votes.csv, event_study_results.csv, cluster_table.csv, closeness_results.csv, event_study.png, SOURCES.md
