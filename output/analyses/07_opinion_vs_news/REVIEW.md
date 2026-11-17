# REVIEW: 07_opinion_vs_news

Reviewer: independent re-run and checks. Analyst files not modified.

## 1. Reproduction
- Re-ran `analysis.py` with `-I` venv python. Exit 0. Output matches prior `run_stdout.txt` exactly.
- All key numbers reproduce: negative share 6/51 vs 20/31; chi2=29.35 df=3; paired mean diff 0.506 (t p=0.008, Wilcoxon p=0.011); news r=0.625 p=0.030, rho=0.559 p=0.059; opinion r=-0.213 p=0.507; interaction b=-1.741, cluster p=0.113, perm p=0.0695; sensitivity range as stated.
- Statement tone recomputed in script matches `reaction_events.csv` within 0.0005 (rounding), n statements match all 13 events.
- Items: 92 total, JSON and `reaction_items.csv` agree on item_type and stance.

## 2. Independent checks (`output/analyses/07_opinion_vs_news_review/check.py`)
- Date alignment OK: item lag from event date is 0 to 11 days, none outside the 14-day window. Statement window is forward-only from event date, not tied to item dates.
- Per-event news r with leave-one-event-out: range r=0.465 to 0.714. Dropping 2011-05-01 (the event with only 1 news item) gives r=0.465, p=0.149. With n>=2 news events (n=11): r=0.465, p=0.149. The headline r=0.63, p=0.03 depends on keeping a 1-item event.
- Lean confound (not in analyst caveats): opinion group lean = left 10, center 4, intl 3, right 3, unknown 3, missing 8. News lean = center 13, intl 8, left 5, right 4, unknown 2, missing 0 (plus missing in opinion). Opinion negatives: left 8 of 20 negatives; left opinion items: 8 of 10 negative. Stance coding ("against the President's decision") may partly capture antiwar outlet ideology, not genre.
- Cluster-robust level test (OLS stance ~ is_opinion, clustered by event, n=82): b=-0.561, se=0.101, p=0.0002. Naive OLS p=1.3e-05. Analyst's Fisher/chi2 p<0.0001 ignores clustering but still holds at the cluster level.
- Event-level paired test of negative share difference (12 events): mean diff 0.459, paired t p=0.014, Wilcoxon p=0.021.
- Duplicate URLs: Media Matters URL shared by an analysis item and a tweet (2009-03-27); PBS URL shared by a news item and a tweet (2014-12-28). Two Al Jazeera news items on 2012-05-21 (stances neutral, mixed). Tweets are excluded from main model, so no effect on main result; they enter sensitivity E.

## 3. Code review (analysis.py)
- No filter, date or join bug found. Event-level permutation (10,000 perms, 12 events) correct for the interaction.
- Stance coded -1/0/+1 with OLS: approximation for an ordinal outcome; mixed=0 merges "mixed" with "neutral". Acceptable but not stated as a caveat for the interaction model.
- Multiple comparisons: 4 per-event correlations, ~12 sensitivity models plus 12 LOEO fits, thresholds 30/50/70 all reported. None corrected. Headline correlation p=0.03 would not survive correction across the 4 correlations.
- Sensitivity variants B (p=0.046) and D (p=0.048) are below 0.05. The analyst's "p 0.05 to 0.66" summary rounds past these. Report as 0.046 to 0.66.
- Clustering: 12 clusters is too few for cluster-robust SEs. The permutation p is the better figure, as the analyst says.

## 4. Verdict
- Level finding (opinion items more negative than news): holds under clustering and paired tests. But confounded by outlet ideology (left-leaning opinion pieces dominate the negative stances). Report as "robust in this sample, not separable from lean".
- Slope finding (news tracks tone, opinion does not; the tone x opinion difference): not established. Interaction p=0.11 (cluster) / 0.07 (perm). Headline news r=0.63 falls to 0.47 (p=0.15) once the single-item event is dropped.
- Strength: downgrade the slope claim to "not supported / insufficient evidence". Keep "weak" overall. Level claim: moderate, with lean caveat.

## 5. Suggested changes to RESULT.md (not made)
- Add lean confound caveat and lean crosstab.
- Report news r with and without 2011-05-01 (0.63 vs 0.47).
- Report cluster-robust and paired level p values alongside Fisher p.
- Report sensitivity range as p 0.046 to 0.66.
- Add multiple-comparison note to the per-event correlations.
