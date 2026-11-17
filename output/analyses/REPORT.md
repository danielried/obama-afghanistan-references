# Obama Afghanistan Correlation Study: Combined Report

Scope: 12 analyses, each with an analyst result and a skeptic verdict. Corrected findings and strengths follow the skeptic verdicts. Analyses 01-07 use project data only. Analyses 08-12 used outside sources (section 4). 

## 1. Summary table

| # | Analysis | Question | n | Headline number (corrected) | Verified strength | One-line finding |
|---|---|---|---|---|---|---|
| 01 | Venue | Do Afghanistan passage war-likelihood, category, tone, and mention rate differ by speech type? | 4,741 passages; 5,023 speeches | Score KW eta2_H = 0.029 (small). Mentions per 10k chars: remarks 0.726, press conference (president) 1.887. NB GLM IRR press 2.44; 1.66 after removing top-3 passage-heavy speeches | weak | Venue shifts scores and mention rates modestly; score gaps are partly built into the scorer and sensitive to controls |
| 02 | Election | Is 2012 more withdrawal-framed, and is the spike just stump-line repetition? | 3,877 non-questioner high-likelihood passages; 5,026 speeches | Withdrawal share 31.8% (2012) vs 9.4% (other years), OR 4.48, speech-clustered p = 1.6e-14 | moderate | 2012 is more withdrawal-framed at year level. Campaign-specific claim not supported. No count spike (726 in 2012 vs 718 in 2009, 720 in 2010) |
| 03 | Framing shift | Do category and frame shares shift over 2009-2016, and do breaks match announcements? | 4,582 main passages; 96 months; 13 events | End frame ex-Iraq 1.8% (2009-11) to 8.6% (2012-14). Event match +/-30 d p = 0.054; +/-60 d p = 0.45 | moderate | Period-level rise in end/withdraw and transition frames holds after Iraq exclusion and clustering. Specific break dates and event alignment do not |
| 04 | Iraq pairing | Do Afghan passages pair with Iraq, and did pairing fall after Dec 2011? | 4,632 passages; 1,103 speeches | Paired share 19.3% pre vs 25.0% post. Post OR 0.90 (p = 0.69) after campaign control; OR 1.01 (p = 0.96) after speech-type FE | weak | Apparent post-2011 rise is campaign- and speech-type-driven; not robust |
| 05 | Salience vs tone | Is monthly salience of high-likelihood passages correlated with mean VADER tone? | 97 months; 3,877 passages | Detrended r = 0.158, p = 0.121. Partial r controlling war share = 0.105, p = 0.31 | null result | No reliable association. First-difference r = 0.279 is carried by spike months |
| 06 | Reaction by lean | Does statement-tone vs press-reaction correlation differ by outlet lean? | 92 items (62 with lean); 13 events | Overall press r = 0.528, p = 0.077 (n = 12). Tone x lean interaction Wald p = 0.13 | weak | Lean-specific correlations not significant. Only robust item-level pattern: left-leaning items more negative than center |
| 07 | Opinion vs news | Do opinion items track statement tone differently from news items? | 82 items (51 news, 31 opinion); 12 events | Negative share 11.8% (news) vs 64.5% (opinion). Tone x opinion b = -1.74, cluster p = 0.113, permutation p = 0.070 | weak | Level difference robust but confounded with lean. Slope difference not established |
| 08 | Casualties | Do monthly US deaths predict passage volume or tone (lags 0-6, Granger)? | 96 months; 3,868 high-likelihood passages | No significant CCF or Granger result. Partial r deaths vs rate = 0.001 | weak (null result) | No evidence of prediction either direction. Test design weak |
| 09 | Troops | Do troop levels relate to frame shares or mention volume, and does rhetoric lead or lag? | 31 quarters (levels); 30 (differences) | Level correlations are trend artifacts (partial r -0.174, p = 0.35; 0.075, p = 0.69). Lagged HAC p = 0.0085, Holm p = 0.10 | inconclusive, data gap | No robust association. One nominal lagged effect is exploratory only |
| 10 | Public opinion | Does Gallup "mistake" opinion track Obama Afghanistan passage volume, tone, and frames? | 11 Gallup readings | Contemporaneous count rho = -0.83 (p = 0.0015 exact). Partial rho given time = -0.54 (p = 0.11) at thr50 | weak | Association largely shared time trend. Tone not related. Opinion-drop tone result fragile and exploratory |
| 11 | Approval | Does monthly Obama approval move with monthly Afghan passage rate or tone? | 95 months | Level r = 0.117, p = 0.261. Diff r = 0.037, p = 0.720. Granger Afghan to approval p >= 0.22 | weak | Narrow null. Exposure rule-based; tone tested in levels only |
| 12 | Congress | Do Congressional Afghanistan votes coincide with changes in passage volume, rate, or tone? | 65 roll calls; 30 Afghan-related votes in 18 clusters | Verified Afghan votes: mentions 37.0 observed vs 49.6 null, p_up = 0.758 | null result | No detectable effect. Power very low (7 verified clusters) |

