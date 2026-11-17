# 03_framing_shift: framing shift over the Obama presidency (2009-2016)

**Question.** Does the monthly share of passage categories (war_direct, war_adjacent, aid_diplomacy_civil, incidental) and of lexical frames (combat; transition/advise/Afghan-lead; end/withdraw/home) change over 2009-2016? Where are the change points, and do they line up with the announcement dates in `reaction_events.csv`?

**Data.** `output/references.csv` (4,741 rows). Kept the four categories, dates 2009-01-01 to 2016-12-31 (drops 11 passages dated Jan 2017). Questioner passages (rationale `questioner_not_president`, n=104 among the four categories) excluded from the main sample. `speeches_index.csv` has no non-empty `dup_of`, so nothing dropped. Main sample n = 4,582 passages, 96 months (min 3, median 26, max 300 passages per month; 13 months with n<10). Events from `reaction_events.csv` (13 dates, 2009-02-17 to 2016-07-06).

**Method.**
- Frames are regex matches on passage text (see `results.json`, key `frame_regex`). combat = combat/surge/fight/fought/offensive/insurgen/battl; transition = transition/transfer/train/advis/handover/Afghan-led/Afghan security forces; end = withdraw/drawdown/come home/troops home/home by/end-of-war-or-mission.
- Change points: binary segmentation on passage-level 0/1 indicators (passages ordered by date). Binomial likelihood-ratio split, splits only at month boundaries, at least 30 passages per side, permutation p (499 shuffles within segment), alpha 0.05, max depth 4. Pettitt test on the same indicator (approximate p).
- Event comparison: break dates within ±30 and ±60 days of an announcement, against a Monte Carlo null (10,000 draws of 12 uniform random dates over 2009-01-20..2016-12-31).
- Sensitivity: questioner-inclusive, and high-likelihood subsets final_score_pct >=30, >=50, >=70.
- Period comparison: 2009-11, 2012-14, 2015-16 pooled shares, chi-square test across the 3 periods.

**Numbers (main sample, n=4,582 passages).**

| measure | overall | 2009-11 | 2012-14 | 2015-16 | chi2 p (3 periods) |
|---|---|---|---|---|---|
| war_direct | 0.460 | 0.431 | 0.489 | 0.472 | 0.0011 |
| war_adjacent | 0.298 | 0.316 | 0.285 | 0.273 | 0.035 |
| aid_diplomacy_civil | 0.058 | 0.062 | 0.050 | 0.066 | 0.18 |
| incidental | 0.184 | 0.190 | 0.175 | 0.189 | 0.44 |
| frame combat | 0.092 | 0.092 | 0.088 | 0.100 | 0.61 |
| frame transition | 0.137 | 0.115 | 0.159 | 0.147 | 0.00026 |
| frame end | 0.072 | 0.038 | 0.123 | 0.046 | 6.7e-25 |

Detected breaks, main sample (binseg, permutation p; Pettitt p is approximate):

| series | binseg breaks (p) | Pettitt date (p) |
|---|---|---|
| war_direct | 2012-12-03 (0.002), 2016-09-06 (0.002) | 2012-05-02 (0.0002) |
| war_adjacent | 2012-11-01 (0.006) | 2012-11-02 (0.044) |
| aid_diplomacy_civil | 2012-06-01 (0.018), 2015-03-02 (0.012), 2015-10-02 (0.022) | 2012-05-02 (0.55) |
| incidental | 2012-11-01 (0.002), 2012-12-03 (0.026), 2016-09-06 (0.002) | 2013-01-11 (0.77) |
| frame combat | 2011-09-10 (0.004), 2013-02-07 (0.008), 2015-11-02 (0.026) | 2013-05-23 (0.42) |
| frame transition | 2010-07-01 (0.002), 2016-09-06 (0.028) | 2010-11-19 (0.0008) |
| frame end | 2011-06-07, 2012-02-03, 2012-06-01, 2012-11-01, 2015-10-02 (all p<=0.026) | 2011-05-30 (4e-5) |

Sensitivity (binseg breaks, abbreviated):
- Transition frame: 2010-07-01 in every subset (>=30, >=50, >=70: 2010-07-04).
- End frame: 2011-2012 breaks and 2015-10-02 recur across subsets (>=30: 2011-05-01, 2012-06-01, 2012-11-01, 2015-10-02).
- War_direct: 2012-06-01 in >=30, >=50, >=70. The >=70 subset adds 2009-10-13, 2010-05-12, 2010-06-05, 2011-04-01, but its Pettitt p is 0.096.
- Including questioner passages changes no break date.

Event match (12 unique pooled breaks, main sample):
- ±30 d: 6 of 12 breaks within 30 days of an event; null mean 2.98; MC p = 0.054.
- ±60 d: 6 of 12; null mean 5.31; MC p = 0.45.
- Nearest-break offsets: 2010-06-23 McChrystal (+8 d, break 2010-07-01); 2011-06-22 drawdown (-15 d, break 2011-06-07); 2012-05-21 Chicago (+11 d) and 2012-05-01 Kabul (+31 d) (break 2012-06-01); 2013-02-12 SOTU (-5 d, break 2013-02-07); 2015-10-15 withdrawal halted (-13 d, break 2015-10-02).
- No break near the early-2009 announcements (nearest 2010-07-01, +212 to +499 d), the 2009-12-01 West Point surge speech, or the 2014-05-27 Rose Garden announcement (nearest 2015-03-02, +279 d).

**Finding.** The clearest change is in the end/withdraw frame. It roughly triples in 2012-14 (12.3%) versus 2009-11 (3.8%) and 2015-16 (4.6%), with breaks in 2011-2012 that recur across thresholds. The transition/advise/Afghan-lead frame rises from about 11.5% (2009-11) to about 15-16% (2012-16), with a stable break around July 2010. War_direct share shifts slightly upward in 2012-14 (0.431 to 0.489, chi2 p=0.001). Combat-frame share is flat (p=0.61). Aid/diplomacy and incidental shares show no reliable shift. Breaks cluster in 2011-2013 and do not match the 2009 surge announcements. Announcement matches are only weakly above chance (±30 d p=0.054, ±60 d p=0.45), so the drawdown-era turn is visible but the event alignment is loose.

**Caveats.**
- Passage-level tests treat passages as independent. Many passages come from the same speech or day, so permutation and Pettitt p-values are anti-conservative. Read them as descriptive.
- Binary segmentation is not multiplicity-corrected across the 7 series × 5 subsets.
- Monthly n is small and uneven (median 26; 13 months <10; 2012-05 has 300 passages from the Kabul/Chicago period). Monthly shares are noisy and partly track speech volume.
- The category shares are rule-derived (`category` from the detector), not stance labels.
- Frame lexicon precision was not measured. Spot checks show false positives: "fight for a job", "combating al-Qaeda", "fighters" (carrier aircraft), "democratic transfer of power" (Afghan election). The end regex is narrow and misses phrasing like "bring our troops home" variants.
- VADER tone was not used here. Tone is word valence, not stance, so it is not part of this framing analysis.
- Breaks in the pooled event test are not independent (the 2012 cluster appears in several series).

**Files.** `analysis.py` (rerun: `.venv/bin/python -I output/analyses/03_framing_shift/analysis.py`), `results.json`, `monthly_shares.csv`, `period_shares.csv`, `framing_shift.png`, `run.log`.
