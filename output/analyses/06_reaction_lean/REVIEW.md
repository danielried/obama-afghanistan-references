# REVIEW: 06_reaction_lean (skeptical statistical reviewer)

Scope: re-ran analyst's analysis.py, read reactions.py, ran independent checks (review_checks*.py in this folder). Analyst files not edited.

## 1. Reproduction
- analysis.py re-run: overall press r=0.528, p=0.077, n=12, rho=0.544. Matches shipped values. Reuse of reactions.analyse reproduces reaction_events.csv exactly (max tone diff 0.000000, n diff 0).
- Left press r=0.527, p=0.18, n_events=8 (independent recompute, review_checks3.py). Matches 0.528/0.178.
- Overall r independently recomputed from references.csv: r=0.528 p=0.078 (all refs); 0.508 p=0.092 (war_direct + war_adjacent only); 0.510 p=0.090 (drop passages from non-duplicate speeches with repeated text). Conclusion insensitive to these choices.

## 2. Code / data checks
- dup_of is empty for all 5,026 speeches, so the dup filter is a no-op. 188 refs rows share passage text (48 texts); 187 of those span different speech_ids (47 cross-speech repeats, 1 within-speech). Effect on r is negligible (0.528 -> 0.510).
- Questioner filter (rationale contains "questioner") applied in reactions.analyse. OK.
- Window = event date through +14 days, inclusive. Date comparison is ISO string compare, which is valid for YYYY-MM-DD.
- Tone is averaged over ALL Afghanistan-mention passages in the window, including incidental (870), aid/diplomacy (270), unrelated (34), political_background (10). Not a bug, but a design choice that is not flagged in the caveats. Core-category sensitivity gives the same direction (r=0.508).
- Multi-line CSV parsing: pandas read_csv with quoted newlines; 4,741 rows, unique ref_id, 0 tone NaN. OK.
- Event-level tone and press index are computed on 12 events (MIN_N=3 gate); 13th event excluded. The item-level models use 13 events (92 items), so the tone variable and the item sample use different event sets. Not wrong, but the analyst should state it.

## 3. Key substantive problems
1. **The question asked (does correlation differ by lean) is not tested directly.** Lean-specific r values are compared by eye. The formal test is tone x lean interaction: joint Wald p=0.13 (4 df, 8 clusters). No evidence the slope differs by lean. This is the headline answer and it should be "no significant difference" stated with p.
2. **Overclaim in finding text.** "Within every outlet-lean group the event-level correlation is positive (r 0.17 to 0.58)" holds only for the press-only variant. In the press+tweet variant right r=-0.342 and unknown r=-0.095 (analyst's own run.log). Must be corrected.
3. **Left-vs-center effect is robust to event FE, but the stance coding is the weak point.** Event FE model (stance ~ lean + event FE, cluster by event): left b=-0.56, cluster p=0.007; international b=-0.41, p=0.08. Within multi-lean events (8 events, classical OLS): left b=-0.56, p=0.032. Left items: 8/15 negative; center: 1/19 negative. Caveats: stance labels are researcher judgments; no evidence they were coded blind to outlet lean; 8 clusters; left items come mostly from 2009 events (7 of 15 from 2009-02-17 and 2009-03-27), so period effects remain possible even with event FE.
4. **Tone coefficient is not robust.** Main: cluster p=0.107, HC1 p=0.526. Excl weak: cluster p=0.080, HC1 p=0.499. With missing category: cluster p=0.007 (verified), but HC1 p=0.315. The analyst's sentence "reaches p<0.05 only in the with-missing model" uses the cluster p only, and that cluster SE is unreliable at 12 clusters. Treat tone as NOT significant. Interaction-model tone (center reference) b=+0.32, p=0.29.
5. **Missing-lean category is a catch-all.** 30 of 92 items (29 press, 1 tweet) lack lean; 4 events are fully unlabelled. The "with missing" model treats them as one lean level. Not informative for lean; it only adds events to the tone estimate. Its tone p=0.007 should not be headlined.
6. **Multiple comparisons.** Five lean cells x 3 min-item variants x 3 model specs, plus ordinal logit. No correction. Only the left effect survives across specs at p<0.05 (cluster and HC1 p 0.006-0.06); it is still exploratory.
7. **Ordinal logit cluster SEs** are unstable (tone SE shrinks from 2.35 to 0.97 when clustered). Direction only.
8. **Event-level correlation tests** use 6-8 events per lean with min 1 item; min-2 variant drops to 1-4 events and gives r near 0 for left (-0.03). Lean-specific r are not robust to the item threshold. The analyst reports the min-2 numbers in results.json but not in the finding.

## 4. Verdict
- Reproduces: YES.
- Strength: keep WEAK. Downgrade the tone claim to "not significant". The lean-difference-of-correlation question has no significant answer (interaction p=0.13). The left-vs-center stance gap is the one item-level result that survives event FE and HC1 (p~0.007-0.03), but it rests on researcher-coded stance and 8 clusters.
- Required fixes before reuse: (a) correct the "every group positive" claim; (b) report the tone x lean interaction Wald test; (c) state that tone is not significant under HC1; (d) add event-FE model; (e) state stance coding was/was not blind to lean; (f) flag tone averaging over incidental passages.