## 2. Per-analysis findings (corrected)

### 2.1 Analysis 01: Venue

Question: Do Afghanistan passages differ by speech type in war-likelihood score, category mix, VADER tone, and mentions per 10k characters?

Corrected finding: Venue shifts the score and mention rate, but effects are small (score KW eta2_H = 0.029). Address and press-conference-president passages score higher than remarks. Questioner passages score lower, but this is built into the scorer (questioner penalty -18). Mentions per 10k chars: remarks 0.726, press conference (president) 1.887, statement 1.772, address 1.927, weekly address 0.603. Speech-level NB GLM IRRs vs remarks: press conference 2.44 [1.68, 3.53]; address 3.31 [1.66, 6.59]; statement 1.44 [1.18, 1.76]. Weekly address is not significantly different from remarks (IRR 0.79, Holm p = 0.30). Interview is not significant (IRR 2.97, Holm p = 0.12).

Major reviewer issues:
- The analyst's text said statements are 2.4-3.3x remarks. The statement GLM IRR is 1.44. The 2.4 figure is press only and 3.3 is address only.
- The address IRR depends on one speech (DCPD-201200336 holds 42 of 206 passages). Excluding top-3 passage-heavy speeches per type: address IRR 1.55 [0.78, 3.09], p = 0.21 (not significant); press 2.44 to 1.66 [1.15, 2.38]; statement 1.44 to 1.31 [1.07, 1.61]. This is an influence diagnostic only.
- Score gaps are specification-sensitive. Passage OLS with speech-clustered SEs: press +4.8 (p < 0.001), statement +4.6 (p = 0.004). Adding year FE and log(hit_count): press -1.96 (p = 0.15), statement +0.70 (p = 0.62). Address +6.6 (p = 0.0002) persists. log(hit_count) may be post-treatment.
- Circularity is under-addressed. Only venue_title (+4) and questioner (-18) were removed. score.py also adds speech-focus hit bonuses (+10/+6, speech-level) and date features (in_administration +5, near_inflection +8). Not sensitivity-tested.
- Minor: 25 questioner-labelled passages are not split out. Rate denominators differ between split and whole-type groups. VADER was not independently recomputed (vaderSentiment not installed); stored values reproduce.

Reproduction: headline numbers reproduce exactly (KW score H = 145.9; tone H = 428.1; category chi2 = 208.5; questioner medians 53.5 vs 71.0).

Strength: weak (downgraded from moderate). Chart: 01_venue/chart_venue.png

### 2.2 Analysis 02: Election (2012 withdrawal framing)

Question: Is 2012 more withdrawal-framed than other years, and is the 2012 spike just stump-line repetition?

Corrected finding: On the lexical measure, 2012 is more withdrawal-framed: 31.8% vs 9.4% of non-questioner high-likelihood (>=50) passages (231/726 vs 297/3151), OR 4.48. Speech-clustered p = 1.6e-14 (the naive p of 1.2e-56 is overstated). Survives Iraq-local exclusion (OR 4.49), removal of repeats, and thresholds 30/50/70. Escalation share is lower in 2012 (18.2% vs 30.4%, OR 0.51).

