# 08_casualties: US military deaths vs Afghanistan rhetoric (2009-2016)

**Question.** Do monthly US military deaths in Afghanistan predict monthly volume or tone of high-likelihood Afghanistan passages in Obama presidency speeches?

## Data
- Passages: `output/references.csv` (4,741 rows). Excluded 109 questioner-flagged passages (`rationale` contains `questioner_not_president`). High-likelihood = `final_score_pct >= 50`: 3,868 passages.
- Speech universe: `speeches_index.csv`, non-duplicate (`dup_of` empty; none in file), status ok, dated 2009-01..2016-12: 5,008 speeches. Rate = HL passages / speeches in month (per speech). Zero-HL months: 0.
- Casualties: monthly US deaths, DoD OEF/OFS all theaters, 96 months, total 1,752. Source is the Wikipedia table (secondary, DoD-attributed). The primary DCAS pages were not readable by WebFetch (dynamic). Annual cross-check vs CRS R41084: 2009 311 = 311; 2010 498 vs 499; 2011 411 vs 414.
- Coalition (non-US) monthly deaths: not obtained. Afghanistan-only iCasualties: not obtained (404).

## Method
- ADF (constant, AIC lags) on levels and first differences.
- First-differenced cross-correlations, lags -6..+6, Pearson, with Bonferroni-adjusted p.
- Granger causality both directions on first differences, lags 1-6 (statsmodels, F and chi2). The AIC-selected lag was 6 (the maximum) for every pair, so selection is at the boundary.
- Sensitivity: thresholds 30/50/70, per-speech and per-1,000-words normalization.
- Robustness: OLS residuals after linear trend plus month-of-year dummies, then the same CCF and Granger.
- Tone = mean VADER compound of HL passages. This is word valence, not stance.

## Numbers
| Check | Result | n | p |
|---|---|---|---|
| ADF deaths, level | stat -0.20 | 96 | 0.94 (non-stationary) |
| ADF deaths, diff | stat -2.57 | 95 | 0.099 (borderline) |
| ADF rate/speech, level | stat -10.43 | 96 | <0.0001 (stationary) |
| Spearman deaths vs rate, levels | rho 0.32 | 96 | 0.0014 (confounded by shared decline) |
| Partial r deaths vs rate, trend+month controlled | r 0.001 | 96 | 0.99 |
| Spearman deaths vs tone, levels | rho 0.10 | 96 | 0.36 |
| CCF diff, deaths vs rate, max abs r | lag -2 r 0.18 | 93 | 0.083 |
| CCF diff, lag 0 | r 0.025 | 95 | 0.81 |
| Granger deaths->rate, lags 1-6 p_F | 0.94, 0.52, 0.91, 0.90, 0.76, 0.83 | 89-94 | all n.s. |
| Granger rate->deaths, lags 1-6 p_F | 0.24, 0.28, 0.32, 0.47, 0.61, 0.65 | 89-94 | all n.s. |
| Granger deaths->tone, lags 1-6 p_F | 0.77 to 0.31 | 89-94 | all n.s. |
| Sensitivity (thr 30/50/70, both norms) lag-0 diff r | -0.004 to 0.048 | 95 | all p >= 0.64 |
| Residual robustness CCF, max abs r | lag -2 r 0.25 | 93 | 0.015 (unadjusted; 0.19 Bonferroni) |
| Residual robustness Granger rate->deaths | lag 6 p_F 0.025; lags 1-5 p 0.07-0.17 | 89-94 | weak, lag-6 only |

Other: contemporaneous change in HL rate vs change in mean tone, r = 0.28, p = 0.006 (Bonferroni 0.23). This is word valence and does not involve casualties.

## Finding
No evidence that monthly US deaths predict Afghanistan passage volume or tone in either direction, at lags 0-6 months, in these data. The raw levels correlation (rho 0.32) disappears once a shared trend and month-of-year pattern are controlled. The only nominally significant signal is a residual rate->deaths effect at lag 6 (p = 0.025), which is one of about 12 tests, is not visible at lags 1-5, and sits at the AIC boundary. Treat it as noise.

## Caveats
- Casualty series is secondary (Wikipedia, DoD-attributed) and covers all OEF/OFS theaters, not Afghanistan alone. Primary DCAS monthly data could not be read. See `SOURCES.md`.
- No coalition series. Excludes six DoD civilian deaths.
- 96 monthly observations give low power. A true effect of r around 0.2 would be hard to detect.
- Rhetoric measure depends on the rule-based scorer, tuned on 30 hand labels with no held-out set. Monthly rate is sensitive to speech count (spiky months with few speeches).
- Speech counts vary across months and drive the normalized rate. Per-1,000-word normalization gives the same null.
- Seasonality is not removed in the primary CCF/Granger. The residual check removes trend and month-of-year, and it still shows no robust link.
- Granger lag selection hit the maximum (6) for all pairs, so the AIC choice is unreliable.
- VADER tone is word valence, not stance.

## Files
`output/analyses/08_casualties/`: `analysis.py`, `casualties_monthly_dod_wiki.csv`, `casualties_annual_crs_r41084.csv`, `SOURCES.md`, `panel_monthly.csv`, `adf.csv`, `ccf.csv`, `ccf_residual_robustness.csv`, `granger.csv`, `granger_residual_robustness.csv`, `sensitivity.csv`, `numbers.json`, `casualties_vs_rhetoric.png`.
