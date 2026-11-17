# Review: 09_troops (reviewer notes, 2026-11-16)

Scope: re-ran analysis.py, read code, checked inputs, spot-checked external sources. Analyst files not modified. Reviewer scratch in output/analyses/09_troops/reviewer_scripts/ (check.py, check2.py) and downloads in output/analyses/09_troops/reviewer_scripts/downloads/.

## 1. Reproduction

analysis.py re-run with the venv python (-I) completes and regenerates results.json. Every key number in the task matches results.json:
- Quarterly level r combat share -0.432 (p=0.0153), Spearman -0.331 (p=0.0685).
- Quarterly level r HL volume 0.413 (p=0.021); all-passage volume 0.467 (p=0.008).
- First differences: combat share r=-0.195 (p=0.303); HL volume r=0.172 (p=0.363).
- Troops ACF(1)=0.945; Ljung-Box(4) p reported as 0.0 (rounds to <0.0001).
- CCF combat share, lag +1: r=0.267, Bartlett p_adj=0.0608.
- HAC OLS combat share ~ dTroops(t-1): beta 5e-6 (results.json, n=28), p_HAC=0.0085, R2=0.074, n=28.
- Lead spec p_HAC=0.797; CCF lag -1 r=-0.033 (p=0.818).
- Monthly 2009-01..2010-09: HL volume r=0.072 (p=0.757); combat r=0.187 (p=0.418).
- Threshold 30/50/70 level volume r: 0.446/0.413/0.349; combat r: -0.369/-0.432/-0.324. All difference-based p >= 0.30.
- n: 31 quarters (levels), 30 (diffs), 28 (lagged OLS), 21 monthly. Questioner flag 109. HL per quarter 19 (2016Q1) to 334 (2010Q2). All confirmed.

Note on beta: results.json gives 5e-6 for the n=28 spec (the sample is trimmed by the lead term via dropna). My recompute without the lead term (n=29) gives 4.5e-6. Sample difference only, not an error.

## 2. Code review

Checked and OK:
- Dup filter: speeches_index.dup_of is entirely empty (0 non-null). Exclusion is a no-op. Result correct but the step does nothing.
- Speech IDs: all 4,741 reference speech_ids exist in speeches_index.
- Questioner flag: 109 passages, every one contains token questioner_not_president. No false matches found.
- CCF sign convention: for k>=0 uses dTroops.shift(k) (troop change at t-k) vs dRhetoric at t. Label "lag +1" = troop change previous quarter. Correct.
- Lead spec uses dTroops.shift(-1) (t+1). Correct.
- Quarterly calendar mapping (FY Q2 = Mar snapshot etc.) is consistent. Spot-checked against monthly Table A-1 at matching quarter ends: Mar 2009 38,350; Jun 2009 55,100; Sep 2009 62,300; Dec 2009 69,000 match in both sources.
- R44116 parse: 37 rows FY07Q4-FY16Q4. Q1 FY2014 row has a stray comma in the Contractor column ("78,136,") in the text extract; the Armed Forces column (43,300) is unaffected.
- Quarterly panel contiguous 2009Q1-2016Q3 (31 quarters, no gaps), so diff() is valid.
- Threshold sensitivity reported in full (30/50/70), not just the best one. No evidence of threshold p-hacking; 50 is a sensible default.

