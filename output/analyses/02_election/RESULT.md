# 02_election: is 2012 framed more around withdrawal?

**Question.** 2012 has 731 high-likelihood passages (final_score_pct >= 50), the same as 2009 (735). Is 2012, especially Jan to Nov 6 2012, framed more around ending/withdrawal than other years? Does the spike come from campaign stump lines repeated across speeches?

**Input.** `output/references.csv` (4,741 passages; read-only). `speeches_index.csv` (5,026 speeches, none with `dup_of` set). Questioner passages excluded from frame analysis (`rationale` contains `questioner_not_president`: 58 of 3,935 at >=50). Final n = 3,877.

**Method.**
- Frames are lexical regexes on passage text. Withdrawal: end the war, coming home, bring troops home, drawdown, responsible end, withdraw*, transition*, handover, etc. Escalation: surge, combat, Taliban, insurgen*, attack*, counterinsurg*, strateg*, etc. Full patterns in `analysis.py`.
- Periods: campaign_2012 = 2012-01-01..11-06; midterm_2010 = 2010-01-01..11-02; midterm_2014 = 2014-01-01..11-04; non_election = rest.
- Near-duplicates: 8-gram Jaccard >= 0.5 with union-find; boilerplate shingles in >150 passages ignored.
- Tests: chi-square, Fisher exact for 2x2, logistic regression (year FE, speech type, repeat flag), quasi-Poisson of high-likelihood passages per speech-month (dispersion 47.8).
- Sensitivity: thresholds 30/50/70; withdrawal frame using passage + context.

## Numbers

| Quantity | Value |
|---|---|
| Hi50 by year (2009 / 2010 / 2012) | 735 / 732 / 731 |
| Hi50 per non-dup speech (2009 / 2010 / 2012) | 1.03 / 0.97 / **1.14** (highest of all years) |
| Speeches per month, mean 2009 / 2012 | 59.7 / 53.6 (2012 volume not higher) |
| Repeat share of hi50 (near-dup), 2012 vs other years | 10.5% vs <=1.8% |
| Withdrawal share, nonq hi50: 2012 vs other years | 31.8% (231/726) vs 9.4% (297/3151); OR 4.48, chi2 251.5, p=1e-56 |
| Escalation share: 2012 vs other years | 18.2% vs 30.4%; OR 0.51, p=4e-11 |
| Withdrawal share by period: campaign_2012 / midterm_2010 / midterm_2014 / non_election | 32.0% (n=709) / 5.7% (542) / 12.5% (279) / 10.0% (2347); chi2 259, df 3, p=8e-56 |
| Campaign_2012 vs midterm windows, withdrawal | OR 5.39, p=1e-32 |
| Non-May 2012 campaign vs midterm windows, withdrawal | 42.2% (181/429) vs 8.0% (66/821); OR 8.35, p=5e-47 |
| Same, excluding `transition` from the frame | 27.7% (119/429) vs 5.0% (41/821); OR 7.30, p=3e-30 |
| May 2012 campaign-window passages (Kabul SPA, Bagram, Chicago NATO) | n=280, withdrawal 16.4% (lower than the rest of 2012) |
| Non-May campaign withdrawal passages in repeat clusters | 23 of 181 (12.7%) |
| Non-May campaign withdrawal share, repeats removed | 43.2% (158/366) vs midterms 7.7%; OR 9.08, p=2e-44 |
| Logit W ~ campaign_2012 + midterm (no year FE) | OR 4.23, p=3e-42 |
| Logit W ~ campaign_2012 + midterm + year FE + type + repeat | OR 1.66, p=0.39 (not identified: only 17 post-Nov-6 2012 hi passages) |
| Logit W ~ y2012 vs rest, type + repeat | OR 4.18, p=3e-40 |
| Quasi-Poisson hi per speech-month, campaign_2012 RR (year FE) | 2.28, p=0.43; excluding May 2012: 1.51, p=0.68 |
| Threshold sensitivity (campaign vs 2010 midterm, withdrawal) | th30: 27.5% vs 5.4%; th50: 32.0% vs 5.7%; th70: 33.4% vs 8.1% (all p<1e-25) |
| Context-window frame, campaign vs non-election | 52.8% vs 23.8% (chi2 282, p=7e-61) |

Top 2012 speeches by hi50 count: Joint Statement on SPA (May 2, 81), Bagram address (May 2, 42), Cameron presser (Mar 14, 37), Chicago presser (May 21, 37), Boca Raton debate (Oct 22, 28). Top-5 speeches hold 31% of 2012 hi50 (2009: 25%).

Top repeated 2012 campaign lines: "I said we'd wind down the war in Afghanistan, and we are." (9 speeches, Sep 7-22); "I said we'd end the war in Afghanistan; we are." (4 speeches, Oct 18-25); "...the war in Afghanistan is ending..." (7 speeches, Nov 2-5).

## Finding
2012 is more withdrawal-framed than other years on this lexical measure, and the difference holds across thresholds (30/50/70), with or without `transition`, and in passage-plus-context coding. Escalation framing is lower in 2012 and in the campaign window. Strength: strong for "2012 more withdrawal-framed than other years" (p<1e-50, large OR).

The 2012 spike in count is real in rate terms (1.14 hi passages per speech, the highest year), not caused by more speeches. Stump-line repetition is part of it but not the bulk: about 13% of non-May campaign withdrawal passages are repeated near-duplicates, and the effect remains (OR 9.1) after removing repeats. Much of the 2012 withdrawal framing is in the Kabul and Chicago event coverage and in the non-repeated campaign text.

**What this does not show:** the campaign window per se, separate from 2012 as a year. With year fixed effects, the campaign-window coefficient is not estimable from the data (only 17 hi passages after Nov 6 2012). The campaign-vs-midterm comparisons are between different years, so they cannot separate campaign rhetoric from a 2012-specific shift in policy messaging. Conclusion: "2012-specific withdrawal framing" is supported; "campaign-driven" is plausible but not separately testable here.

## Caveats
- Frame coding is lexical, not human-coded. `transition` is ambiguous (handover of security vs general use). `withdraw*` and `end the war` can be negated or refer to Iraq; not manually checked. VADER tone was not used; it measures word valence, not stance.
- The hi-likelihood scores come from a rule-based scorer tuned on 30 hand labels. The scores are estimates, not ground truth.
- Near-duplicate threshold (Jaccard >= 0.5 on 8-grams) is a judgment; results were similar with unique clusters.
- Poisson p-values come from quasi-Poisson (dispersion 47.8). Plain Poisson would be far too liberal.
- Speech volume is taken from `speeches_index.csv`, which covers all sources, not only those with hits.

Reproduce: `.venv/bin/python -I output/analyses/02_election/analysis.py`
Outputs: `results.json`, `monthly_counts.csv`, `election_frame.png`, `run_log.txt`.
