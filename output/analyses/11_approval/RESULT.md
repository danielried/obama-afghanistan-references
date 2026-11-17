# 11_approval: Obama job approval vs Afghanistan passage volume and tone

**Question.** Does Obama's monthly job approval move with how often (and how negatively or positively) he talks about Afghanistan in presidential speeches? Tested in levels, first differences, lags (0–6 months), and Granger causality in both directions.

**Data.**
- Approval: UCSB American Presidency Project weekly table for Obama (418 weekly windows, 01/19/2009–01/19/2017). Converted to monthly means of the weekly approve % (by window midpoint). Primary window Feb 2009 to Dec 2016 (n = 95 months); Jan 2009 and Jan 2017 are partial and used only in a sensitivity run.
- Afghanistan: `output/references.csv` (4,741 passages). Primary exposure = passages with `final_score_pct >= 50` (the "high-likelihood" cut), excluding questioner passages (109 flagged). Normalized as passages per 10,000 words of presidential text (words from `data/speeches.db`, status ok, non-dup; 8.58M words total).
- Tone: `tone` (VADER compound) averaged over high-likelihood passages per month. VADER is word valence, not stance.
- Validation: 16 published Gallup monthly values (2011–2012 and 2016) vs the UCSB-derived monthly means.

**Method.** Pearson and Spearman correlations; first differences of approval and of the rate; cross-correlation at lags 0–6 in both directions; ADF stationarity checks; `statsmodels` Granger F-tests on first differences, lags 1–3; threshold (30/50/70) and inclusion sensitivities; Jan 2013 outlier exclusion.

**Numbers.**

| Test | n | Statistic | p |
|---|---|---|---|
| Level: approval vs Afghan rate (>=50) | 95 | r = 0.117 | 0.261 |
| Level: same, Spearman | 95 | rho = 0.147 | 0.156 |
| Level: approval vs monthly mean tone (VADER) | 95 | r = 0.031 | 0.763 |
| Diff, lag 0 (d approval vs d rate) | 94 | r = 0.037 | 0.720 |
| Diff, lag 0, Spearman | 94 | rho = 0.002 | 0.988 |
| Diff, Afghan leads approval by 1 mo | 93 | r = 0.059 | 0.575 |
| Diff, Afghan leads by 2 mo | 92 | r = -0.091 | 0.386 |
| Diff, Afghan leads by 3 mo | 91 | r = -0.123 | 0.246 |
| Diff, approval leads Afghan by 1 mo | 93 | r = 0.128 | 0.221 |
| Granger Afghan -> approval, lag 1 | 94 | F = 0.29 | 0.592 |
| Granger Afghan -> approval, lag 2 | 94 | F = 0.45 | 0.642 |
| Granger Afghan -> approval, lag 3 | 94 | F = 1.49 | 0.224 |
| Granger approval -> Afghan, lag 1 | 94 | F = 2.58 | 0.112 |
| Granger approval -> Afghan, lag 2 | 94 | F = 2.24 | 0.112 |
| Granger approval -> Afghan, lag 3 | 94 | F = 1.62 | 0.190 |

Descriptive values: approval monthly mean 47.8 (sd 5.1), range 40.5 (Aug 2011) to 64.3 (May 2009). Afghan high-likelihood passages: 3,853 total; rate mean 4.68 per 10k words (median 3.15, max 39.0 in Jan 2013). Monthly tone mean 0.117 (sd 0.212). Stationarity: approval in levels ADF p = 0.046 (borderline), approval differenced p < 0.001, Afghan rate in levels p < 0.001.

**Sensitivity (level r / p; lag-0 diff r / p).**
- Threshold 30: 0.122 / 0.240; 0.036 / 0.729.
- Threshold 70: 0.094 / 0.365; 0.035 / 0.736.
- All passages (no threshold, rate_all): 0.130 / 0.209; 0.055 / 0.598.
- Include questioner passages: 0.119 / 0.251; 0.036 / 0.732.
- Exclude Jan 2013 (one Karzai press conference and joint statement drives the peak): 0.077 / 0.464; 0.014 / 0.897.
- Full range incl. partial months (n = 97): 0.122 / 0.234; 0.036 / 0.731.
- Validation vs published Gallup monthly values (n = 16): mean abs diff 0.37 pts, max 0.8.

**Finding.** No detectable relationship. Monthly Afghanistan passage volume does not track approval in levels or in month-to-month changes, at lag 0 or lags 1–3. Granger tests do not support Afghan mentions predicting approval (p = 0.59 to 0.64 for lags 1–2; lag 3 p = 0.22). Reverse direction (approval -> Afghan mentions) is also not significant (p = 0.11 to 0.19), but it is the closer of the two (approval-leads-volume lag-1 p = 0.22 in the cross-correlation). Tone (VADER) is unrelated to approval (r = 0.03). Strength: **null result** on this series and these measures, with 95 monthly observations.

**Caveats.**
- The approval series is a UCSB-hosted weekly table. The page does not name the pollster. It matches the 16 Gallup values checked, but Obama's Gallup-labelled Google Sheet was not found, and the UCSB sheets checked are for other presidents. Several Gallup validation values come from search snippets, not full page fetches.
- Monthly approval is an unweighted mean of overlapping 7-day windows. Passage volume is driven by press conferences and foreign-policy events. Large approval moves (2009 decline, 2011 bin Laden bump, 2013 slide, late-2016 rise) are dominated by other issues, and the test has no controls for them.
- The Jan 2013 spike is one event; excluding it weakens the level correlation but leaves the null in place.
- VADER tone is word valence, not stance.
- Multiple tests (about 30 reported) with no correction; the non-significant results are reported as-is. ADF on approval levels is borderline; the differenced model is the one to rely on.
- Granger lags limited to 1–3 months.

**Files.** `analysis.py` (re-run with `.venv/bin/python -I .../11_approval/analysis.py`); `results.json`; `lag_correlations.csv`; `monthly_panel_primary.csv`; `monthly_panel_full_2009-01_2017-01.csv`; `approval_weekly_clean.csv`; `validation_vs_published_gallup.csv`; `approval_vs_afghan.png`; `SOURCES.md`; `raw/` (UCSB HTML and parsed CSV; Google Sheet exports checked).
