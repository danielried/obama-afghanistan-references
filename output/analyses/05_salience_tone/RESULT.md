# 05 Salience vs tone (monthly)

**Question.** Does the monthly salience of high-likelihood Afghanistan passages (count per speech) move with the mean VADER tone of those passages? Checked on detrended levels (primary), first differences (secondary), and lags -3..+3.

**Data.**
- `output/references.csv`: 4,741 passages. 109 flagged `questioner` in rationale, excluded (they are not the President's words).
- `output/speeches_index.csv`: 5,026 speeches. Denominator: `status == ok`, empty `dup_of` (5,023; no duplicates flagged; 3 `missing`).
- 97 months, 2009-01 to 2017-01. No zero-speech months. 3,877 high-likelihood (>=50) passages.

**Method.**
- Salience = high-likelihood passages in month / speeches that month. Tone = mean VADER compound of those passages (word valence, not stance).
- Primary: OLS-detrended levels, Pearson and Spearman.
- Secondary: first differences. Also a circular-shift permutation p (2,000 shifts) to respect serial dependence.
- Effective n: Bartlett-type `n (1 - r1x r1y)/(1 + r1x r1y)`. Approximate.
- Lags: corr(x_t, y_{t+k}), k = -3..+3; k > 0 means salience leads tone.
- Why first differences are secondary: level ACF1 is small (salience -0.078, tone +0.098) and trends are tiny (salience -0.0058/month, tone -0.0012/month). Differencing near-white series mechanically creates lag ±1 cross-correlation of about -0.5 times the lag-0 value. The lag ±1 negatives below are consistent with that artifact. Differencing also makes each spike month enter two differences, which inflates the lag-0 r. This is an interpretation; it was not separately simulated.

**Numbers (thr 50, questioners excluded).**

| Analysis | n | Pearson r | p | Spearman rho | p |
|---|---|---|---|---|---|
| Levels (raw) | 97 | 0.184 | 0.071 | 0.161 | 0.116 |
| **Detrended levels (primary)** | 97 | **0.158** | **0.121** | 0.083 | 0.421 |
| First differences (secondary) | 96 | 0.279 | 0.006 (eff-n 0.037; circ-perm 0.008) | 0.190 | 0.064 |
| Detrended, lag -3 / -2 / -1 / +1 / +2 / +3 | 93-97 | -0.199 / -0.063 / -0.159 / -0.093 / 0.028 / -0.142 | all p > 0.05 | | |
| First diff, lag -1 / +1 | 95 | -0.204 / -0.183 | 0.048 / 0.076 (artifact, see above) | | |

**Threshold sensitivity (detrended levels, lag 0).**

| Variant | n | Pearson r | p | Spearman rho | p |
|---|---|---|---|---|---|
| thr 30 | 97 | 0.258 | 0.011 | 0.246 | 0.015 |
| thr 50 (primary) | 97 | 0.158 | 0.121 | 0.083 | 0.421 |
| thr 70 | 97 | 0.045 | 0.666 | | |

Raw levels: thr 30 r = 0.274 (p = 0.007); thr 70 r = 0.069 (p = 0.50).

**First-difference robustness (lag 0).**

| Variant | n | r | p |
|---|---|---|---|
| thr 50 | 96 | 0.279 | 0.006 |
| thr 30 | 96 | 0.370 | 0.0002 |
| thr 70 | 94 | 0.019 | 0.85 |
| questioners included | 96 | 0.272 | 0.007 |
| log1p salience | 96 | 0.251 | 0.014 |
| drop months with < 5 high passages | 83 | 0.341 | 0.002 |
| drop top-3 salience months (2012-05, 2013-01, 2015-03) | 90 | 0.101 | 0.344 |

**Category-mix check (thr 50).**
- Monthly war_direct share among high passages vs salience: r = -0.276, p = 0.006 (n = 97). vs tone: r = -0.286, p = 0.005 (n = 97). Spearman vs tone rho = -0.395.
- Press-conference share of speeches vs salience r = 0.047 (p = 0.65); vs tone r = 0.059 (p = 0.56). Not related.
- Spike months are war-heavy, not diplomacy-heavy: 2012-05 (280 passages, 132 war_direct, mean tone 0.315); 2013-01 (174, 93 war_direct, 0.347); 2015-03 (164, 77 war_direct, 0.388). Speech types are mostly remarks and statements; press conferences are 1-2 per month.
- Mean tone by category among hi passages: war_direct 0.118 (n = 2,107), war_adjacent 0.246 (1,057), aid_diplomacy_civil 0.417 (206), incidental 0.152 (503). This is VADER word valence; it is higher for diplomacy and aid wording, which is consistent with a vocabulary-mix explanation for part of the tone signal.

**Finding.** Weak, and not significant on the primary spec. Detrended monthly salience and tone show r = 0.16 (p = 0.12, n = 97) at the 50% threshold, with no lag structure. The association is clearer at a lower threshold (30%: r = 0.26, p = 0.011) and vanishes at 70%. First differences give r = 0.28 (p = 0.006), but that spec is inflated by differencing and by a few spike months; the association drops to r = 0.10 when the top three salience months are removed. The category check suggests the tone signal tracks war-vocabulary share: months with a higher share of war_direct passages have lower mean tone and fewer high-likelihood passages per speech. This is word-valence evidence, not stance.

**Caveats.**
- Salience is heavy-tailed (up to 4.7 high passages per speech). Pearson on levels is sensitive to spike months.
- The 30/50/70 thresholds change the answer. The scores are rule-based estimates, not ground truth.
- VADER measures word valence on passage wording. War passages score lower on vocabulary alone.
- Monthly tone means from 1-4 high passages are noisy (for example 2013-03: n = 1). Dropping months with fewer than 5 high passages raises the first-difference r to 0.34, so the noise does not drive the result.
- Effective-n corrections are approximate, especially for differenced series.
- Multiple testing: about 7 lags times 4 variants were examined. The only lag with p < 0.05 (lag -1, first differences) is an artifact by the mechanism above.

**Files.** `analysis.py` (re-run: `.venv/bin/python -I output/analyses/05_salience_tone/analysis.py`), `results.json`, `robustness.json`, `category_check.json`, `monthly_panel_thr50.csv`, `monthly_panel_thr30.csv`, `monthly_panel_thr70.csv`, `salience_tone.png`.
