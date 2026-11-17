# 10_public_opinion: Afghanistan opinion (Gallup/Pew) vs Obama passage volume, tone, frame

**Question.** Does US public opinion on the Afghanistan war move with Obama's Afghanistan rhetoric (volume, VADER tone, frame shares) in the 30 days before a poll, and do opinion drops precede rhetoric shifts in the following 30 days?

**Data.**
- Opinion: Gallup "mistake" item, 11 readings Jul 2009 to Jun 2015 inside the presidency (Jan 2009 reading excluded: its 30-day pre-window starts before inauguration). Read directly from Gallup topline PDF (S1). Approval of Obama's handling of Afghanistan (Gallup): 4 readings, Nov 2009 to Nov 2010 (S3, S4). Pew right-decision: 4 points (S6, S7), too few to test.
- Passages: `output/references.csv`, 4,632 after dropping 109 questioner-flagged passages (`questioner_not_president`) and passages in duplicate speeches. Speeches: `output/speeches_index.csv`, 5,026 non-dup.
- High-likelihood = `final_score_pct >= 50` (primary). Sensitivity at 30 and 70.
- Windows: pre = [t-30d, t), post = [t, t+30d), t = fieldwork midpoint.

**Method.** Spearman rho, exact p and permutation p (10,000 shuffles). Volume = high-likelihood passages per window and per 100 speeches. Tone = mean VADER compound (word valence, not stance). Frame = category share among high-likelihood passages. Tests: (A) opinion_t vs pre-window; (B) opinion_t vs post-window; (C) opinion drop since prior poll vs change in rhetoric (post minus pre). Time-trend check in `confound_check.py`.

**Key numbers (thr 50, n=11 polls).**

| Test | Metric | n | rho | p_exact | p_perm |
|---|---|---|---|---|---|
| A contemporaneous | high-lik. passages (count) | 11 | -0.83 | 0.0015 | 0.003 |
| A | per 100 speeches | 11 | -0.77 | 0.005 | 0.007 |
| A | share war_direct | 11 | +0.73 | 0.010 | 0.014 |
| A | tone mean | 11 | -0.37 | 0.27 | 0.26 |
| B lead | count | 11 | -0.64 | 0.035 | 0.041 |
| B lead | tone mean | 10 | -0.26 | 0.46 | 0.46 |
| C drop -> change | tone mean | 9 | +0.78 | 0.014 | 0.018 |
| C drop -> change | count | 10 | +0.34 | 0.34 | 0.34 |
| Approval (Gallup), pre | per 100 speeches | 4 | -1.0 | n/a (scipy t-approx gives 0.00, unreliable at n=4) | 0.08 (exact enumeration: 0.083 two-sided) |

Time confound (opinion rises over time, volume falls): opinion vs days since inauguration rho=+0.82 (p=0.002). Partial rho of opinion with pre-window count controlling for time: -0.54 (thr 50, p=0.11); -0.66 at thr 30 (p=0.04); -0.28 at thr 70 (p=0.44). Partial with per-100-speeches: -0.49 (p=0.15) at thr 50; -0.03 at thr 70.

**Sensitivity.** The contemporaneous and lead volume correlations are negative at all thresholds; significance drops after controlling for time. Tone-based results are unstable across thresholds (test C tone: rho +0.84 at thr 30, +0.78 at thr 50, +0.52 at thr 70, p=0.19).

**Finding.**
1. Volume is negatively associated with the public-opinion "mistake" share, both before and after each poll. Most of this is the shared time trend: opinion rose and rhetoric fell from 2009 to 2015. With time partialled out, the volume link is weak and not significant at thr 50 or 70.
2. Tone: no reliable relation to opinion level (test A rho -0.37, p=0.27).
3. Opinion drops do not predict a rhetoric shift in the expected direction. When opinion fell since the previous poll, the tone of the following window was higher (rho +0.78, p=0.014 at thr 50). This is the opposite of "rhetoric darkens after opinion falls". It rests on 9 points, does not hold at thr 70, and is not corrected for ~54 tests run. Treat as likely chance or a VADER artifact.
4. Approval series (n=4) and Pew right-decision (n=3 covered) are descriptive only.

**Verdict: weak / inconclusive.** No robust link between public opinion and Obama's Afghanistan rhetoric beyond a shared time trend. Opinion-drop-then-tone result is fragile and contrary to hypothesis.

**Caveats.**
- n=11 mistake readings. Power is low; p-values are from 54 uncorrected tests.
- Gallup wording changed: 2009-2011 "military forces" (comparison block) vs 2013-2015 "sending troops to fight" (main Q25 block). Both used as one series.
- Approval values from Gallup articles (WebFetch summary). Nov 2009 and Feb 2010 are month-only; mid-month used as placeholder.
- Pew values from WebFetch summaries of pewresearch.org pages (question wording not verified). Pew 2011-11 (56) vs 2011-06 (57) taken from different pages.
- Gallup gives no 2012 or 2016 readings in S1; windows after Jun 2015 have no opinion point.
- Passage scores are rule-based estimates (README); no LLM judge. VADER = word valence, not stance.
- Search-result summaries (WebSearch) were used only to find URLs; no figure in the analysis came from them alone.

**Files.** `analysis.py` (main), `confound_check.py`, `out/mistake_windows_thr{30,50,70}.csv`, `out/correlations_thr*.csv`, `out/approval_windows_thr50.csv`, `out/confound_time_check.csv`, `out/chart_opinion_vs_volume.png`, `data/gallup_mistake.csv`, `data/gallup_approval_obama_afghanistan.csv`, `data/pew_right_decision.csv`, `SOURCES.md`.
