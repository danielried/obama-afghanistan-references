# 04 Iraq-Afghanistan pairing

**Question.** How often does an Afghanistan passage (passage + context_before/after) mention Iraq too, by year/month? Did pairing fall after the Dec 2011 Iraq withdrawal? Does paired framing differ in tone/category? Trend test and paired-vs-unpaired tone.

**Data.** `output/references.csv` (4,741 rows, read-only). Excluded 109 questioner passages (`rationale` contains `questioner_not_president`); 0 duplicate-speech rows (`speeches_index.csv` dup_of empty). Analysis n = 4,632 passages from 1,103 speeches.

**Method.**
- Paired = `\biraq` AND `afghan` both in passage+context_before+context_after (case-insensitive). Passage-only pairing reported too.
- Split = 2011-12-18 (last US troops left Iraq). Sensitivity: 2011-10-21 (announcement).
- Trend: Mann-Kendall on yearly shares (9 yrs) and monthly shares (97 months with n>=1); Kendall tau; logit paired ~ years (speech-clustered SEs).
- Period test: chi-square / Fisher on pre vs post.
- Tone: VADER `tone` of passage wording only (word valence, not stance). Mann-Whitney.
- Category: chi-square on category mix.
- High-likelihood sensitivity at final_score_pct >= 30 / 50 / 70.
- Campaign confound: speech titles matching Campaign|Fundraiser|Debate|Victory Fund|Convention (regex, 748 passages / 304 speeches).

**Numbers.**

| Quantity | Value |
|---|---|
| Overall paired (window) | 1,037 / 4,632 = 22.4% |
| Overall paired (passage only) | 495 = 10.7% |
| Pre-split (<2011-12-18) paired | 19.3% (n=2,121) |
| Post-split paired | 25.0% (n=2,511) |
| Chi2 pre vs post | 20.72, p=5.3e-6 (Fisher p=4.9e-6) |
| Announcement split (2011-10-21) | 18.4% vs 25.6%, p=7.4e-9 |
| Logit post effect, time-adjusted (speech-clustered) | OR 1.92 (CI 1.02-3.63), p=0.044 |
| Logit post + campaign + time | post OR 0.90 p=0.69; campaign OR 5.26 p<0.001; time OR 1.02 p=0.81 |
| Non-campaign only: pre vs post | 17.6% vs 16.1%, p=0.21 |
| Excluding calendar 2012: pre vs post | 19.3% vs 17.3%, p=0.12 |
| Campaign-titled vs other | 50.9% (n=748) vs 16.9% (n=3,884) |
| 2012 monthly paired share | Jan 44%, May 13% (n=300), Sep 72%, Oct 59% |
| MK yearly S=4, z=0.31, p=0.75; tau=0.11, p=0.76 | No trend |
| MK monthly z=1.48, p=0.14 (97 months) | No significant trend |
| Yearly paired share | 2009 20.8, 2010 13.3, 2011 26.7, 2012 36.9, 2013 13.1, 2014 23.0, 2015 10.4, 2016 26.2 |
| Thresholds (score>=30/50/70) pre vs post | 19.3 vs 24.2 (p=1e-4); 20.1 vs 25.5 (p=7e-5); 21.6 vs 23.0 (p=0.48) |
| Tone, paired vs unpaired (mean VADER) | -0.080 vs +0.184, MWU p=3.7e-42 |
| Tone, post period only | -0.187 (n=627) vs +0.171, p=1.6e-43 |
| Tone, war_direct only | -0.138 (n=585) vs +0.216, p=6.7e-37 |
| Negative label share | paired 44.6% vs unpaired 26.4% (chi2 p=1.9e-36) |
| Category, war_direct share | paired 56.4% vs unpaired 42.6% (chi2 p=9.4e-19) |
| Rule score mean | paired 67.3 vs unpaired 67.8, p=0.88 |
| Framing "ending two wars" (tight regex) | 21 paired passages (12 pre, 9 post); 2.9% vs 1.4% of paired, pre vs post |
| "war of choice" cue | 2 paired passages total (not testable) |

**Finding.**
1. Pairing did not fall after the Dec 2011 withdrawal. It rose from 19.3% to 25.0% (p<0.001 unadjusted). That rise is almost entirely campaign-season content: campaign-titled speeches pair 51% vs 17% elsewhere, and after controlling for campaign titles the post-2011 effect disappears (OR 0.90, p=0.69). Non-campaign and 2012-excluded comparisons are not significant.
2. No monotone time trend in pairing (MK p=0.75 yearly; monthly p=0.14). Yearly values swing with campaign and speech-type mix.
3. Paired passages are more negative in VADER tone (mean -0.08 vs +0.18) and more often war_direct (56% vs 43%). The tone gap holds within war_direct (-0.14 vs +0.22) and in the post period. Read as word valence: paired passages use more negative vocabulary about war, not a demonstrated stance.
4. The explicit "ending two wars" framing is rare (21 of 1,037 paired passages). A broader regex hit 295, but it matched loose "end war" phrasing, so it was discarded. "war of choice" appears twice in the whole set, so that framing cannot be tested here.

**Caveats.**
- Denominator is references.csv, which only contains passages selected for Afghanistan content. Pairing shares are shares of Afghan-referencing passages, not of all speeches. Speech-level co-mention from speeches.db was not computed.
- Campaign flag is title-regex based. Speech titles were not hand-checked.
- Passage tone is VADER on passage wording only; context is not scored.
- Context windows come from the detector (adjacent paragraphs), so pairing may be caused by neighbouring text that the President did not link to Afghanistan.
- Post-2011 includes ISIL-era Iraq references (70 paired passages have an ISIL/ISIS/Islamic State term; 3.4% pre vs 8.9% post). Those are a different framing from the 2009-2011 combat-era Iraq references.
- Mann-Kendall on 9 yearly points has very low power; 2017 has n=11.
- Score threshold 70 gives no significant pre/post difference (p=0.48).

**Reproduce.** `.venv/bin/python -I output/analyses/04_iraq_pairing/analysis.py`. Outputs: `results.json`, `pairing_by_year.csv`, `pairing_by_month.csv`, `pairing_by_year.png`, `examples_two_wars.csv`, `examples_war_choice.csv`, `paired_sample.csv`, `run_log.txt`.