The campaign-specific claim is not supported. With year FE, campaign_2012 is not identified: logit OR 1.66 (p = 0.39); quasi-Poisson RR 2.28 (p = 0.43). Only 17 high-likelihood passages fall after Nov 6 2012.

No count spike. Reviewer counts: 726 (2012) vs 718 (2009) and 720 (2010). Per-speech excess is modest (1.13 vs 1.00, unclustered p = 0.025), partly a denominator effect because speech volume fell.

Stump-line repetition is a minor, threshold-dependent part. Repeated near-duplicates are 12.7% of non-May campaign withdrawal passages (8-gram Jaccard >= 0.5), 17.7% at J >= 0.3, and 33.7% at 5-gram J >= 0.3. Removing repeats keeps OR 8.4-9.1.

Major reviewer issues: passages treated as iid in the main tests (speech-clustered values above); WITHDRAW regex has no Iraq filter (44 of 227 campaign withdrawal passages mention Iraq; effect survives); May 2012 exclusion was post hoc and the full-campaign contrast (32.0% vs 5.7%) should be the headline; 'transition' drives much of the signal (no-transition result 27.7% vs 5.0%, OR 7.30 should be reported alongside); method text miscounts exclusions (58 questioner passages removed, 3,935 to 3,877).

Strength: moderate (downgraded from strong). Chart: 02_election/election_frame.png

### 2.3 Analysis 03: Framing shift (2009-2016)

Question: How do category and frame shares shift over the term, and do change points align with reaction-event announcements?

Corrected finding: The end/withdraw frame shows a period-level rise. Ex-Iraq, share is 1.8% (2009-11) and 8.6% (2012-14); speech-cluster bootstrap CI for the difference [0.051, 0.087]. With Iraq-mentioning passages: 3.8% and 12.3%. Transition frame: 11.5%, 15.9%, 14.7% (chi2 p = 0.00026). War_direct: 43.1%, 48.9%, 47.2% (chi2 p = 0.0011); still significant under clustering. Combat frame flat. Aid/diplomacy and incidental show no reliable shift.

Not supported as stated:
- The 2011-12 end-break cluster as a framing shift. It is Iraq-contaminated, not re-tested without Iraq, and has no multiplicity control across 7 series x 5 subsets.
- The July 2010 transition break. It is token-driven ('transition' 107 to 169 hits while 'train' falls 102 to 54 to 38).
- Event alignment. Breaks within +/-30 d of 13 announcements: 6 of 12 vs null mean 2.98, MC p = 0.054. Within +/-60 d: 6 of 12 vs 5.31, p = 0.45. The null ignores clustering of pooled breaks.

Other issues: 2012-05 has 300 passages (157 from three speeches). 2015-16 END rests on one speech (9 of 31 hits). Campaign-season confound unchecked (END share 0.23-0.28 in Jun-Oct 2012, 0.057 in Nov 2012). Frame lexicon precision unmeasured; spot checks show false positives.

Strength: moderate (unchanged). Chart: 03_framing_shift/framing_shift.png

### 2.4 Analysis 04: Iraq pairing

Question: Do Afghanistan passages pair with Iraq, and did pairing fall after the Dec 2011 withdrawal?

Corrected finding: Paired share (Iraq and Afghan both in passage plus context) is 22.4% overall (1037/4632); passage-only 10.7%. Pre/post: 19.3% vs 25.0% (chi2 p = 5.3e-6), but the rise is not robust:
- Speech-clustered bootstrap of the difference (+5.6 points): 95% CI about -0.1 to +11.7, p about 0.06.
- Campaign control removes it: post OR 0.90 (p = 0.69). Campaign-titled speeches pair 51% vs 17% elsewhere.
- Removing detector Iraq-cue rows (INDIRECT 'two wars' / 'Iraq and Afghanistan'; 207 of 1037 paired came in via cues): post OR 0.86 (p = 0.62).
- Speech-type FE: post OR 1.01 (p = 0.96). Press conference 6.2% and statement 6.3% pair less than remarks 30.0% and weekly address 43.3%.

