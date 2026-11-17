# Afghanistan in Obama's speeches, 2009–2017

**Live site:** https://danielried.github.io/obama-afghanistan-references/

This project finds every passage in Barack Obama's presidential speeches and statements (January 20, 2009 to
January 20, 2017) that mentions or plausibly alludes to Afghanistan. Each passage gets an **estimated likelihood
(0–100%)** that it concerns the US war there, plus a tone score and a link back to the official text. On top of
that, the project measures how the press received 13 key announcements, and runs 12 follow-up analyses that compare
the President's rhetoric with outside data such as casualties, troop levels and polling.

The likelihood is a transparent rule-based estimate, **not ground truth**. Read the passage before relying on a score.

## Contents

- [What the site shows](#what-the-site-shows)
- [Data collected](#data-collected)
- [Resources used and why](#resources-used-and-why)
- [How it was computed](#how-it-was-computed)
- [Results](#results)
- [Limitations](#limitations)
- [About this repository](#about-this-repository)

## What the site shows

`index.html` is a single self-contained page, about 8 MB, with all data embedded. It has six tabs:

| Tab | What it does |
|---|---|
| Passages | A monthly timeline stacked by category, with the tone of each month shown underneath. Drag across it to filter by date. Next to it are filters for category, tone, minimum likelihood, date and search, a list of passages, and a reader that shows each passage in context with a link to that spot in the official source. Keys: `j`/`k` move through the list, `/` searches, `Esc` closes the reader. The filtered list can be downloaded as CSV. |
| Speeches | Every speech with its passage count. Select one to read only its passages. |
| Patterns | A year-by-month heatmap of passage counts and the most frequent matched terms. Both follow the current filters. |
| Press reaction | 13 key announcements: the President's tone in the 14 days after each one, against how the press and Twitter reacted, with every source linked. |
| Findings | Plain-language results of the 12 follow-up analyses, rated after independent review, with the numbers, method and the reviewer's concerns. |
| About the data | Sources, method and limits, in short form. |

Filters are stored in the URL, so a filtered view can be shared as a link. The page follows the system light or dark
setting, and there is a toggle in the top right corner.

## Data collected

| Dataset | Size | Notes |
|---|---|---|
| Presidential documents enumerated | 7,811 | Every GovInfo DCPD package in the date range |
| Non-speech documents skipped | 2,785 | Proclamations, executive orders, nominations, lists of acts approved, and similar |
| Speeches and statements kept | 5,026 | 5,023 with full text, 3 with text missing at the source |
| Speeches with at least one passage | 1,107 | |
| Afghanistan passages | 4,741 | 3,935 score 50% or higher |
| Passages by category | | War, direct 2,154; war-adjacent 1,403; incidental 870; aid, diplomacy and civil 270; unrelated 34; political background 10 |
| Passages by tone | | Positive 2,392; negative 1,451; neutral 898 |
| Press reaction items | 92 | 88 press items and 4 tweets across 13 events. Each has a stance and political-lean label. |
| Hand-labeled calibration passages | 30 | Labeled yes, possible or no, and used to tune the scorer |
| Outside series (follow-up analyses) | 5 | Monthly US deaths, troop levels, Gallup and Pew war polling, Gallup job approval, House and Senate roll calls |

Speeches by year: 2009 716, 2010 754, 2011 658, 2012 643, 2013 567, 2014 623, 2015 558, 2016 492,
2017 15 (January 1 to 20).

## Resources used and why

### Speech text

| Resource | Used for | Why |
|---|---|---|
| [GovInfo, Compilation of Presidential Documents (DCPD)](https://www.govinfo.gov/app/collection/cpd) and the [GovInfo API](https://api.govinfo.gov/docs/) | **All speech text** | It is the official record, published by the US Government Publishing Office, and it is public domain. The API serves each document by ID, so no HTML listings had to be scraped. Every passage links back to its GovInfo page. |
| [Obama White House archive](https://obamawhitehouse.archives.gov/) | Fallback collector, not in the final data | A static mirror with full text. It was considered for cross-checks, but GovInfo already covered the range. |
| [UCSB American Presidency Project](https://www.presidency.ucsb.edu/) | Fallback collector, not in the final data | It mirrors the *Public Papers* and also covers pre-2009 material. Its crawl delay is 10 seconds, so a full crawl is slow. |
| [Miller Center](https://millercenter.org/the-presidency/presidential-speeches) | Considered as a checklist | It covers major speeches only, so it suits coverage checks but cannot serve as a primary source. |
| C-SPAN | Not used | Its robots.txt disallows transcripts. |

### Tone and analysis

| Resource | Used for | Why |
|---|---|---|
| [VADER sentiment](https://github.com/cjhutto/vaderSentiment) (Hutto and Gilbert, 2014) | Tone of each passage's wording, from −1 to +1 | A fixed, public, rule-based word list. Results are reproducible and can be inspected, with no model training. |
| Python: `requests`, `beautifulsoup4`, `lxml`, `PyYAML`, SQLite | Collection, parsing and storage | Standard, well-tested tools. HTTP responses are cached, so runs can resume. |
| Python: `pandas`, `scipy`, `statsmodels`, `matplotlib` | The 12 follow-up analyses | Correlation, regression, time-series tests (ADF, Granger), multiple-testing correction and charts |

### Press reaction (13 events)

Press items and tweets were found by web research. Each item was then fetched again and checked by a second pass,
and every one is linked on the Press reaction tab. Only 4 tweets could be confirmed, because historical Twitter
archives were not available.

### Outside data for the follow-up analyses

| Analysis | Source | Why this source |
|---|---|---|
| US military deaths | [Wikipedia monthly table](https://en.wikipedia.org/wiki/United_States_military_casualties_in_the_War_in_Afghanistan), which attributes its figures to the Department of Defense. Cross-checked against [CRS report R41084](https://www.everycrsreport.com/files/20121206_R41084_f61416a669ea9d115f8867df20c7e944ca927c0d.html). | The primary DoD casualty site (DCAS) could not be read automatically, and iCasualties is offline. The reviewer confirmed the saved series matches the Wikipedia table cell for cell. It has not been checked against DoD directly. |
| US troop levels | CRS reports [R44116](https://www.congress.gov/crs_external_products/R/PDF/R44116/R44116.11.pdf) (quarterly) and [RL33110](https://www.everycrsreport.com/files/20110329_RL33110_be1a00c99d668bee3b4ec4f6fc82e914f62c39f0.pdf) (monthly) | Nonpartisan Congressional Research Service tables, compiled from Defense Department figures |
| Public opinion on the war | [Gallup's "Was it a mistake?" series](https://news.gallup.com/file/poll/352841/210727Afghanistan.pdf) and Pew ([2014](https://www.pewresearch.org/politics/2014/01/30/more-now-see-failure-than-success-in-iraq-afghanistan/), [2011](https://www.pewresearch.org/politics/2011/06/21/record-number-favors-removing-u-s-troops-from-afghanistan/)) | The longest consistent question wording available for the whole period |
| Presidential job approval | [UCSB weekly Gallup approval table](https://www.presidency.ucsb.edu/statistics/data/barack-obama-public-approval), spot-checked against [Gallup](https://news.gallup.com/poll/113980/presidential-approval-ratings-barack-obama.aspx) | A complete weekly series in one table |
| Congressional votes | [House roll-call XML](https://clerk.house.gov/evslegacy/) and [Senate vote menus](https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_111_1.xml) | The official vote records, with dates and margins |

All outside data was retrieved on November 16, 2026.

## How it was computed

### Main pipeline

1. **Collect.** List every DCPD package for each year through the GovInfo API, fetch its text, and store it unchanged in
   SQLite. Proclamations, executive orders and other non-speech documents are skipped. Responses are cached and
   requests are rate-limited.
2. **Clean.** Check for duplicate copies of the same speech across sources (same or adjacent date, similar title
   and text). Only GovInfo went into the final data, so none were found. GovInfo's editor's `NOTE:` paragraphs are skipped
   because they are not the President's words. Paragraphs from reporters (`Q.`) and the audience are kept but flagged.
3. **Detect.** Split each speech into paragraphs and match a term list:
   - Strong terms such as Afghanistan, Kabul, Taliban, ISAF, Helmand and Karzai.
   - Ambiguous terms such as "Afghan" and "Ghani".
   - Indirect phrases such as "the surge", "two wars" and "longest war".
4. **Score.** Each passage starts from a base score for its strongest term and is adjusted by its context:
   - Raised for war language (troops, combat, withdrawal, casualties).
   - Raised for speeches that mention Afghanistan many times.
   - Raised for dates within a week of a key announcement.
   - Raised slightly when the speech title points to a military setting (troops, West Point, Bagram, NATO and similar).
   - Lowered for reporters' questions and passing mentions.
   - The rule is deliberately strict: routine diplomacy, elections, history and veterans' benefits score low.
   - Each passage gets a category and a written rationale that lists every adjustment.
   - The scorer was tuned on 30 hand-labeled passages.
   - An optional LLM layer is built in but was **not used**.
5. **Tone.** VADER compound score of the passage text, labeled positive at +0.05 or more and negative at −0.05 or
   less. It measures word choice, not the President's stance: war vocabulary pulls a resolute statement negative.
6. **Press reaction.** For each of 13 events:
   - Statement tone is the average tone of the President's passages from the event date through 14 days after.
   - The reaction index is (supportive − critical) ÷ all items found, from −1 to +1.
   - Pearson and Spearman correlations are computed across the 12 events that have at least 3 passages and 3 press items.
7. **Report.** Everything is written to CSV and JSON, and to this self-contained HTML page.

### Follow-up correlation study

Twelve analyses were each run as a separate script. A second, independent reviewer then:
- re-ran each script and confirmed the numbers reproduce;
- read the code for errors;
- spot-checked outside figures against their source pages;
- downgraded claims the evidence did not support.

The site and the table below report the reviewer's corrected rating. All 12 scripts reproduce exactly.

Methods used, depending on the question:
- Kruskal–Wallis and Mann–Whitney tests with Holm correction.
- Chi-square tests and negative-binomial regression of mention rates.
- Logistic regression with errors clustered by speech.
- Change-point tests.
- Detrended and first-differenced correlations, lagged cross-correlations, ADF stationarity tests and Granger tests.
- Permutation event studies around vote dates.

## Results

### Press reaction

Across 12 events, the President's statement tone and the press reaction moved together moderately:
- Pearson r = 0.53 (p = 0.077).
- Spearman ρ = 0.54 (p = 0.068).

That is **not statistically significant**: with this few events, it could be chance. Counting tweets as well, the
link is weaker (r = 0.37, p = 0.24).

### Follow-up analyses

| Analysis | Rating after review | Result |
|---|---|---|
| Speech venue | Weak | Per word, Afghanistan comes up about 2.4 times as often in press conferences as in ordinary remarks, and 1.4 times as often in written statements. Score differences between venues are small and partly built into the scorer. |
| The 2012 election year | **Moderate** | In 2012, 32% of high-likelihood passages used withdrawal language, against 9% in other years. Afghanistan did not come up more often that year, and the data cannot separate the campaign from where the war stood. |
| Framing over the two terms | **Moderate** | Language about ending the war rose from 1.8% of passages (2009–11) to 8.6% (2012–14), even with Iraq mentions removed. The turning points do not line up with the major announcements. |
| Iraq and Afghanistan together | Weak | About one passage in five also mentions Iraq. An apparent rise after December 2011 disappears once campaign speeches and speech type are accounted for. |
| How often vs. how warmly | No link found | Months with more mentions were not reliably warmer or colder in tone (r = 0.16, p = 0.12, 97 months). |
| Press reaction by outlet lean | Weak | The tone–reaction link did not clearly differ by outlet lean (p = 0.13). Left-leaning outlets were more critical than centrist ones. |
| Opinion vs. news | Weak | Opinion pieces were far more critical than news reports (65% against 12% negative). This cannot be separated from outlet lean. |
| US military deaths | Weak | Monthly deaths did not predict how often or how warmly Afghanistan came up, in either direction. |
| US troop levels | Data gap | No solid link. The data has only 31 quarters, and the apparent correlations reflect shared trends over time. |
| Public opinion on the war | Weak | Mentions fell as more Americans called the war a mistake (ρ = −0.83, 11 polls), but most of this is a shared time trend (ρ = −0.54, p = 0.11 once time is removed). |
| Presidential job approval | Weak | Approval did not move with how often Afghanistan came up (r = 0.12, p = 0.26). |
| Congressional votes | No link found | Mentions did not change around war votes. With 7 clearly Afghanistan-specific votes, the test has little power. |

**In short:** two results hold at moderate strength. In 2012 the President's Afghanistan passages leaned much more
toward withdrawal, and "ending the war" language rose after 2011. Neither has been hand-validated yet. Outside
events (deaths, troop levels, approval and votes) showed no reliable link to how often or how warmly Afghanistan
came up.

## Limitations

- Likelihood scores, categories and framing word lists are rule-based. They have been checked against only 30 hand
  labels, and the scorer was tuned on those same labels, so its accuracy is untested on new data.
- Speeches from before January 2009 (Senate and campaign years) are not included. DCPD may omit some items.
- Reporter-question detection only flags the first paragraph of each question.
- VADER measures word valence, not stance.
- Press stance labels are judgments, the sample per event is small (4 to 10 items), and only 4 tweets could be
  confirmed.
- Many follow-up tests were run without a study-wide correction for multiple comparisons. Some analyses with few
  data points (11 polls, 31 quarters, 7 votes) have little power, so a null result is weak evidence of no effect.
- Some outside data is secondary: the casualty figures come from a Wikipedia table that cites DoD, because the DoD
  site could not be read automatically.
- No result here shows cause and effect.

## About this repository

This repository holds the published site only: `index.html` and this README. GitHub Pages serves it from the `main`
branch. The collection pipeline, the tests, the 12 analysis scripts and their outputs (CSV, JSON and charts) are
kept in a separate working project. The page itself has no build step and loads no scripts from outside. It only
requests two web fonts from Google Fonts, and falls back to system fonts without them.
