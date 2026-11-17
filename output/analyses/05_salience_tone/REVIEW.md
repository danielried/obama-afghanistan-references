# Review: 05_salience_tone

Reviewer: independent re-run and checks. Analyst files were not modified. My check code was inline (not saved to the analyst folder).

## 1. Reproduction
`analysis.py` re-runs cleanly (exit 0). results.json and robustness.json match the reported numbers:
- Detrended levels thr50: r=0.1584, p=0.1212, n=97 (Spearman 0.083, p=0.421)
- Raw levels thr50: r=0.1843, p=0.0707
- First diff thr50: r=0.2787, p=0.006, n=96; eff-n p=0.037; circular-shift perm p=0.008
- Thr30 detrended r=0.258 (p=0.011); thr70 r=0.045 (p=0.666)
- Drop top-3 salience months, FD: r=0.101, p=0.344, n=90
- Lag -1 FD r=-0.204, p=0.048

## 2. Independent recompute (own code)
Rebuilt the monthly panel from raw references.csv and speeches_index.csv without the analyst's functions. Matches:
- Detrended r=0.15841, p=0.12119; Spearman 0.0827, p=0.4206
- FD r=0.27871, p=0.00597
- Raw r=0.18434, p=0.0707

## 3. Input and filter checks
- refs date == speech index date for all 4,741 rows (0 mismatches). Month alignment correct.
- dup_of is empty for every speech, so the dup filter is a no-op. No refs point at non-ok speeches.
- 109 questioner rows flagged by rationale text. Zero unflagged Q./Question/Audience-style passages found.
- 97 months, 0 zero-speech months, 3,877 hi passages after exclusion (3,935 before).
- Spike months are not small-denominator artifacts: n_speeches 60 (2012-05), 41 (2013-01), 46 (2015-03), vs median 51.
- 2013-03 has n_hi=1 (tone 0.45), as RESULT says.

## 4. Checks on the permutation and effective-n
- **Circular-shift permutation.** For FD there are only 96 distinct circular shifts. Enumerating all 96: the observed alignment is the strict maximum (count=1), so exact p = 1/96 = 0.0104. The reported 0.008 is Monte Carlo noise from 2000 random draws, below the exact floor. Real but coarse: p is about 0.01, and the observed alignment beats every other shift.
- **Effective-n.** FD ACF1 is -0.515 (salience) and -0.506 (tone). Analyst formula n(1-ab)/(1+ab) gives 56.3. The MA(1)-form n/(1+2ab) gives 63.1. Both are approximate; the direction (shrink n) is correct. Minor.
- **Lag-0 identity for FD (raw levels).** Cov of differences expands to 2c0 - c(+1) - c(-1) over 2*sqrt((1-acf_x1)(1-acf_y1)). Using raw cross-lags c0=0.184, c(+1)=-0.060, c(-1)=-0.119: (0.368+0.060+0.119)/1.972 = 0.2774, observed 0.2787. So FD r is the level lag-0 r (0.184) plus about +0.09 from the negative neighbouring cross-lags. The FD inflation is concrete: it comes from the non-significant negative level lags, not from the signal itself.
- **Lag +/-1 FD artifact.** A simple -rho/2 heuristic predicts about -0.09; observed -0.18 and -0.20. So the lag +/-1 values are mechanically linked to level structure but the "artifact" label is only partly supported. At p=0.048 with about 28 tests, it is not meaningful.

## 5. Issues
**Major**
1. **Mix confound untested; the partial correlation shrinks the association.** War_direct share correlates with salience (r=-0.276) and with tone (r=-0.286). Controlling for it: levels r 0.184 to partial 0.114 (p=0.27); detrended r 0.158 to partial 0.105 (p=0.31). The analyst reports only the marginal correlations and says the mix "suggests" a tone explanation. The partial is the appropriate test, and it is null.
2. **Wrong spike-month claim in RESULT.md.** RESULT says "Spike months are war-heavy". War_direct share in spike months is 0.471 (2012-05), 0.534 (2013-01), 0.470 (2015-03). Overall share among hi passages is 0.543. Spike months are below average on war share. The corrected fact reinforces point 1: the spike months are the ones with the lower war share and higher mean tone (0.315, 0.347, 0.388 vs overall mean), which is what a vocabulary-mix effect on VADER would produce.
3. **Threshold dependence with no correction.** Significant at thr30 (p=0.011), not at thr50 (p=0.12), not at thr70 (p=0.67). The result depends on threshold. Across about 28 tests (thresholds x specs x lags) no multiplicity correction is applied.

**Minor**
4. **Robustness filter "drop months with fewer than 5 high passages".** It sets tone to NaN in low-n_hi months. n_hi = salience x n_speeches, so this selects on something correlated with x. The jump to FD r=0.34 is partly selection. RESULT's claim that "noise does not drive the result" overstates it.
5. **Spike sensitivity.** Removing the top-3 salience months drops FD to r=0.10 (p=0.34). The permutation p (about 0.01) uses all months and does not address this. The FD association is carried by a few months.
6. **Effective-n and permutation floor.** See section 4. Approximate, not wrong in direction.
7. **Questioner inclusion.** Detrended r becomes 0.148 (p=0.147). Immaterial.

Not an issue: spec choice. The analyst's stated reason for detrended primary (level ACF1 about 0, so differencing is unnecessary) is defensible. The multiplicity point is what matters, and the analyst already flags it.

## 6. Verdict
- Primary spec (detrended, thr50): not significant (p=0.12). Mix-adjusted: not significant (partial p=0.31).
- FD association (p=0.006; perm about 0.01) is real in the arithmetic but carried by a few spike months, and inflated by negative neighbour cross-lags. Without the top-3 months p=0.34.
- Only thr30 is significant on the detrended spec. That is threshold selection, not robust.
- **Strength: null_result.** No reliable monthly salience-tone association. Do not report FD p=0.006 as a finding. Correct the RESULT.md "war-heavy spike months" sentence before use.