No significant trend (Mann-Kendall yearly p = 0.75; monthly p = 0.14), but power is low (9 yearly points).

Paired passages have more negative VADER passage tone (-0.080 vs +0.184, MWU p = 3.7e-42), persisting within Iraq-in-passage stratification and within war_direct. This is word valence, not stance. Explicit 'ending two wars' framing is rare (21 passages under the tight regex).

Other issues: headline p-values treat passages as independent; about 15 p-values without multiplicity correction; thresholds and regex choices made after viewing results.

Strength: weak (downgraded from moderate). Chart: 04_iraq_pairing/pairing_by_year.png

### 2.5 Analysis 05: Salience vs tone

Question: Is monthly salience of high-likelihood (>=50) passages correlated with mean VADER tone?

Corrected finding: No reliable association. Detrended Pearson r = 0.158 (p = 0.121, n = 97); Spearman rho = 0.083 (p = 0.421). Controlling for war_direct share: partial r = 0.105 (p = 0.31). First-difference r = 0.279 (p = 0.006; permutation p = 0.0104, the floor of 1/96) is carried by spike months 2012-05, 2013-01, 2015-03; dropping the top three gives r = 0.101 (p = 0.344). Only thr30 reaches significance on the primary spec (r = 0.258, p = 0.011); thr70 gives r = 0.045 (p = 0.666). Do not report the first-difference p as a finding.

War_direct share correlates negatively with salience (r = -0.276) and tone (r = -0.286), so VADER tracks war vocabulary mix. The analyst's claim that spike months are war-heavy is wrong (their war_direct shares, 0.470-0.534, are not above the overall 0.543).

Strength: null result (downgraded from weak). Chart: 05_salience_tone/salience_tone.png

### 2.6 Analysis 06: Reaction tone by outlet lean

Question: Does the statement-tone vs press-reaction correlation differ by outlet lean?

Corrected finding: Analyst values reproduce (overall press r = 0.528, p = 0.077, n = 12 events). Press-only lean-specific event correlations are positive (left 0.528, p = 0.18; center 0.222, p = 0.60; right 0.174, p = 0.74; international 0.578, p = 0.13; unknown 0.274, p = 0.60), none significant, with 6-8 events each. The 'positive in every lean group' claim fails under press+tweet (right -0.342; unknown -0.095). Tone x lean interaction is not significant (joint Wald p = 0.13, 4 df, 8 clusters).

Tone coefficient is not robust: main model cluster p = 0.107, HC1 p = 0.526. With-missing-lean model: cluster p = 0.007 but HC1 p = 0.315. The p < 0.05 claim is not justified.

The item-level pattern that survives: left-leaning press items are more negative toward the decision than center items (b about -0.56 with event FE; cluster p = 0.007; HC1 p = 0.025-0.03). Stance is a researcher judgment with unknown blinding; left items are concentrated in 2009; only 8 clusters.

Other: 30 of 92 items lack lean and are not imputed. Tone uses 12 events, item models use 13 (undocumented). Core-only statement tone sensitivity r = 0.508 (p = 0.092).

Strength: weak (unchanged). Chart: 06_reaction_lean/lean_split_correlation.png

### 2.7 Analysis 07: Opinion vs news items

Question: Do opinion/editorial/analysis reaction items track statement tone differently from news_report items?

Corrected finding: The level difference is robust. Opinion items are negative 20/31 times vs news 6/51 (item-level Fisher p < 0.0001). Survives cluster-robust (b = -0.561, p = 0.0002) and event-level paired (p = 0.014) tests. But it is confounded by outlet lean: 10 of 31 opinion items are left-leaning, and 8 of those are negative. It cannot be separated from ideology here.

