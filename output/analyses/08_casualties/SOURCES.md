# SOURCES (retrieved 2026-11-16)

Generic User-Agent via WebFetch/WebSearch tools. No personal data sent.

1. **casualties_monthly_dod_wiki.csv** (2009-01..2016-12, 96 rows, US deaths, OEF/OFS all theaters)
   - URL: https://en.wikipedia.org/wiki/United_States_military_casualties_in_the_War_in_Afghanistan
   - Retrieved 2026-11-16 via WebFetch; values transcribed from the monthly table, which the page attributes to the US DoD (DCAS). Excludes six DoD civilian deaths.
   - Wikipedia is a secondary source. Primary DCAS monthly pages (https://dcas.dmdc.osd.mil/dcas/conflictCasualties/oef/byMonth and https://dcas.dmdc.osd.mil/dcas/pages/report_ofs_month.xhtml) returned only page titles to WebFetch (dynamic content), so monthly primary values could NOT be verified. Treat as DoD-derived partial-verified series.
   - Scope caveat: all OEF/OFS theaters, not Afghanistan only. Postwar OFS (2015-16) is Afghanistan-only in practice.

2. **casualties_annual_crs_r41084.csv**
   - URL: https://www.everycrsreport.com/files/20121206_R41084_f61416a669ea9d115f8867df20c7e944ca927c0d.html (CRS report R41084, dated 2012-12-06)
   - Retrieved 2026-11-16. Source note in report: DoD Statistical Information Analysis Division (DCAS), plus three DoD civilians.
   - Used as cross-check of the monthly series. Annual sums: 2009 Wikipedia=311 (matches CRS 311); 2010 Wikipedia=498 vs CRS 499; 2011 Wikipedia=411 vs CRS 414. Differences attributed to the civilian-death inclusion (not verified).

3. **Not obtained**: iCasualties Afghanistan-only monthly series (https://icasualties.org/oef/ returned 404 in this session; a fan-wiki mirror at military-history.fandom.com gave different figures and was NOT used). Coalition (non-US) monthly data not obtained.

4. Local data: output/references.csv, output/speeches_index.csv (read-only).
