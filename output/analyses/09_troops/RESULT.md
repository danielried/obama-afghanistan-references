# 09_troops: US troop levels in Afghanistan vs Obama-speech Afghanistan rhetoric

## Question
Do monthly/quarterly rhetoric shares (combat, transition, withdrawal frames) and mention volume in the Obama-presidency Afghanistan passages track US troop levels in Afghanistan, and does rhetoric lead or lag posture changes?

## Data
- Troops, quarterly (primary): CRS R44116 v11 (updated Apr 28, 2017), Table 1, "U.S. Armed Forces" in Afghanistan, from DoD Boots on the Ground reports. Mapped to calendar quarter-ends. Usable calendar quarters 2009Q1-2016Q3 (n=31). 2016Q4 has no value in the source.
- Troops, monthly (secondary): CRS RL33110 (Belasco, Mar 29, 2011), Table A-1. Covers Jan 2009-Sep 2010 for this analysis. Aug 2009 is interpolated; Jul-Sep 2010 are CRS estimates. No monthly Oct 2010-2016 series was obtained.
- Rhetoric: `output/references.csv` (read-only). 4,741 passages, none dup-flagged. 109 passages carry a questioner flag in `rationale` and are excluded from the high-likelihood (HL) set. HL = final_score_pct >= 50 and not questioner.
- Frames: keyword regex on passage + context (lists in analysis.py). Frames are non-exclusive. Shares are computed over HL passages per period.
  - combat: combat, fight, battle, offensive, surge, insurgen, Taliban, al-Qaeda, militant, casualt, killed, enemy, attack, firefight
  - transition: transition, handover, hand over, Afghan security/army/police/forces/troops, train*, assume/lead responsibility
  - withdrawal: withdraw, drawdown, come home, bring...home, end the war/combat mission, responsible end, leave Afghanistan, exit

## Method
- Levels: Pearson and Spearman on quarterly troops vs each series.
- Changes: first differences (n=30) for troops and each series.
- Cross-correlation of differences at lags -4..+4 with Bartlett effective-n adjustment (AR(1)). Positive lag = troop change at t-k vs rhetoric change at t (rhetoric lags).
- Autocorrelation: lag-1 ACF and Ljung-Box (lag 4).
- OLS on differences with Newey-West (HAC, 2 lags) for contemporaneous, lag-1, and lead-1 troop changes.
- Threshold sensitivity at 30/50/70. Monthly check on 2009-01 to 2010-09.

## Numbers

Quarterly, levels (n=31, naive p):

| series | Pearson r | p | Spearman rho | p |
|---|---|---|---|---|
| combat share of HL | -0.432 | 0.015 | -0.331 | 0.069 |
| transition share of HL | 0.050 | 0.79 | 0.086 | 0.65 |
| withdrawal share of HL | 0.029 | 0.88 | -0.028 | 0.88 |
| HL volume (n) | 0.413 | 0.021 | 0.386 | 0.032 |
| all-passage volume | 0.467 | 0.008 | 0.439 | 0.014 |

Quarterly, first differences (n=30):

| series | r | p | rho | p |
|---|---|---|---|---|
| combat share | -0.195 | 0.30 | -0.105 | 0.58 |
| transition share | 0.040 | 0.83 | 0.107 | 0.57 |
| withdrawal share | -0.240 | 0.20 | -0.113 | 0.55 |
| HL volume | 0.172 | 0.36 | 0.071 | 0.71 |

Autocorrelation (quarterly):
- troops: lag-1 ACF 0.945; Ljung-Box(4) p < 0.001
- combat share: ACF 0.127; LB p = 0.26
- withdrawal share: ACF 0.489; LB p = 0.077
- HL volume: ACF 0.016; LB p = 0.49

Cross-correlation, differences, Bartlett-adjusted p:
- Combat share, lag +1 (troop change previous quarter): r = 0.267, p_adj = 0.061. Lag 0: r = -0.195, p = 0.16. Lag -1 (rhetoric leads troops): r = -0.033, p = 0.82.
- HL volume, lag +1: r = -0.215, p = 0.097. Lag 0: r = 0.172, p = 0.18. Lag -1: r = 0.063, p = 0.62.

