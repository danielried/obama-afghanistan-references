# 01_venue: does venue (speech type) change how Afghanistan passages are scored, categorised, or toned?

Re-run: `.venv/bin/python -I output/analyses/01_venue/analysis.py` (full log: `run_log.txt`).

## Question
Do Afghanistan passages differ in war-likelihood score, category mix, VADER tone, and mention rate across speech types (weekly_address, press_conference, remarks, statement, address, interview)? Press conferences and interviews are split into the President's answers vs questioner passages.

## Data
- `output/references.csv`: 4,741 passages (all in kept speeches). `llm_score` blank, so `final_score_pct` = rule score.
- `output/speeches_index.csv`: 5,026 speeches. 0 rows have non-empty `dup_of`, so none excluded.
- Speaker split: derived from `data/speeches.db` raw text. Paragraph labels use the same regex as `detect.py` (`Q.`, `Audience Member`, etc.). 109 passages labelled questioner; this matches the `questioner_not_president` rationale flag in 109/109 cases. Passage offsets fall inside their labelled paragraph in 100% of rows.
- Denominators: `len(raw_text)`. `text_len` in the index differs from raw text for 3 speeches (99.94% match).
- Tone = VADER compound (word valence, not stance).
- Groups with n >= 10 are tested. Kept: remarks 2,685; press_conference|president 1,030; statement 506; address 206; weekly_address 97; interview|president 83; press_conference|questioner 80; other 50. Dropped from tests: interview|questioner (n=4; included in rate table only).

## Method
- Kruskal-Wallis (score, tone); eta²_H effect size.
- Pairwise Mann-Whitney (two-sided), Holm correction over 28 pairs per outcome; rank-biserial r.
- Chi-square of group x category (unrelated and political_background merged); Cramér's V.
- High-likelihood share (score >= 50 primary; 30 and 70 as sensitivity); chi-square.
- Rates per 10k chars: exact Poisson CI. Speech-level negative binomial GLM (exposure = text length; base = remarks); LR test; Holm on IRRs.

## Key numbers

| Group | n passages | Score median | Tone median | War share (direct+adj) | Score >= 50 | Rate /10k chars [95% CI] |
|---|---|---|---|---|---|---|
| remarks | 2,685 | 69 | 0.000 | 0.750 | 0.779 | 0.726 [0.699, 0.754] |
| press_conference\|president | 1,030 | 71 | 0.340 | 0.739 | 0.926 | 1.887 [1.773, 2.006] |
| press_conference\|questioner | 80 | 53.5 | 0.000 | 0.688 | 0.588 | 1.866 [1.480, 2.322] |
| statement | 506 | 71 | 0.637 | 0.753 | 0.923 | 1.772 [1.621, 1.934] |
| address | 206 | 79 | 0.000 | 0.825 | 0.883 | 1.927 [1.673, 2.209] |
| weekly_address | 97 | 74 | 0.000 | 0.845 | 0.845 | 0.603 [0.489, 0.735] |
| interview\|president | 83 | 67 | 0.000 | 0.675 | 0.952 | 2.127 [1.694, 2.637] |
| other | 50 | 63 | 0.000 | 0.760 | 0.640 | 1.149 [0.853, 1.515] |

Tests:
- Score KW: H = 145.9, df = 7, p = 2.9e-28, eta²_H = 0.029 (small). Holm-significant pairs: 18/28.
- Tone KW: H = 428.1, df = 7, p = 2.2e-88, eta²_H = 0.089 (small to moderate).
- Category chi-square: chi² = 208.5, df = 28, p = 1.7e-29, V = 0.105 (small). 22.5% of cells have expected count < 5, so the p-value is approximate.
- High-likelihood share chi-square: at 50, chi² = 207.6, p = 2.8e-41, V = 0.21. At 30, chi² = 138.6, V = 0.17. At 70, chi² = 93.9, V = 0.14. The ranking is stable across thresholds.
- Speech-level NB GLM (5,023 speeches, 4,741 passages, alpha = 5.50): LR = 57.1, df = 6, p = 1.8e-10. IRR vs remarks: press_conference 2.44 [1.68, 3.53], Holm p < 0.001; address 3.31 [1.66, 6.59], Holm p = 0.003; statement 1.44 [1.18, 1.76], Holm p = 0.002; interview 2.97 [1.06, 8.33], Holm p = 0.12 (n.s.); weekly_address 0.79 [0.57, 1.09], Holm p = 0.30 (n.s.); other 0.95 (n.s.).

Key pairwise results (Holm p, rank-biserial r):
- address vs remarks: r = -0.29, p < 0.001.
- press_conference|questioner vs press_conference|president: r = 0.55, p < 0.001.
- press_conference|president vs remarks: r = -0.14, p < 0.001.
- statement vs remarks (score): r = -0.09, p = 0.017.
- Tone, statement vs remarks: r = -0.49, p < 0.001. Tone, press_conference|president vs remarks: r = -0.27, p < 0.001.
- Tone, press_conference|president vs address: r = 0.25, p < 0.001.
- weekly_address vs remarks: score p_holm = 1.0 (n.s.).

## Finding
1. Venue shifts the score and the mention rate, but the effect sizes are small. Address and press-conference-president passages score higher than remarks. Questioner passages score clearly lower. Weekly addresses do not differ significantly from remarks (score Holm p = 1.0); statements differ only slightly (r = -0.09).
2. The score gap between questioner and president passages is circular, because the scorer applies a -18 penalty to questioner passages (`score.py:106`). It is not evidence about framing.
3. The venue-title bonus is also circular. `venue_title` (+4) keys on speech titles, and it applies to 71% of statements, 49% of addresses, 39% of press_conference|president passages, and 0% of weekly addresses and "other". Removing it (approximate, -4 per flagged passage) keeps a significant venue effect (H = 132.0, p = 2.5e-25, eta²_H = 0.026). Address median drops 79 -> 77 and statement median 71 -> 67.
4. Mention rates: press conferences (about 1.9 per 10k chars), addresses (1.9), and statements (1.8) run about 2.4-3.3x the remarks rate (0.73). Weekly addresses (0.60) are the lowest, with no significant difference from remarks. The questioner rate (1.87) is similar to the president rate, so the questioner passages are not a rate artefact.
5. Tone (VADER, word valence only): statements use the most positive wording (median 0.64). Press-conference-president answers are mildly positive (median 0.34). Most other groups have median 0. Tone is not a stance measure; statement positivity most likely reflects ceremonial wording.

## Caveats
- Scores are rule-based estimates, not ground truth. The scorer was tuned on 30 labels.
- The score differences by venue are partly built into the rules (questioner penalty, venue-title bonus, speech-level hit-count bonus). The sensitivity analyses reduce, but do not remove, these built-in effects.
- Only the first paragraph of each Q&A turn is labelled as questioner. Multi-paragraph questions may be misattributed to the President, and some questioner text may be counted as president text. Rates for the split groups are therefore approximate.
- 24 questioner-labelled passages sit inside `remarks` (audience Q&A) and are left there.
- Small groups (interview|president n = 83, interview|questioner n = 4, other n = 50) give wide CIs. "other" is a mixed bag of 8 speeches.
- Many speeches contribute several passages (for example, 98 press conferences give 1,030 passages), so passages are not independent. The Mann-Whitney and chi-square tests treat them as independent, which overstates significance. The speech-level GLM is the more appropriate test for rates.
- Category chi-square has sparse cells (22.5% expected < 5). The p-value is approximate.
- VADER tone is word valence, not stance.