Problems:
1. MAJOR. Level correlations are trend artifacts. Troops fall monotonically after 2010 (corr with time = -0.77) and combat share drifts up (corr with time = +0.43). Partial r of troops vs combat share controlling for linear time = -0.174 (p=0.35). Troops vs HL volume controlling for time = 0.075 (p=0.69). The headline level r values do not survive a trend control. RESULT.md line 78 says "Level associations are real in the data but confounded by trend". That wording overstates. They are not established as real.
2. MAJOR. The one nominal lag result is fragile. Re-running the same spec (dx1 on dCombat) gives: HAC(2) p=0.0098 (n=29, no lead term); HAC(1) p=0.027; HC3 p=0.169; with a linear time trend added, HAC(2) p=0.015. Holm adjustment across the 12 reported OLS specs gives p=0.102. Bartlett CCF p=0.061. With n=28 and maxlags=2, the HAC estimator is unreliable; HC3 is the more defensible check and it is not significant.
3. MAJOR (interpretation). "Rhetoric does not show a lead" should read "no evidence of a lead". With n=28 and wide CIs, the lead tests have little power to detect a lead. Null is not evidence of absence.
4. MINOR. Frames are matched on passage + context_before + context_after (analysis.py line: refs["text"]), but HL membership is decided on final_score_pct for the passage only. Context may contain interviewer or questioner text. Not quantified. Recommend a passage-only frame check.
5. MINOR. Frame regex terms are broad: "train(ing|ed|s)?" matches 14.1% of HL passages and "taliban" 14.5% (my count). "train" catches generic training language, not only Afghan security-force training. "surge" is only 1.2% of HL passages, so it is not a meaningful confound (checked: dropping it changes combat level r from -0.432 to -0.457).
6. MINOR. Monthly check (n=21) includes modeled values: Aug 2009 interpolated (no flag in table, only in note); Jul, Aug, Sep 2010 flagged "b" (CRS estimates); Jun 2010 printed unflagged but described in the source note as a CRS estimate. So 5 of 21 monthly troop values are not DoD counts. The monthly check adds little beyond the quarterly result.
7. MINOR. Multiplicity. Level tests: 6 series x 2 tests. Difference tests: same. CCF: 9 lags x 6 series, no correction. OLS: 12 specs. The reported p-values are naive. The analyst states this. Ok.
8. MINOR. Bartlett effective-n uses a single AR(1) acf per series, not a lag-specific adjustment. Approximate; acceptable for a screen, not for a claim.

## 3. External spot-checks (fetched this session)

- Fetched https://www.congress.gov/crs_external_products/R/PDF/R44116/R44116.11.pdf and https://www.everycrsreport.com/files/20110329_RL33110_be1a00c99d668bee3b4ec4f6fc82e914f62c39f0.pdf with curl (generic UA) into a fresh folder. SHA-256 matches the analyst's copies in raw/ exactly (0407abba... and 5382ca28...). The R44116 v11 cover reads "Updated April 28, 2017".
- R44116 Table 1 values confirmed in pdftotext output: Q2 FY2010 = 79,100; Q2 FY2015 = 9,100; Q3 FY2016 = 9,365; Q1 FY2017 = "Not Yet Available". Match the derived CSV.
- RL33110 Table A-1 Afghanistan row confirmed: Mar 2010 = 85,000; Jun 2010 = 91,775 (no flag); Jul 95,925b, Aug 95,920b, Sep 98,000b. Aug 2009 = 62,600 (interpolated per source note, no flag in table). Matches monthly CSV.
- Source note text quoted in SOURCES.md matches the PDF (interpolation for Oct/Nov 2008 and Aug 2009; CRS estimates for Jul-Sep 2010; "DOD plans for average strength of 84,000").
- Not checked: policyarchive.org copy (said to match 2009-2010; not fetched). Brookings PDFs (described as chart-only; not fetched). Their use in the analysis is nil, so this does not affect results.

SOURCES.md completeness: adequate. Gaps: does not list the exact pdftotext command options beyond "-layout", and does not state the fetch date per file (only the top-level retrieval date). Calendar mapping is labeled as analyst derivation, which is correct.

## 4. Verdict

Numbers reproduce. Strength should be downgraded from "weak" to "inconclusive". The level associations are trend artifacts. The lagged-troop result is nominal, unstable across estimators (HAC p 0.0085 vs HC3 p 0.17), does not survive Holm across the 12 specs (p 0.10), and the Bartlett CCF is p 0.06. No robust link between troop levels and rhetoric. Null for contemporaneous changes. Lead direction: no evidence, low power.

Suggested replacement wording:
"No robust association between US troop levels in Afghanistan and the frame shares or mention volume of Obama-speech Afghanistan passages (2009-2016, n=31 quarters). Level correlations reflect a shared post-2010 trend (partial r with time, combat share: -0.17, p=0.35). First differences show no significant contemporaneous association (all p >= 0.20). One nominal association (combat share vs prior-quarter troop change, HAC p=0.0085) is not robust (HC3 p=0.17; Holm across 12 specs p=0.10). Exploratory only. No evidence rhetoric leads posture changes; power is low."

## Actions

- Rewrite RESULT.md finding and strength (analyst's call; reviewer did not edit).
- Replace "Level associations are real" with the time-trend wording above.
- Report HC3 alongside HAC.
- Optional: passage-only frame re-run to address context leakage.
