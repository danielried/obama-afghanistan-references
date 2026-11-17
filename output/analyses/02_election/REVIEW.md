# Review of 02_election (reviewer notes)

Scope: re-run, code read, independent recounts. Analyst files not modified. Review scripts in /tmp (rev02_*.py).

## 1. Reproduction
- Re-ran analysis.py with the venv python -I. Exit 0. results.json identical to the prior run (dict equality).
- Key numbers reproduce: 2012 vs other years withdraw 231/726 (31.8%) vs 297/3151 (9.4%); chi2 251.5, p_chi2 1.22e-56; Fisher p 1.8e-47; OR 4.48.
- Campaign vs midterm (non-May, repeats removed): 158/366 vs 63/816, OR 9.08, p_fisher 4.3e-44 (analyst said 2e-44 for 158/366 vs 63/816, which is the same test with rounding).
- Poisson camp12 RR 2.282 p 0.434; dispersion 47.84. Reproduced.

## 2. Input and filter checks
- references.csv: 4,741 rows, no speech_id that is a dup_of speech (index has 0 non-blank dup_of). The dup filter is a no-op here, which is fine.
- questioner flag: 109 rows with questioner_not_president in rationale. 58 hi50 passages are questioner (3,935 - 3,877). Method text says "questioner passages excluded (n=3,877)". That number is the remaining non-questioner count, not the excluded one. Wording error only.
- All speech_ids match speeches_index. Dates parse. No null final_score_pct.
- Type join in logit (lines 236-238) matches govinfo: prefix; IDs are identical in both files, so the type control is live.

## 3. Method problems (code)
- **Independence / clustering (major):** chi2 and Fisher treat passages as iid. Passages nest in speeches (922 speeches in hi50 nonq). Speech-clustered logit (cluster-robust by speech_id):
  - 2012 vs other years: OR 4.48, p = 1.6e-14 (naive p 1e-56)
  - campaign vs other: OR 4.23, p = 4.1e-13
  - campaign vs midterm only: OR 5.39, p = 5.8e-10
  The direction holds. The reported p-values are overstated by about 40 orders of magnitude. Effect is still significant.
- **Campaign vs 2012-as-year not separable (confirmed):** with year FE, camp12 is identified only from Nov 7-Dec 2012 hi passages (17). Logit OR 1.66 p 0.39. Poisson RR 2.28 p 0.43. The headline "campaign window" framing is not supported by the year-controlled models. The year-level claim (2012 > other years) is supported by the y12 model (OR 4.18, p 3e-40 naive; type and repeat controlled). Note Poisson year-FE also makes "mid" identified only from Nov-Dec months of 2010/2014; not flagged in RESULT.
- **Iraq contamination (not checked by analyst):** WITHDRAW regex has no Iraq filter. 44 of 227 campaign withdraw passages mention Iraq (also 13/66 midterm, 51/235 other). Stump lines ("end the war", "bring our troops home") are often Iraq. Tests:
  - Withdraw match counted only if no "Iraq" within 120 chars: campaign 27.2% (193/709) vs midterm 6.5% (53/821), OR 5.42, p 5e-29. 2012 vs others 26.9% vs 7.6%, OR 4.49.
  - Passages with no "Iraq" at all: campaign 30.5% vs midterm 7.1%, OR 5.74, p 9e-30.
  Effect survives. Iraq is a real contaminant of the measure but not the driver.
- **Lexical terms (minor):** "transition\w*" (82 "transition" + 35 "transitioning" in campaign hits) carries much of the signal. Analyst's no-transition sensitivity (27.7% vs 5.0%) is fine and should be the reported number alongside the full one.
- **Post hoc May exclusion:** the May 2012 cluster was excluded after the fact. Including May lowers the effect; excluding it is the headline "cleaner comparison". Both are reported, but the non-May result is the one carried into the finding. Flag as a forking choice; the full-campaign result (32.0% vs 5.7%) is the honest headline.
- **Repeat / stump-line threshold:** repeat share of non-May campaign withdraw passages depends on the near-dup rule:
  - 8-gram J>=0.5 (analyst): 12.7% (23/181)
  - 8-gram J>=0.3: 17.7%
  - 5-gram J>=0.3: 33.7%
  The "minor" framing is threshold dependent. After removing repeats the effect remains (OR 8.4-9.1 across all three rules), so the conclusion "not just stump-line repetition" holds, but "minor part" is overstated at the looser rules.
- **Per-speech "spike" (overstated):** raw counts show no spike: hi nonq 726 (2012) vs 718 (2009) and 720 (2010). Per speech, 2012 = 726/643 = 1.13 vs 2009 718/716 = 1.00 (binomial p 0.025, not clustered) and vs 2010 720/754 = 0.96 (p 0.0015). Speech volume fell (643 vs 716/754), so the per-speech rise is partly a denominator effect. The analyst's "speech volume did not rise" is true but the per-speech comparison is modest and not clustered. 2011 is also elevated (20.9% withdraw) and sits in the "other years" pool.
- **Threshold sensitivity:** th30/50/70 all give 2012-campaign withdraw > midterm (27.5/32.0/33.4% vs 5.4/5.7/8.1%). Good. Escalation share lower in 2012 at all three.
- **Context window:** context-based withdraw rate is higher in every period (campaign 52.8%) because the window is wider, so this is not a like-for-like robustness check. The analyst said context coding "holds"; direction holds, levels are not comparable.
- **Multiple comparisons:** many chi2/Fisher/logit tests unreported corrections. Given the p-values, correction does not change conclusions for the main contrast, but the subsidiary tests (e.g. Poisson p 0.43) are not informative.
- **Causation:** RESULT wording "framed more around withdrawal" is a lexical description, fine. No causal claim found in analysis.py. Campaign "effect" language should be dropped.

## 4. Independent checks done
- Recount 2012 vs other withdraw: 231/726 vs 297/3151 (matches).
- Iraq-local and no-Iraq subsets (above).
- Speech-clustered logits (above).
- Repeat thresholds (above).
- Per-speech binomial (above).

## 5. Verdict
- Reproduction: PASS. Code runs and matches.
- Headline "2012 framed more around withdrawal than other years": supported. Survives Iraq exclusion and speech clustering. Naive p-values overstated; use the clustered ones (p ~1e-13 to 1e-14).
- "Campaign window specifically": NOT supported. Year-controlled models do not separate campaign from 2012. Downgrade to descriptive.
- "Spike is real per speech": weak. Counts flat; per-speech difference modest; unclustered.
- "Stump-line repetition minor": partly supported. Depends on near-dup rule; removal of repeats leaves effect large.

Recommended strength: moderate (was strong). Strong only for the year-level withdrawal-share difference, and only with clustered p-values. Campaign-specific claim: weak/inconclusive.

Required fixes before reuse:
1. Report speech-clustered p-values (or GEE / speech-level bootstrap) in RESULT.
2. Add Iraq-local window exclusion to the frame coder and report it.
3. Drop or demote the "campaign window" claim; say the year-FE models cannot separate it.
4. Report repeat share under 2+ near-dup rules.
5. Report the full-campaign result as headline; present non-May as sensitivity.
6. Fix method text: questioner excluded = 58 hi50 passages; n=3,877 is the remaining count.