The slope claim is not supported. News-only per-event r = 0.625 (p = 0.030, n = 12); dropping event 2011-05-01 (one item) gives r = 0.465 (p = 0.149, n = 11). Opinion index is flat (r = -0.213, p = 0.507). Interaction b = -1.74 (cluster p = 0.113; permutation p = 0.070). Sensitivity range p = 0.046 to 0.66; leave-one-event-out p = 0.050 to 0.189. Opinion items are negative regardless of tone, so the flat slope is partly a ceiling effect.

Other: 12 clusters make cluster SEs unreliable; no multiplicity correction.

Strength: weak (unchanged). Chart: 07_opinion_vs_news/chart.png

### 2.8 Analysis 08: Casualties (outside data)

Question: Do monthly US military deaths in Afghanistan (2009-2016) predict monthly volume or mean tone of high-likelihood passages?

Corrected finding: No evidence in these data that monthly deaths predict passage volume or tone at lags 0-6 in either direction. Raw level Spearman rho = 0.32 (p = 0.0014) disappears after trend and month-of-year controls (partial r = 0.001, p = 0.99). First-differenced CCF: max |r| = 0.18 at lag -2 (p = 0.083), none significant. Granger deaths to rate, lags 1-6: p = 0.52-0.94. Granger rate to deaths: p = 0.24-0.65. The one nominal residual result (rate to deaths at lag 6, p = 0.025) does not survive multiplicity correction (Bonferroni about 0.3 over its 12 tests).

Test design is weak:
- Rate per speech is stationary in levels (ADF p < 0.0001) but was first-differenced; the differenced series has lag-1 ACF -0.515, i.e. over-differencing.
- Deaths stationarity is spec-dependent: constant-only ADF p = 0.94; trend ADF p about 0.001-0.003. "Non-stationary in levels" is not robust.
- VAR AIC selects the maximum lag (6) for all pairs.
- p-values assume iid observations.

Input caveats: casualty series is secondary (Wikipedia DoD-attributed table, all OEF/OFS theaters, US only; primary DCAS pages not readable). Reviewer matched all 96 monthly cells. Printed 2015/2016 row totals (21, 10) differ from cell sums (22, 9); cells used, total 1,752 unaffected. CRS R41084 cross-check: 2009 matches (311); 2010 and 2011 differ by -1 and -3 (civilian attribution unverified).

Strength: weak (verdict corrected from null_result; the finding is a null).

### 2.9 Analysis 09: Troop levels (outside data)

Question: Do US troop levels in Afghanistan relate to frame shares and mention volume, and does rhetoric lead or lag posture?

Corrected finding: No robust association. Level correlations (combat-frame share r = -0.432, p = 0.015 naive; HL volume r = +0.413, p = 0.021) are trend artifacts: troops vs time r = -0.77; partial r given time is -0.174 (p = 0.35) for combat share and 0.075 (p = 0.69) for HL volume. First differences show no contemporaneous association (all p >= 0.20).

One nominal lagged result: combat share change on prior-quarter troop change (HAC(2) p = 0.0085, n = 28, R2 = 0.074). Fragile: HAC(1) p = 0.027; HC3 p = 0.169; with linear time p = 0.015; Holm across 12 specs p = 0.102; Bartlett CCF p = 0.061. Exploratory only.

Lead test: no evidence rhetoric leads posture (lead p = 0.80; CCF lag -1 r = -0.033, p = 0.82). This is a low-power null, not evidence of absence.

Input caveats: 5 of 21 monthly troop values are not DoD counts (Aug 2009 interpolated; Jun-Sep 2010 CRS estimates or unflagged estimates). Quarterly and monthly CRS series disagree at Mar 2010 (79,100 vs 85,000). 2016Q4 has no troop value. Frame regex runs on passage plus context while HL membership uses passage score only. 'train' and 'taliban' are generic terms (about 14% of HL passages each). Brookings charts not usable.

Strength: inconclusive, data gap. Chart: 09_troops/troop_vs_rhetoric.png

### 2.10 Analysis 10: Public opinion (Gallup mistake item)

Question: Does Gallup "mistake" opinion track Obama Afghanistan passage volume, tone, and frames in 30-day windows around each poll?

