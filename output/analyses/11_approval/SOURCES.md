# SOURCES (11_approval) — retrieval date 2026-11-16

## Used in the analysis

1. **UCSB American Presidency Project — Barack Obama Public Approval (weekly table)**
   - URL: https://www.presidency.ucsb.edu/statistics/data/barack-obama-public-approval
   - Retrieved by: `curl` with generic User-Agent (`Mozilla/5.0 (research-bot; generic)`), saved as `raw/ucsb_obama_public_approval.html` (386,398 bytes, HTTP 200). Table parsed with a regex-based HTML parser into `raw/ucsb_obama_public_approval_raw.csv` (418 data rows + header; columns Start Date, End Date, Approving, Disapproving, Unsure/NoData, Democrats/Independents/Republicans Approving).
   - Coverage: 01/19/2009 – 01/19/2017, 7-day windows.
   - Attribution caveat: the page itself does not name the pollster (WebFetch summary said so). The values match Gallup's published monthly figures (16 points checked, mean abs diff 0.37 pts; see validation below). The general UCSB presidential-job-approval page states "Data adapted from the Gallup Poll and compiled by Gerhard Peters", but that note was not seen on this Obama page itself. Treat the series as Gallup-derived, not confirmed as Gallup-labelled for this specific page.
   - Derived file: `approval_weekly_clean.csv` (start, end, approve, disapprove, unsure), produced by `analysis.py`.

2. **Gallup — Obama Job Approval (Monthly), 2016–2017**
   - URL: https://news.gallup.com/poll/151025/obama-job-approval-monthly.aspx
   - Retrieved by: WebFetch (summarized extraction of the page table, not raw HTML). Values used: Apr 2016 50, May 51, Jun 52, Jul 51, Aug 51, Sep 52, Oct 54, Nov 56, Dec 56 (% approve). Page states "Each result is based on a monthly aggregate", telephone interviews ~15,000 adults per month, ±1 point MOE.
   - Used only for validation (`validation_vs_published_gallup.csv`).

3. **Gallup — Daily tracking, Obama approval (Jan 2017 3-day rolling averages)**
   - URL: https://news.gallup.com/poll/113980/presidential-approval-ratings-barack-obama.aspx
   - Retrieved by: WebFetch. Table 01/07–01/19/2017 (55–59% approve). Consistent with UCSB weekly 01/09–01/15 = 57 and 01/16–01/19 = 59. Used as a sanity check only; not in the validation table.

4. **Gallup — monthly text figures 2011–2012 (used for validation)**
   - Sources: Gallup articles surfaced by WebSearch, e.g. https://news.gallup.com/poll/152123/Obama-Averages-Approval-3rd-Year.aspx, https://news.gallup.com/poll/149966/obama-september-approval-rating-remains-term-low.aspx, https://news.gallup.com/poll/148394/obama-averages-approval-june-par-2010-2011.aspx, https://news.gallup.com/poll/153152/obama-approval-averages-february.aspx
   - Retrieved by: WebSearch result snippets only (full pages were not fetched). Values used: Jan 2011 49, May 2011 50, Jun 2011 46, Aug 2011 41, Sep 2011 41, Feb 2012 45, Aug 2012 45.
   - Caveat: these are snippet-level figures; treat as indicative.

## Checked and not usable

- UCSB Presidential Job Approval page (https://www.presidency.ucsb.edu/statistics/data/presidential-job-approval): 14 links to one Google Sheet (`1iEl565M1mICTubTtoxXMdxzaHzAcPTnb3kpRndsrfyY`), one per president. Exported all 13 gid tabs plus the default tab as CSV (`raw/g_*.csv`, `raw/g_default.csv`). None contains Obama 2009–2017. Tabs: 1067240630 = Bush 2001–2009; 671375968 = Trump 2017–2021; default = 2021–2022. The Obama tab was not located.
- Gallup Presidential Job Approval Center interactive (https://news.gallup.com/interactives/185273/...): no data.
- Gallup Obama public approval pages: only summary tables (2017 and 2016–17).
- Wikipedia "Public image of Barack Obama": no Gallup approval table in the portion read.
- Statista (https://www.statista.com/statistics/205284/...): HTTP 403.
- RealClearPolitics poll list (https://www.realclearpolitics.com/epolls/other/president_obama_job_approval-1044-test_newnum.html): HTTP 403.
- Gallup Obama monthly series for 2009–2015 (e.g. "Obama Averages 47.9% Job Approval", https://news.gallup.com/poll/202742/...): not fetched; the UCSB weekly table was used instead.

## Project data (read-only, the project root)

- output/references.csv (4,741 passages; 1,107 speeches; columns final_score_pct, rationale, tone, tone_label, date, speech_id). Questioner passages identified by `questioner_not_president` in `rationale` (109 rows).
- output/speeches_index.csv (5,026 rows; 5,023 status=ok; 0 with non-empty dup_of in this file).
- data/speeches.db table `speeches` (status='ok' and dup_of null/empty): raw_text, used to count words per month (8,578,374 words across 5,023 speeches).
