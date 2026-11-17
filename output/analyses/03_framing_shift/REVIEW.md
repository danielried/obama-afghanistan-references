# REVIEW of 03_framing_shift (reviewer notes)

Reviewer re-run and checks. Analyst files were not modified. Reviewer scripts live in `output/analyses/03_framing_shift/reviewer_scripts/` (check.py, check2.py, check3.py).

## 1. Reproduction
- `analysis.py` re-run with `venv/bin/python -I`: exit 0. Output log matches the original `run.log` line for line (excluding the "wrote" line).
- All key numbers reproduce: period shares and chi2 p-values (end 0.038/0.123/0.046, p=6.65e-25; transition 0.115/0.159/0.147, p=0.00026; war_direct 0.431/0.489/0.472, p=0.0011; war_adjacent p=0.035; combat p=0.61), event match (±30 d 6 of 12, null mean 2.98, p=0.0537; ±60 d p=0.4493).
- Reviewer's independent regex copy with pandas reproduces the end-frame counts (80/2100, 221/1804, 31/678), transition counts, and the main-sample n (4,582 after excluding 104 questioner rows and 11 Jan-2017 rows).

## 2. Data filters
- dup_of: none non-empty in speeches_index.csv, so no dedupe applied. Correct for this file.
- Refs dates agree with speeches_index dates (0 mismatches). Multi-line CSV parse fine (4,741 rows, 23 columns).
- Questioner flag: `rationale` contains `questioner_not_president-18` in 109 rows total, 104 among the four categories. Filter is correct.
- Era/window filters correct (2009-01-01..2016-12-31; 2017 rows excluded).
- 140 rows (47 distinct passage texts) repeat across speech_ids that are not marked dup_of. Deduping by passage text leaves all period results essentially unchanged (END 0.038/0.120/0.047, p=9.4e-23; TRA 0.116/0.164/0.152, p=9.6e-5; war_direct 0.434/0.496/0.488, p=3.4e-4). Not a driver, but a data-hygiene gap.

## 3. Code review (analysis.py)
- Pettitt: formula and V_i/U_t construction look right for a binary x (V_i = n0 for x=1, -n1 for x=0). Approx p is anti-conservative under clustering, as the analyst says.
- Binseg: splits only at month boundaries (correct), min 30 per side, permutation within segment. Permuting within segment ignores autocorrelation and speech clustering. Caveat is correct.
- Event match: the Monte Carlo null draws 12 uniform dates, but the observed set is data-selected and clustered (2012 cluster repeats across series). Null is not matched to that structure, so the ±30 d p=0.054 is loose, not a clean test. Not significant at alpha 0.05 by the analyst's own threshold.
- Multiple comparisons: 7 series x 5 subsets, no correction. Break set is a union across series. Any "robust break" claim is a count of recurrences, not a test.
- Frame regex bugs and confounds (most important, see section 4): the end regex has no Iraq exclusion; `withdraw*`, `end of the war` and `troops home` also fire on Iraq-withdrawal passages.
- Threshold choice: subsets >=30/50/70 are reported as sensitivity, not as selected. Break-date recurrence across them is weaker than presented (e.g., war_direct >=70 has 5 breaks, Pettitt p=0.096; transition break 2010-07-01 appears only in >=30/50/70 and in main, fine).
- Chi-square tests on passages treat passages as iid. Anti-conservative. Reviewer's speech-cluster bootstrap (resampling speeches, B=3000) is still strongly significant for the main contrasts (see below), so the period contrast survives clustering. The break p-values were not re-tested with clustering.

