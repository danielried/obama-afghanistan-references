# Review: 10_public_opinion (reviewer notes)

Scope: re-ran analysis.py (exit 0); read code and data; spot-checked external sources; scratch sensitivity script at /tmp/rev10/sens.py (analyst files not modified).

## Reproduction
- All key numbers reproduce from analysis.py output: A n_hi rho -0.833 p_exact 0.0015 p_perm 0.0027; A share_war_direct +0.732 p 0.0104; B n_hi -0.636 p 0.035; C tone +0.778 p 0.0135 (n=9); C count +0.337 p 0.34; time rho 0.815 p 0.0023; partial rho (thr50/30/70) -0.542 p 0.105 / -0.658 p 0.039 / -0.278 p 0.437; A tone -0.366 p 0.27.

## Errors and gaps
1. Dedupe filter is a no-op. speeches_index.csv dup_of is empty for all 5,026 rows. Text hash finds one group of 3 identical speeches (govinfo:DCPD-201000797, -201400210, -201500307), none removed. 65 refs rows repeat a (date, passage). Dropping repeats changes nothing in test A (rho -0.833 unchanged). Impact is nil here, but "duplicates removed" is false.
2. Selective reporting. Finding text omits the significant frame-share result (A share_war_direct +0.73, p=0.010; A share_aid_civil -0.65, p=0.03). It says partials are not significant "at thr 50 or 70" but omits thr30 partial -0.66, p=0.04.
3. "Most of this is a shared time trend" is overstated. Time partial cuts thr50 rho from -0.83 to -0.54 (p=0.11), attenuated, not removed.
4. Pooled questionnaire wording. 2009-2011 items ("military forces", comparison block) and 2013-2015 items ("sending troops to fight", looking-back block) are pooled into one series. Opinion-vs-time rho (0.82) may partly reflect the wording change. Not tested.
5. Non-independence and autocorrelation. Overlapping 30-day windows; 2010-07-08 and 2010-07-27 polls are 3 weeks apart with shared windows; permutation ignores time order; no autocorrelation handling. Effective n below 11.
6. Gallup footnote "^ asked of a half sample" (2008-08, 2009-07, 2010-07-08) not in caveats.
7. Test C direction is not in analysis.py. The "sign opposite to hypothesis" claim cannot be traced in code. C also uses post minus pre windows where pre overlaps the drop interval, so it is not a clean lead test. VADER is word valence (noted in caveats).
8. Denominator per 100 speeches includes interviews and press conferences; type mix not controlled.
9. Chart: axvspan(alpha=0) line is a no-op (harmless).

## External spot-checks (WebFetch, 2026-11-16)
- Gallup Nov 19-21 2010: approve 44, disapprove 49 - VERIFIED (S4).
- Gallup Feb 2010 approval 48 - VERIFIED (S4 text "down slightly from the 48%").
- Gallup Nov 2010 "up by eight points" implies summer 2010 approx 36 (44-8) - consistent with the 36 in the CSV.
- Gallup Nov 2009 approval 35 - NOT TRACED. Fetched S3 page did not contain it. Tagged in SOURCES.md as from "last November = 35" but not confirmed.
- Pew right-decision 69 (Jan 2006), 64 (Jan 2009), 56 (Nov 2011), 51 (Jan 2014, fieldwork Jan 15-19, n=1,504) - VERIFIED from Pew 2014 page. Question wording NOT verified (as caveated).
- Pew June 2011 57 (2011 article) - not re-fetched.
- Gallup mistake series (all 2008-2021 rows used) matches S1 PDF text (gallup_210727.txt) - VERIFIED.
- SOURCES.md: complete for the values used, except the untraced Nov 2009 approval 35.

## Verdict
Correlations reproduce. The contemporaneous count association is real in-sample but confounded by time and small n. Strength downgraded to weak. The tone-drop result (C) is exploratory and direction is unsupported in code. Finding text should report the frame-share and thr30 results and drop "most of this is time trend" wording.
