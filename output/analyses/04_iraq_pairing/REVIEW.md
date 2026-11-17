# Review: 04_iraq_pairing

Reviewer: independent re-run and checks. Analyst files were not modified.

## 1. Reproduction

Re-ran `analysis.py` with the venv python (`-I`). Exit 0. All key numbers reproduce exactly:
- n=4632 (raw 4741, questioner 109 excluded, dup 0), 1103 speeches
- paired 1037 = 22.39%; passage-only 495 = 10.69%
- pre 19.33% vs post 24.97%, chi2=20.72, p=5.3e-6
- logit post OR 1.923 (1.018-3.63), p=0.044; post+campaign+time OR 0.895 p=0.69; campaign OR 5.26
- MK yearly z=0.313 p=0.7545; monthly z=1.484 p=0.138
- tone -0.080 vs +0.184, MWU p=3.7e-42; war_direct 56.4% vs 42.6%, chi2 p=9.4e-19
- threshold 30/50/70 chi2 p=1.06e-4 / 7.5e-5 / 0.48
- campaign 50.94% vs 16.89%; non-campaign pre/post 17.64 vs 16.09 p=0.213

## 2. Code and data checks

Clean: dup filter (0 dup_of in speeches_index), questioner filter (109 rows, `questioner_not_president`), date parse and 2011-12-18 split are correct. Multiline CSV parsed fine by pandas.

Problems found:

**A. Selection built into the denominator (major).** `detect.py` INDIRECT cues include "two wars" / "Iraq and Afghanistan" / "wars in Iraq and Afghanistan". 437 rows in references.csv were admitted via these cues. Of these, 207 (47%) are paired. So ~20% of the 1037 paired passages got into the dataset partly because the detector looked for Iraq+Afghanistan co-framing. Pairing share is partly circular. Not disclosed in RESULT.md.
- Excluding cue rows: pre 16.9% vs post 22.2% (n=4195). Logit with post + campaign + time on non-cue rows: post OR 0.857, p=0.62.

**B. Speech type confound not controlled (major).** Pairing by speech type: press_conference 6.2% (n=1030), statement 6.3% (n=506), remarks 30.0% (n=2661), address 31.1%, weekly_address 43.3%, interview 26.5%. Adding speech-type fixed effects to the speech-clustered logit (post + campaign + time + type FE): post OR 1.013, p=0.96. The post effect is fully absorbed by speech-type mix. Analyst did not check this.

**C. Chi-square ignores clustering (moderate).** Pre/post chi2 (p=5e-6) treats 4632 passages as independent, but they come from 1103 speeches (many passages per speech). Speech-cluster bootstrap (2000 reps) of post-minus-pre difference: +5.6 pts, 95% CI -0.1 to +11.7, so about p≈0.06 two-sided. The headline "p<0.001" is not valid under clustering. The analyst's clustered logit (p=0.044) is the better number, and it is fragile (see A, B, and the campaign control).

**D. Tone confound partly handled (moderate).** Pairing uses passage+context; tone uses passage only. Iraq is in the passage text for 524 rows (mean tone -0.071 across all). Stratified check: among passages with Iraq only in context, paired -0.075 (n=522) vs unpaired +0.236 (n=3349), MWU p=3e-36. So the tone gap is not only from Iraq words inside the passage. It still reflects war-vocabulary valence (category mix is also different), so the gap is word valence about war topics, not framing or stance. The analyst's wording on this is appropriate.

**E. Category and rule score circularity (minor).** `score.py` gives a penalty for Iraq terms without Afghan terms and adds Iraq-related terms in the war-language scoring. Category and score are therefore not independent of Iraq wording. The "category" chi2 result (war_direct 56% vs 43%) should not be read as independent evidence of framing.

**F. Mann-Kendall (minor).** Yearly series: 2017 is a partial year (n=11, ends 2017-01-12); 9 points, low power. Monthly series mixes months with n=1 and n=300 with no weighting. Both trend tests are non-significant, so the "no trend" conclusion is low-power, not evidence of absence.

**G. Multiple comparisons and threshold choice (minor).** About 15 p-values reported with no correction. Thresholds 30/50/70 were chosen post hoc; two of three are significant and one is not, which is exactly why the result is fragile. The analyst reports all three, which is honest, but the 50 and 30 rows are not independent evidence.

**H. Campaign flag (minor).** Title regex only, not checked by hand (analyst's own caveat). Note 2012 contains most campaign-titled speeches and is entirely in the post period, so the campaign flag and the post split are collinear in part.

## 3. Independent checks (my code: `review/check.py`)

| Check | Result |
|---|---|
| Overall post-pre diff | +5.64 pts |
| Speech-cluster bootstrap 95% CI | -0.11 to +11.71 (bootstrap P(diff<=0)=0.029) |
| Non-cue rows, post+campaign+time logit | OR 0.857, p=0.62 |
| Speech-type FE added | post OR 1.013, p=0.96 |
| Tone, Iraq only in context | paired -0.075 vs unpaired +0.236, p=3e-36 |
| Index dup_of non-empty | 0 |

## 4. Verdict on claims

- "Pairing did not fall after withdrawal": supported descriptively.
- "Pairing rose 19.3% to 25.0% (p<0.001)": not supported. Clustered CI is borderline and the effect vanishes after removing the Iraq-cue rows, adding speech-type FE, or adding campaign control. Report as "no reliable change."
- "Rise is campaign-driven": partly; the campaign control removes it, but speech type also removes it, so the attribution to campaigns is not unique.
- "No monotone trend": supported only as low-power null.
- "Paired passages more negative in tone and more war_direct": supported as word-valence difference, robust to Iraq-in-passage stratification. Not stance. War-topic confound remains.
- "Explicit 'ending two wars' framing is rare (21)": supported with the tight regex; broad regex was discarded post hoc (a choice that should be stated as a choice).

## 5. Recommended strength

Downgrade from **moderate** to **weak**. The only robust results are the descriptive pairing share and the tone and war-category association (word valence). The pre/post rise, which is the question's headline, is not robust to clustering, the Iraq-cue selection, speech-type mix, and the campaign control.

## Suggested fixes (not applied)

1. Report pairing with and without cue-admitted rows (the `two wars` / `Iraq and Afghanistan` INDIRECT matches) as the primary comparison.
2. Add speech-type fixed effects to the main logit.
3. Use speech-level or cluster-bootstrap inference for pre/post, and drop or down-weight the chi2 p-values.
4. Disclose that the "two wars" regex choice (tight vs broad) was made after seeing results.