Corrected finding: Correlations reproduce. Contemporaneous count vs mistake share: rho = -0.83 (p = 0.0015 exact; 0.003 permutation; n = 11; thr50). War_direct share: rho = +0.73 (p = 0.010). Both are confounded by time (opinion vs days since inauguration rho = +0.82). Partial rho given time for count: thr50 -0.54 (p = 0.11); thr30 -0.66 (p = 0.04); thr70 -0.28 (p = 0.44). The time control attenuates but does not remove the thr50 link. Tone shows no reliable relation (rho = -0.37, p = 0.27).

Opinion-drop vs tone-change (rho = +0.78, p = 0.014, n = 9) has no hypothesized direction in the code and runs opposite to the lead hypothesis; fragile (thr30 +0.84; thr70 +0.52, p = 0.19); overlapping windows. Exploratory.

Input caveats: dedupe was a no-op (dup_of empty), so the claim that duplicates were removed is false (no effect on results). Gallup Nov 2009 approval value (35) was not traced to the fetched article; Feb 2010 (48) and Nov 2010 (44) were verified; Jul-Aug 2010 (36) is consistent with the CSV. Gallup question wording changed between 2009-2011 and 2013-2015 and was pooled. Pew (n = 3) and approval (n = 4) too small to test. About 54 uncorrected tests.

Strength: weak (verdict corrected from inconclusive_data_gap). Chart: 10_public_opinion/out/chart_opinion_vs_volume.png

### 2.11 Analysis 11: Obama approval (outside data)

Question: Does monthly Obama approval move with monthly Afghan passage rate and tone?

Corrected finding: No detectable relationship. Level r = 0.117 (p = 0.261, n = 95; Spearman p = 0.156). First-difference lag-0 r = 0.037 (p = 0.720). Lags 1-3 r = 0.059, -0.091, -0.123 (all p > 0.24). Granger Afghan to approval p = 0.59, 0.64, 0.22 (lags 1-3). Approval to Afghan p = 0.11, 0.11, 0.19. Tone level r = 0.031 (p = 0.763). Excluding Jan 2013 (one Karzai press conference and joint statement supplies 154 of 174 passages): r = 0.077 (p = 0.464).

Major issues:
- Exposure is rule-based: llm_score is blank in all rows, so the >=50 label is not LLM-validated.
- Tone was tested only in levels; "tone unrelated" overstates the test.
- Validation: of 16 published Gallup points, 10 were verified (9 from the 2016 Gallup page; May 2011 = 50). On those 10, mean absolute difference is 0.36 and maximum 0.5. The 0.37/0.8 figures partly rest on search snippets. The conclusion that the series tracks Gallup holds.
- Level p-values ignore autocorrelation (approval ADF p = 0.046, borderline).
- The caveat "overlapping 7-day windows" is inaccurate: windows are consecutive.
- Exposure partly reflects speech_focus hits. About 30 unadjusted tests, all null (minimum p = 0.112); no power analysis.

Strength: weak (verdict corrected from null_result). Chart: 11_approval/approval_vs_afghan.png

### 2.12 Analysis 12: Congressional Afghanistan votes (outside data)

Question: Do Congressional Afghanistan actions coincide with changes in passage volume, rate, or tone in [-14,+14] day windows vs matched baselines? Do close votes attract more mentions?

Corrected finding: No detectable change around Afghanistan-related votes, 2009-2016. Mention excess is negative in every group, p_up >= 0.576 for counts: verified Afghan votes 37.0 observed vs 49.6 null (-25%, p_up = 0.758, p_two = 0.460; 10 votes, 7 clusters); supplementals 35.3 vs 63.4 (p_up = 0.889); withdrawal amendments 36.2 vs 42.7 (p_up = 0.665); NDAA/DoD 37.1 vs 38.9 (p_up = 0.576). Verified-Afghan tone: 0.247 observed vs 0.158 null (n = 259), p_up = 0.189; no tone group is significant.

Close-vote Spearman: verified Afghan rho = +0.086 (p = 0.81); Afghan-related (30) rho = -0.211 (p = 0.26); all 65 votes rho = -0.113 (p = 0.37). Signs are mixed and none is significant.