HAC OLS on differences (n=28; one of 12 specs, not corrected for multiplicity):
- Combat share on Δtroops(t-1): beta = +5.0e-6 per troop (about +2.5 pp per 5,000 troops), p_HAC = 0.0085, R^2 = 0.074
- Combat share on Δtroops(t): beta = -2e-6, p_HAC = 0.46
- Combat share on Δtroops(t+1): beta = +1e-6, p_HAC = 0.80
- Withdrawal share on Δtroops(t): p_HAC = 0.070
- HL volume: all specs p_HAC between 0.095 and 0.65

Threshold sensitivity (quarterly levels, n=31):

| threshold | HL vol r (p) | combat share r (p) | diff-based r, any series (p) |
|---|---|---|---|
| 30 | 0.446 (0.012) | -0.369 (0.041) | all p > 0.35 |
| 50 | 0.413 (0.021) | -0.432 (0.015) | all p > 0.30 |
| 70 | 0.349 (0.054) | -0.324 (0.075) | all p > 0.32 |

Monthly, 2009-01 to 2010-09 (n=21 levels; n=20 diffs):
- HL volume: levels r = 0.072 (p = 0.76); diffs r = 0.025 (p = 0.92)
- Combat share: levels r = 0.187 (p = 0.42); diffs r = -0.333 (p = 0.15)
- Transition share: levels r = 0.353 (p = 0.12; rho = 0.43, p = 0.052); diffs r = -0.253 (p = 0.28)
- Withdrawal share: levels r = 0.090 (p = 0.70); diffs r = -0.177 (p = 0.45)

## Finding
Level correlations are positive for volume and negative for combat share, but these mostly reflect shared trend. Troop levels are highly autocorrelated (ACF 0.95), so naive level p-values are not valid. On first differences, no contemporaneous association between troop changes and rhetoric shares or volume is significant (all p >= 0.20). The one nominally significant result is weak: a one-quarter-lagged troop change predicts the change in combat-frame share (HAC p = 0.0085, R^2 = 0.07). The Bartlett-adjusted cross-correlation at the same lag is only p = 0.06, and the result is one of 12 uncorrected specs. Rhetoric does not show a lead over posture changes (lead specs p = 0.80 and 0.82). The data are weakly consistent with rhetoric reacting about one quarter after troop changes, but this is exploratory and not robust.

Strength: weak / inconclusive for lead-lag. Null for contemporaneous differences. Level associations are real in the data but confounded by trend.

## Caveats
- Small n: 31 quarters, 28 usable for lagged regressions, 21 months in the monthly check. Per-quarter HL counts range from 19 (2016Q1) to 334 (2010Q2), so shares in small quarters are noisy.
- Monthly troop data end Sep 2010. Jul-Sep 2010 and Aug 2009 are CRS estimates or interpolations. The monthly and quarterly CRS series disagree for some dates (e.g., Mar 2010: 85,000 monthly vs 79,100 quarterly). The quarterly series is used as primary.
- Calendar quarter-end snapshot mapping is my derivation from FY quarters. Snapshot timing in the source is not explicitly stated.
- Frames are keyword rules, not validated against hand labels. Withdrawal terms can match campaign rhetoric (2012Q3 withdrawal share = 0.63 on 162 HL passages), and frame terms are not Afghanistan-specific. The Iraq context guard used in score.py is not applied here.
- VADER tone was not used in this analysis (word valence, not stance).
- Naive p-values in the level and difference tables ignore multiplicity across all tests run.

## Files
- `analysis.py` (run: `.venv/bin/python -I .../09_troops/analysis.py`)
- `results.json`, `run.log`, `quarterly_panel.csv`, `monthly_panel.csv`, `quarterly_table_for_report.csv`
- `troops_quarterly_CRS_R44116_Table1.csv`, `troops_monthly_CRS_RL33110_TableA1.csv`
- `troop_vs_rhetoric.png`
- `SOURCES.md`
- `raw/` (CRS PDF and text extracts; Brookings PDFs examined, not used)
