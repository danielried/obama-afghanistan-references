# REVIEW: 08_casualties (independent statistical review)

Reviewer scope: re-run analysis.py, audit code and data, spot-check external sources. analysis.py and the analyst's output files were not modified.

## 1. Reproduction
- Re-ran `.venv/bin/python -I .../08_casualties/analysis.py`. Runs in about 4 s, no errors.
- All CSV outputs and numbers.json are byte-identical to the pre-run state (md5 check). Script is deterministic.
- Key numbers reproduce exactly: ADF deaths level -0.2029 / p 0.9382; deaths diff -2.5729 / p 0.0987; rate level -10.43 / p<0.0001; Spearman deaths vs rate rho 0.3213 / p 0.0014; partial r 0.0014 / p 0.989; lag-0 diff CCF r 0.0250 / p 0.81; max |CCF| r 0.181 at lag -2 / p 0.083 (n=93); Granger p_F values match RESULT.md for all six lags in both directions and for tone; sensitivity range -0.004 to 0.048, all p >= 0.64; residual Granger rate->deaths lag 6 p_F 0.0251.
- Totals: 4,741 refs; 109 questioner-flagged; 3,868 HL non-questioner in 2009-2016 (3,877 in full file, 9 are dated 2017 and correctly excluded); 5,008 speeches; total deaths 1,752.

## 2. Code and data audit
Checked and OK:
- Speech universe: 5,026 rows, 0 non-empty dup_of, 3 status "missing", 15 in 2017. 5,023 ok, minus 15 in 2017 = 5,008. Correct.
- Passage dates match speech dates (0 mismatches). All 4,741 refs map to a speech in the index.
- Questioner flag: 109 rows flagged via rationale. Spot-check shows real questioner text. Zero unflagged passages start with Q./Question/Audience. Flagged passages are only 1.5% of HL, so this is low-impact.
- CCF shift logic: corr(x_t, y_{t+k}), k>0 = x leads. Correct.
- Granger direction: statsmodels tests whether column 2 causes column 1. Labels and calls are consistent.
- Casualty merge asserted complete. No NaN months.
- Tone interpolation for ADF/CCF is labeled in code. Interpolated and raw ADF identical.

Problems:
1. MAJOR, wrong test for data: rate_per_speech is stationary in levels (ADF p<0.0001, with or without trend). First-differencing it over-differences. The lag-1 autocorrelation of d(rate) is -0.515 (ACF checked). The CCF and Granger tests on d(rate) are therefore run on a series with a strong MA(1)-like structure. This can distort lag patterns and reduce power. Preferred: levels with trend and month-of-year controls, or a VAR in levels. The residual robustness check also differences a stationary residual series, so it has the same issue.
2. MAJOR, stationarity claim is specification-dependent. Deaths: ADF with constant only and AIC lags (max 9 lags chosen, which overfits) gives p=0.94. With trend ("ct") and fixed lags 0, 1, 3 it gives p=0.0009, 0.003, 0.001, i.e., trend-stationary. "Non-stationary in levels" is therefore not a robust finding. Deaths looks trend-stationary, not unit-root. Recommend KPSS or ADF-ct with fixed lags, and reporting the spec.
3. MAJOR, no autocorrelation or effective-n correction. CCF p-values use iid Pearson tests. d(deaths) lag-1 ACF is -0.18. Level series ACF is 0.83 at lag 1. Combined with issue 1, the nominal p-values are not calibrated. This does not change the null direction but it does make any "nominal" p (e.g., 0.025) less interpretable.
4. MAJOR, Granger lag selection at boundary. VAR AIC chose lag 6 (the max) in all four pairs. Results at lags 1-6 are reported, which is fine, but the lag range should be extended or lag selection should use BIC. The "lag 6 only" residual signal sits exactly at the boundary.
5. MODERATE, multiple testing is under-accounted. Primary family: 24 Granger F-tests, 39 CCF tests (Bonferroni applied only to CCF), 12 residual Granger tests, 13 residual CCF tests, 12 sensitivity tests. The residual Granger p=0.025 at lag 6 has Bonferroni p about 0.3 across the 12 residual Granger tests. The RESULT's "one of about 12 tests" understates this. Language is acceptable ("treat as noise") but the finding should be labeled as not surviving any multiplicity adjustment.
6. MODERATE, construct and scope. (a) Casualty series is all OEF/OFS theaters. Wikipedia notes 60 of 2,402 OEF deaths (2001-2024 range) were outside Afghanistan (Horn of Africa, Philippines, Guantanamo). Share for 2009-2016 was not computed. (b) Deaths are US only. Coalition deaths were not obtained. (c) Rhetoric scorer tuned on 30 labels. Sensitivity to thresholds is reported (good).
7. MINOR, text error in RESULT.md. Granger deaths->tone p range is written as "0.77 to 0.31". Actual p_F values: 0.774, 0.448, 0.194, 0.203, 0.251, 0.307. Minimum is 0.19 (lag 3), so the range is 0.19-0.77.
8. MINOR, causal wording. "Predict" is Granger-sense only. Finding is fine but should not be read as causal.