Positive excess clusters coincide with Afghan policy events rather than votes: McChrystal resignation (2010-07-01), drawdown address (2011-07-06), NATO summit (2012-05-18), Bagram/drawdown remarks (2014-05-22), strategy speech (2015-10-01). The design cannot separate vote timing from Afghan news.

Major issues: the 'all Afghan-related' headline includes 14 unverified McGovern/Jones/Kucinich amendments and 6 bill-level supplemental votes (including a cloture vote); NDAA/DoD milestones are not Afghanistan-specific. Only 10 votes (7 clusters) are verified. Null design lacks session-calendar matching; overlapping windows treated as independent. Livable World and NPR tallies were not confirmed in fetched text.

Strength: null result. Power is very low, so this is not evidence of no effect. Chart: 12_congress/event_study.png

## 3. Cross-cutting observations

- Shared nulls. Analyses 08, 09, 10, 11, and 12 find no robust relation between outside war-event series and rhetoric volume or tone. Level correlations in 08 (rho 0.32), 09 (r -0.43 and 0.41), and 10 (rho -0.83) all weaken or vanish after time controls. Trend control is the common thread.
- Campaign confound. The 02 withdrawal spike, the 04 pairing rise, and the 03 end-frame rise in 2012-14 all coincide with campaign months. Campaign control removes the 04 effect. 02 cannot separate campaign from 2012 as a year. The 03 campaign-season pattern (END 0.23-0.28 in Jun-Oct 2012; 0.057 in Nov 2012) is untested.
- Iraq contamination. Lexical end/withdraw frames (02, 03) catch Iraq references. Ex-Iraq, 03's end-frame magnitude falls (12.3% to 8.6%) but the direction holds. 02 survives Iraq-local exclusion (OR 4.49).
- Scorer circularity. Venue score gaps (01), questioner effects (01, 06, 07), and the 50% threshold used throughout are partly built into the rule-based scorer. Treat scores as descriptive.
- Tone. VADER is word valence, not stance, in every analysis that uses it (01, 04, 05, 06, 07, 10, 12). 05 found tone tracks the war-vocabulary mix. 04's tone gap is partly category-driven.
- Non-independence. 01 and 02 both show more withdrawal/war-heavy framing in press conferences, using the same campaign-season passages, so they are not independent confirmations.
- Strongest results: 02 (year-level 2012 withdrawal framing, moderate) and 03 (period-level end/transition rise ex-Iraq, moderate). Both are lexical and need hand validation.

## 4. Data sources

Project files (read-only, the project root): output/references.csv (4,741 passages); output/speeches_index.csv (5,026 speeches; dup_of empty); output/reaction_events.csv; output/reaction_items.csv; output/reaction_correlation.json; data/speeches.db (raw_text); data/reactions.json (13 events, 92 items); src/obama_afghan/score.py, detect.py, tone.py, reactions.py (read-only); README.md.

