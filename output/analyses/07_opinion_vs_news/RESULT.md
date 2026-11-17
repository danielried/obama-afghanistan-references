# 07 Opinion vs news: do opinion items track statement tone differently from news reports?

## Question
Do opinion/editorial/analysis reaction items follow statement tone differently than news_report items, across the 13 key events in `data/reactions.json`?

## Data
- `data/reactions.json`: 92 items. Used for item type and stance. Matches `output/reaction_items.csv` on item_type and stance (checked in code).
- Groups: news = news_report (n=51). Opinion = opinion + editorial + analysis (n=31). Excluded from the main model: poll (6), tweet (4). Sensitivity E includes them as non-opinion.
- Statement tone: `output/references.csv`, mean VADER `tone` of Afghanistan passages from the event date through +14 days, questioner passages excluded. Recomputed in code and matches `output/reaction_events.csv` (n match, max diff 0.0005 from 3-dp rounding). This is passage word valence, not stance.
- Stance coding: positive=+1, negative=-1, neutral and mixed=0 (same as `reactions.py`).

## Method
1. Per-event stance index by group: (pos - neg) / n. Spearman and Pearson of statement tone vs index, per group.
2. Paired comparison of news vs opinion index in events having both.
3. Pooled group test of stance (chi-square, Fisher on negative share, Mann-Whitney).
4. Item-level OLS: stance ~ statement_tone * is_opinion, SE clustered by event (12 clusters, t reference). Event-level permutation test: shuffle event tone across events 10,000 times.
5. Sensitivity: final vs first-pass stance, drop weak_evidence, drop mixed, include polls/tweets, tone from passages with final_score_pct >= 30/50/70, leave-one-event-out.

## Numbers
| Item | Value |
|---|---|
| Negative share, news | 6/51 = 0.118 |
| Negative share, opinion | 20/31 = 0.645 (Fisher p < 0.0001) |
| Chi2 stance x group (4 stances) | 29.35, df 3, p < 0.0001 |
| Mean stance, news / opinion | -0.020 / -0.581 (Mann-Whitney p < 0.0001) |
| Events with both groups | 12. Mean(news idx - opinion idx) = +0.506; paired t p = 0.008; Wilcoxon p = 0.011 |
| Per-event corr tone vs news index (n=12) | Pearson r = 0.625, p = 0.030; Spearman rho = 0.559, p = 0.059 |
| Per-event corr tone vs opinion index (n=12) | Pearson r = -0.213, p = 0.507; Spearman rho = -0.218, p = 0.496 |
| Item model, tone slope (news reference) | b = 1.63, cluster SE 0.79, p = 0.062 |
| Item model, opinion extra slope (interaction) | b = -1.74, cluster SE 1.01, p = 0.113, 95% CI [-3.97, 0.49] |
| Event-level permutation p, interaction | 0.070 (10,000 perms) |
| Within-group slope, opinion | b = -0.11, SE 0.89, p = 0.90 (n=31, 12 clusters) |

Interaction sensitivity (b; cluster p):
- Base (n=82, 12 clusters): -1.74; p = 0.113
- First-pass researcher stance: -1.92; p = 0.046
- Drop weak_evidence (n=74): -1.81; p = 0.173
- Drop mixed (n=67): -1.76; p = 0.048
- Include polls/tweets (n=92): -0.68; p = 0.662
- Tone from passages with final_score_pct >= 30 / 50 / 70: -2.20 (p = 0.139), -2.13 (p = 0.120), -2.50 (p = 0.063)
- Leave-one-event-out: b ranges -0.92 to -2.62; cluster p ranges 0.050 to 0.189

Full tables: `model_sensitivity.csv`, `model_main.csv`, `per_event_indices.csv`, `per_event_correlations.csv`, `numbers_log.txt`.

## Finding
Opinion-type items are much more negative toward the President's decisions than news reports (negative share 65% vs 12%). This level difference is strong and survives the paired and pooled tests.

Whether opinion items track statement tone differently is not established. The news index rises with statement tone (r = 0.63, p = 0.03, n = 12 events). The opinion index is flat (r = -0.21). The item-level interaction is negative, as expected, but not significant: b = -1.74, cluster p = 0.11, permutation p = 0.07. Several sensitivity variants cross p = 0.05, but the sign and size are stable and the interaction is weak. Read this as a suggestive pattern, not a finding.

Most of the opinion-vs-news contrast is a level effect: opinion items sit near -1 whatever the tone, so there is little slope to track.

## Caveats
- 12 event clusters. Cluster-robust SEs are unreliable at this count, so the permutation p (0.07) is the more honest number. Leave-one-out and threshold variants move the p-value across 0.05.
- The event-level correlations are on 12 points, and the news index for 2011-05-01 is based on one item.
- Stance labels are judgments by a researcher, with a second-pass check. 10 items disagree between passes. The stance is toward the President's decision, not the speech wording.
- VADER tone is word valence, not stance. Statement tone is also computed from Afghanistan-mention passages only, not whole speeches.
- Items are not independent of outlet (several items come from the same outlet or author) and some have weak evidence (9 items; search snippet only).
- Opinion items are often negative regardless of tone, so a flat slope is partly a ceiling effect.
- Event 2013-02-12 has statements but no press items, so it is not in the item model.

## Files
- `analysis.py` (rerun: `.venv/bin/python -I output/analyses/07_opinion_vs_news/analysis.py`)
- `chart.png`, `numbers_log.txt`, `run_stdout.txt`, `per_event_indices.csv`, `per_event_correlations.csv`, `model_main.csv`, `model_sensitivity.csv`, `item_model_data.csv`