## 4. Substantive confounds found by reviewer
- Iraq contamination of the end frame. Of 332 END-frame hits in the main sample, 111 (33%) passages mention "Iraq" (case-sensitive). By year: 2011 25/48, 2012 48/155. The END share with Iraq-mentioning passages removed: 2009-11 0.018, 2012-14 0.086, 2015-16 0.041 (chi2 p=5e-22). So the 12-14 share falls from 12.3% to 8.6%. The absolute gap vs 2009-11 shrinks from 8.5 pp to 6.8 pp. The ratio vs 2009-11 is about 3.2x with Iraq and about 4.8x without, because the 2009-11 base also falls (3.8% to 1.8%). The shift survives, but the headline 12.3% is inflated by roughly 30% of the 12-14 excess.
- The 2011 end-frame break region (2011-06 to 2012-02) is largely Iraq-withdrawal period. Monthly END counts with/without Iraq (2011-01..2012-12): 2011-03 3 (0 w/o Iraq), 2011-08 7 (2), 2011-10 5 (1), 2011-11 11 (6), 2012-01 6 (3). The break at 2011-06-07 and 2011-09/2012-02 segments were not re-run without Iraq. The analyst's 2011-2012 "end" break cluster should be treated as partly Iraq-driven and untested.
- Campaign-season confound (hypothesis, not verified). END share in monthly 2012-06..2012-10 is 0.23-0.28 (with Iraq), 0.09-0.22 (w/o Iraq); 2012-11 drops to 0.057 (n=70) after the November election. "Withdraw/home" rhetoric in campaign speeches could explain much of the 2012-14 bump. Speech type (campaign remarks vs official) was not checked. The period 2012-14 mixes campaign and governing months, so the "2012-14" label hides this.
- Concentration. 2012-05 has 300 passages but 157 come from three speeches (Enduring Strategic Partnership joint statement 81, Bagram address 42, Chicago presser 34). The 2012-06 war_direct break is plausibly driven by these speeches. END hits in 2015-16: 9 of 31 from one speech (DCPD-201500196), top-5 share 0.55, so 2015-16 END rate (4.6%) is one speech's worth of signal.
- Transition frame is driven by the word "transition" (2009-11 107, 2012-14 169, 2015-16 13 passage hits). "train" falls 102 -> 54 -> 38 over the same periods. The frame is a token lexicon, not stance. The 2010-07 break is not checked against term composition.
- Dedupe, speech clustering and the term check do not reverse any period contrast.

## 5. Cluster bootstrap (speech resampling, B=3000, reviewer code)
- END all, 12-14 minus 09-11: diff 0.084, 95% CI [0.061, 0.110].
- END excl Iraq: diff 0.068, 95% CI [0.051, 0.087].
- TRA: diff 0.044, 95% CI [0.018, 0.068].
- war_direct: diff 0.058, 95% CI [0.018, 0.098].
Conclusion: period-level contrasts are not an artifact of passage iid assumption at the level of speech clusters, but CIs are over a narrow set of speeches in 2012 (183 distinct END speeches in 12-14, so the clustering is not extreme).

## 6. Numbers verdict
- Reproduces exactly.
- Independent checks match (counts, shares).
- Headline "end frame triples in 2012-14" should be stated as "rises from 1.8% to 8.6% when Iraq-mentioning passages are removed (12.3% with them)".
- "Breaks in 2011-2012 recur across thresholds" is not evidence of a shift: the recurrence is over a small, overlapping set of permutation tests with no multiplicity control, and the 2011-12 cluster is Iraq-contaminated.
- "Stable break near July 2010" (transition) is a single binseg hit at p=0.002 in the main sample and dominated by the word "transition" and falling "train". Report as descriptive only.
- Event alignment: ±30 d p=0.054 is not significant at the analyst's own alpha; ±60 d p=0.45. The "drawdown-era turn" wording is over-read.

## 7. Recommended edits to RESULT.md (analyst to make; reviewer did not edit)
1. Re-run END frame with Iraq-mentioning passages removed (or add an Iraq-exclusion frame) and re-run the 2011-2012 break detection on it.
2. Add a campaign-season flag (or split 2012-06..2012-10 from 2012-11..2014) and report the period contrast with and without it.
3. Report speech-cluster bootstrap CIs next to the chi2 p-values.
4. Re-state the event match as not significant at alpha 0.05 and remove "robust" language for breaks.
5. Drop or qualify "triples" (use 1.8% -> 8.6% ex-Iraq, 3.8% -> 12.3% with Iraq).

## Verdict
Reproduces. Period-level END and TRA contrasts survive the checks, but the headline end-frame magnitude is inflated by Iraq contamination, and the break-level and event-alignment claims are weak. Strength for the period contrast: moderate. Strength for the break and event claims: weak.