External sources (analyses 08-12):
- 08: https://en.wikipedia.org/wiki/United_States_military_casualties_in_the_War_in_Afghanistan (secondary; DoD-attributed monthly table)
- 08: https://www.everycrsreport.com/files/20121206_R41084_f61416a669ea9d115f8867df20c7e944ca927c0d.html (CRS R41084, annual cross-check)
- 08: https://dcas.dmdc.osd.mil/dcas/conflictCasualties/oef/byMonth and https://dcas.dmdc.osd.mil/dcas/pages/report_ofs_month.xhtml (attempted; not readable)
- 09: https://www.congress.gov/crs_external_products/R/PDF/R44116/R44116.11.pdf (CRS R44116 v11, quarterly troop table)
- 09: https://www.everycrsreport.com/files/20110329_RL33110_be1a00c99d668bee3b4ec4f6fc82e914f62c39f0.pdf (CRS RL33110, monthly troop table)
- 09: https://www.policyarchive.org/download/2588 (RL33110 Sep 2010 copy; not re-fetched by reviewer)
- 09: Brookings Afghanistan Index PDFs (examined; chart-only, not used)
- 10: https://news.gallup.com/file/poll/352841/210727Afghanistan.pdf (Gallup mistake series)
- 10: news.gallup.com/poll/122816, 144965, 144944, 141716
- 10: https://www.pewresearch.org/politics/2014/01/30/more-now-see-failure-than-success-in-iraq-afghanistan/ and https://www.pewresearch.org/politics/2011/06/21/record-number-favors-removing-u-s-troops-from-afghanistan/
- 11: https://www.presidency.ucsb.edu/statistics/data/barack-obama-public-approval (weekly approval table)
- 11: https://news.gallup.com/poll/151025/obama-job-approval-monthly.aspx; https://news.gallup.com/poll/113980/presidential-approval-ratings-barack-obama.aspx; Gallup snippets 152123, 149966, 148394, 153152 (search snippets)
- 12: https://clerk.house.gov/evslegacy/ and https://clerk.house.gov/evs/{YYYY}/rollNNN.xml (House roll XML)
- 12: https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{111..114}_{1,2}.xml (Senate menus)
- 12: https://www.rollcall.com/2010/07/01/anti-war-liberals-put-afghanistan-to-three-votes/ (fetched); Council for a Livable World, The Nation, NPR, Himes, ProPublica (search snippets only; ProPublica not used for numbers)

Not reached: congress.gov bill text (HTTP 403 for analysis 12); iCasualties (404); Gallup approval 2011-2016 from other pollsters.

## 5. Limitations

- Lexical and rule-based measures throughout (frames, category, war-likelihood score, 50% threshold). None hand-validated at scale; scorer tuned on 30 labels.
- Passage-level tests treat passages as independent in most analyses; speech-clustered checks were run only in 01-04. Other p-values are overstated.
- Many uncorrected tests (roughly 12-54 per analysis in several cases). No family-wise correction across the study.
- Small panels (96, 95, 31 periods) and few event clusters (8-12) limit power. Nulls are weak evidence of no effect.
- Casualty and congressional inputs are partly secondary or unverified.
- Post-hoc choices (thresholds, May 2012 exclusion, tight vs broad regexes, dedupe rules) were made after viewing results in several analyses.
- No analysis supports causal claims. Granger results are predictive only.

## 6. Recommended next steps

1. Hand-code a stratified sample (about 100) of withdrawal, end, transition, and combat frame matches (by year and Iraq mention) to measure precision. Top priority for 02 and 03.
2. Build the Iraq filter into the frame regex and report campaign-window and governing-period effects separately (02, 03).
3. Re-run 01 and 03 with speech-clustered inference and a scorer-free outcome (fill llm_score, or hand labels) to remove scorer circularity.
4. Fix 08's test design: difference only where needed, use trend-stationarity tests, select lags by information criteria with a cap above 6, and use HAC or block bootstrap.
5. Obtain primary DoD DCAS monthly data to replace the Wikipedia table (08).
6. Validate the 50% threshold against the existing 30 labels before further monthly panel work (05, 11).
7. For 12, obtain text for the 14 unverified amendments and 6 supplemental votes; separate them from NDAA/DoD.
8. For 10 and 11, add a time-controlled panel model and verify the Gallup Nov 2009 approval value (35).
9. Report 04 pairing with and without detector INDIRECT cues and the 'two wars' regex.
10. Do not publish the 04 pre/post rise, the 05 first-difference correlation, or the 03 event-break claim without these corrections.

## 7. Charts (relative to output/analyses/)

01_venue/chart_venue.png; 02_election/election_frame.png; 03_framing_shift/framing_shift.png; 04_iraq_pairing/pairing_by_year.png; 05_salience_tone/salience_tone.png; 06_reaction_lean/lean_split_correlation.png; 07_opinion_vs_news/chart.png; 08_casualties/casualties_vs_rhetoric.png (not verified in review); 09_troops/troop_vs_rhetoric.png; 10_public_opinion/out/chart_opinion_vs_volume.png; 11_approval/approval_vs_afghan.png; 12_congress/event_study.png