## 3. External spot-checks (fetched 2026-11-16, generic UA)
- Wikipedia "United_States_military_casualties_in_the_War_in_Afghanistan": "U.S. fatalities by month in all OEF/OFS theaters according to the US DoD" table. All 96 monthly cells for 2009-2016 match casualties_monthly_dod_wiki.csv exactly (0 mismatches). The page's note says the table omits six DoD civilian deaths, as SOURCES.md says.
- Wikipedia printed row totals for 2015 (21) and 2016 (10) do NOT equal their monthly cell sums (22 and 9). The analyst's CSV uses the cells (sum 1,752, matches). Printed totals across 2009-2016 also sum to 1,752, so total is unaffected. Discrepancy is not disclosed in SOURCES.md.
- CRS R41084 (everycrsreport.com, 2012-12-06), annual table: 2009 311, 2010 499, 2011 414, 2012 306 (through Dec 6). Matches SOURCES.md values for 2009 and for the CRS side of 2010 and 2011. Wikipedia sums: 2010 498 (diff -1), 2011 411 (diff -3). CRS note says "with the addition of three DoD civilian personnel" and Wikipedia says six civilians are omitted. These two civilian counts are inconsistent with each other. Attribution of the 2010/2011 differences to civilian inclusion is therefore NOT verified (SOURCES.md says "not verified", which is correct; caveat should stay).
- DCAS primary pages (dcas.dmdc.osd.mil .../oef/byMonth): fetched HTML contains only the page title "Defense Casualty Analysis System" (34 chars of text). Monthly primary values are not verifiable. Analyst's statement is accurate.
- Not verified: iCasualties (404 per SOURCES.md), Brookings, Gallup/Pew (not fetched). None of these are used in the numbers.

## 4. SOURCES.md completeness
- Covers URLs, retrieval date, scope, secondary status, and the cross-check. Complete for the data used.
- Missing: the Wikipedia row-total discrepancy (2015, 2016) and the civilian-count inconsistency (CRS three vs Wikipedia six).
- Note "Postwar OFS (2015-16) is Afghanistan-only in practice" is an unsourced assertion.

## 5. Verdict
- Numbers reproduce. Casualty input matches its cited secondary source cell-for-cell. Primary DoD not readable. CRS annual figures match for 2009 and partly for 2010-2011.
- Null finding (no lag 0-6 predictive link between US deaths and Afghanistan rhetoric volume or tone, in either direction) is consistent with the reproduced tests. But the test design has real problems (over-differenced stationary rate series, spec-dependent stationarity, iid p-values, boundary lag selection, low n=95). Power is low.
- Downgrade: analyst's strength "null_result" -> "weak" (weak evidence of absence, not a confirmed null). Residual lag-6 Granger signal is not evidence of a relation.
- Required fixes before stronger claim: levels-based or properly specified (trend, month-of-year, no over-differencing) Granger/VAR; KPSS or trend ADF; BIC lag selection with lags beyond 6 or an explicit argument; multiplicity-adjusted family; correct RESULT tone range; document Wikipedia row-total discrepancy.
