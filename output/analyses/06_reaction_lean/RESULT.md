# 06_reaction_lean: statement tone vs press reaction, by outlet lean

**Question.** Does the correlation between statement tone and press reaction differ by outlet political lean (left / center / right / international / unknown)? Item-level: stance ~ statement tone + lean.

**Data (read-only).**
- `output/references.csv`: 4,741 passages with tone (VADER compound). Statement window = event date through +14 days, questioner passages excluded (same as `reactions.py`).
- `data/reactions.json`: 13 events, 92 items (88 press, 4 tweets). Stance is the researcher's judgment label (mixed = 0).
- Logic reused by importing `src/obama_afghan/reactions.py` (`analyse`, `stance_index`, `_corr`). Reproduction check: recomputed statement tone matches `output/reaction_events.csv` exactly (max diff 0.000); overall press r = 0.528 (n = 12) matches `reaction_correlation.json`.

**Data gap.** 30 of 92 items have no `political_lean` key (29 press, 1 tweet). 4 events have no lean on any item (2009-12-01, 2010-06-23, 2011-06-22, 2014-05-27); 2009-03-27 has one unlabelled tweet. Not imputed. Reported as `missing`. Lean-split analyses use the 62 labelled items.

**Method.**
1. Event-level, per lean: press-only stance index (positive minus negative over items of that lean) per event, correlated (Pearson, Spearman) with statement tone. Events need >= 3 statements. Sensitivity: >= 1 and >= 2 items per event; press+tweet variant.
2. Item-level: OLS (stance coded -1/0/+1, mixed = 0) on tone + lean dummies (reference = center), SEs clustered on event; HC1 for comparison. Ordinal logit (statsmodels OrderedModel), with and without cluster-robust SE. Models: main (62 items, 8 clusters), excluding weak_evidence (60), and including missing lean as its own category (92 items, 12 clusters).
3. High-likelihood threshold (final_score_pct) not applicable here (no references scoring used).

**Numbers.**

Lean-split, press index, >= 1 item per event:

| lean | items | events (n) | Pearson r | p | Spearman rho | p |
|---|---|---|---|---|---|---|
| left | 15 | 8 | 0.528 | 0.178 | 0.574 | 0.137 |
| center | 19 | 8 | 0.222 | 0.598 | 0.247 | 0.555 |
| right | 7 | 6 | 0.174 | 0.742 | 0.088 | 0.868 |
| international | 11 | 8 | 0.578 | 0.134 | 0.630 | 0.094 |
| unknown | 7 | 6 | 0.274 | 0.599 | 0.370 | 0.470 |
| (all press, reference) | 88 | 12 | 0.528 | 0.077 | 0.544 | 0.068 |

Sensitivity: >= 2 items per event leaves n = 4 (left, center), 3 (international), 1 (right, unknown). No correlation computable for right or unknown. Press+tweet (>= 1): right r = -0.342 (n = 6, 8 items, one tweet); unknown r = -0.095 (n = 6, 9 items).

Item-level OLS, main (n = 62, 8 clusters):

| term | coef | cluster SE | cluster p | HC1 p |
|---|---|---|---|---|
| statement tone | +0.521 | 0.323 | 0.107 | 0.526 |
| left (vs center) | -0.466 | 0.176 | 0.008 | 0.028 |
| international | -0.324 | 0.188 | 0.085 | 0.049 |
| right | -0.168 | 0.254 | 0.509 | 0.587 |
| unknown | -0.066 | 0.308 | 0.831 | 0.849 |

R^2 = 0.08. Excluding weak_evidence (n = 60): tone +0.580 (cluster p = 0.080), left -0.420 (p = 0.011). Including missing lean (n = 92, 12 clusters): tone +0.704 (p = 0.007), left -0.470 (p = 0.006), missing -0.173 (p = 0.024).

Ordinal logit, cluster-robust (main): tone +2.01 (p = 0.039), left -1.50 (p = 0.036), international -0.86 (p = 0.050), right -0.56 (p = 0.524), unknown -0.18 (p = 0.902). Naive (non-clustered) ordinal logit SEs give tone p = 0.39. The clustered ordinal SEs are unstable (tone SE shrinks when clustering), so treat them as unreliable.

Lean x stance counts (labelled items): center 5 mixed / 1 neg / 11 neu / 2 pos; international 2/3/6/0; left 1/8/4/2; right 0/3/3/2; unknown 1/4/0/4.

**Finding (descriptive).** Within each lean, the event-level correlation between statement tone and press stance is positive in all five groups (r from 0.17 to 0.58), but none is significant (all p >= 0.13, n = 6 to 8 events). Its magnitude does not clearly differ by lean. Item-level, the only lean difference that holds across specifications is that left-leaning items are more negative toward the decision than center items, about -0.4 to -0.5 on the -1/+1 scale (cluster p = 0.006 to 0.011; HC1 p = 0.03 to 0.06). Statement tone has a positive item-level coefficient (about +0.5 to +0.7) that is significant only in the with-missing model (cluster p = 0.007) and borderline elsewhere (p = 0.08 to 0.11), and it rests on 8 to 12 event clusters. Lean-split cells are tiny (right = 7 to 8 items, 6 events), so these are descriptive, not confirmatory.

**Caveats.**
- Cell sizes: right = 8 items total (7 press, 1 tweet); 6 events. Lean-specific correlations use 6 to 8 events and are not significant.
- Tone is event-level (13 events). Tone varies only across events, so the effective sample for the tone coefficient is 8 to 12 clusters. Cluster-robust SEs with few clusters are unreliable; HC1 is shown for comparison.
- Missing lean: 30 items (33%) unlabelled, concentrated in 4 events. Not random by outlet type; a "missing" dummy was added in the robustness model.
- Stance is a judgment label (mixed coded 0). 10 items had stance_agree = False; 9 flagged weak_evidence.
- VADER tone is word valence in the statements, not stance toward the war or decision. The analysis tests word-tone vs press stance, not position.
- Ordinal logit cluster SEs are unstable with 8 to 12 clusters; use only as a direction check.
- Multiple comparisons: 5 lean cells plus 3 model specifications; no correction applied.

**Chart.** `lean_split_correlation.png`: lean-specific press r with n and p (dashed = all-press r). Descriptive only.

**Re-run.** `.venv/bin/python -I output/analyses/06_reaction_lean/analysis.py` (writes `results.json`, `run.log`, chart).
