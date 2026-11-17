# REVIEW 01_venue (independent re-check, reviewer pass)

Re-ran: `.venv/bin/python -I .../01_venue/analysis.py` exit 0. Note: the rerun overwrote the analyst's output files in place (results.json, CSVs, chart_venue.png). Headline numbers matched the analyst's values; I did not diff the files byte-for-byte.
Reviewer scripts (outside analyst folder): output/analyses/01_venue/reviewer_scripts/check.py, check2.py, check3.py.

## Reproduction: PASS
All headline numbers reproduce: KW score H=145.9 p=2.9e-28; KW tone H=428.1; category chi2=208.5 V=0.105; HI>=50 chi2=207.6 V=0.209; rates (remarks 0.726, press|president 1.887, statement 1.772, address 1.927, weekly 0.603); NB GLM IRR press 2.435, address 3.311, statement 1.440, interview 2.970, weekly 0.790; questioner median 53.5 vs 71.0; venue_title-removed KW H=131.95.
Independent csv-module parse: 4741 rows, multiline fields OK. final_score_pct == round(rule_score) for all rows (llm blank). index hit_count == refs count for all 1107 speeches with refs. dup_of: none non-empty.

## Errors / overclaims
1. **MAJOR, finding text wrong.** Finding says mention rates are "about 2.4-3.3x higher in press conferences, addresses, and statements". GLM IRR for statements is 1.44 [1.18, 1.76]. 2.4 is press conferences only; 3.3 is addresses only. Crude statement rate ratio is 2.44 (1.772/0.726), which disagrees with the GLM; write-up does not mention this.
2. **MAJOR, address rate result depends on one speech (influence diagnostic).** Top-3 speeches per type are 38% of press-conference passages, 42% of address, 37% of statement. One address speech (DCPD-201200336) holds 42 of 206 passages. Dropping the top-3 passage-heavy speeches per type (same NB GLM spec): address IRR 3.31 -> 1.55 [0.78, 3.09] p=0.21; press_conference 2.44 -> 1.66 [1.15, 2.38] p=0.006; statement 1.44 -> 1.31 [1.07, 1.61] p=0.010. Crude rates excl top-3: press 1.85 -> 1.17, statement 1.77 -> 1.14, address 1.93 -> 1.17, remarks 0.73 -> 0.68. Caveat: this trim removes 3 of 31 address speeches but 3 of 825 remarks speeches, so it is not a neutral test. Treat as influence diagnostic, not a corrected estimate. Weekly_address change under trim (0.79 -> 0.61, p=0.004) is an artefact of the same selection; not reported as a finding.
3. **MAJOR, score gaps sensitive to specification.** Passage-level OLS, SE clustered by speech (check2.py). Type only: address +9.4, press +4.8 (p<0.001), statement +4.6 (p=0.004). Adding year FE and log(hit_count): press -1.96 (p=0.15), statement +0.70 (p=0.62), address +6.6 (p=0.0002), weekly +5.2 (p=0.011). Adding venue_title dummy: press -0.68 (p=0.66), statement +0.09 (p=0.95). Only the address gap persists. log(hit_count) is a scorer input and plausibly a consequence of venue (post-treatment), so this is a sensitivity result, not a correction.
4. **MAJOR, circularity under-addressed.** Analyst removes only venue_title (+4) and questioner (-18). score.py also gives speech_focus_8+/3+ hits (+10/+6, speech-level, tied to speech length) and in_administration (+5) / near_inflection (+8) by date. Not sensitivity-tested. Venue-score effects are partly built into the scorer.
5. **MINOR, questioner split incomplete.** 25 questioner-labelled passages (remarks 24, other 1) stay in remarks/other; method text says Q&A answers are split. Effect small; should be disclosed.
6. **MINOR, inconsistent rate denominators.** Split groups (press|president, press|questioner, interview|*) use speaker/questioner paragraph chars (exclude editor NOTE text); whole-type rates use full raw_len incl. editor notes. Small, but not like-for-like.
7. **MINOR, n reporting.** data_used says 5026 speeches with 0 dup_of; n field says 5023. Reason: 3 speeches with raw_len 0 dropped in GLM (text_len>0 filter). Should be stated.
8. **MINOR, rank-stability claim loose.** "High-likelihood share ranking is stable across 30/50/70." Ranks change (e.g., weekly_address 0.845 at >=50 vs press|president 0.926; at >=70 weekly 0.588 > press 0.551, reversed vs >=50 order). Only the extremes (address top, other bottom) hold across thresholds.
9. **MINOR, multiple-test scope.** Holm within each outcome family; no correction across the 4 outcome families. Fine for descriptive use.
10. **Clustering / p-values.** Mann-Whitney, KW and chi-square treat passages as independent (analyst notes this). Speech-level check (one mean score per speech; 1102 speeches across 6 groups with n>=10 speeches; "other" excluded at 5 speeches): KW H=59.96 p=1.2e-11. Venue-to-score difference is real at speech level but small.
11. **UNVERIFIED, VADER tone.** vaderSentiment not installed in the venv; tone values not recomputed. Tone numbers reproduce from the stored column only.

## Checks that passed
- Dup filter: correct (no dup_of rows).
- Questioner label: para_label == questioner matches rationale flag exactly (109/109, 0 off-diagonal).
- Passage spans inside labelled paragraphs: 100%. Editor-labelled passages in refs: 0.
- Multiline CSV parse: row count matches csv module.
- KW eta2_H, Holm, chi-square, Poisson CI formulas read correctly.
- NB GLM: exposure handled as log offset by statsmodels; LR df = 6 type dummies. Correct.

## Verdict
Reproduction clean. Interpretation overreaches. Venue effect on score is real but small (eta2_H 0.026-0.029) and speech-level significant. Score gaps for press/statement are specification-sensitive; address gap persists. Mention-rate ratios are inflated by a few speeches; address IRR depends on one speech. Finding text misstates the statement IRR.

Recommended strength: WEAK (downgrade from moderate).
Safe claims: (a) remarks have the lowest mention rate per character except weekly addresses; (b) press-conference and statement passages occur about 1.3-2.4x as often as in remarks (NB GLM range), press figure about 1.7x without top-3 speeches; (c) address IRR depends on a few speeches; (d) venue score differences are small and partly scorer-built; (e) questioner passages score lower by construction; (f) VADER tone is word valence, not stance, and was not recomputed. No causal claims supported.
