# SOURCES - 09_troops (retrieved 2026-11-16)

Generic User-Agent used for all downloads. No personal data sent.

## Used for numbers

1. **CRS R44116 v11, "Department of Defense Contractor and Troop Levels in Iraq and Afghanistan: 2007-2017"**
   - URL: https://www.congress.gov/crs_external_products/R/PDF/R44116/R44116.11.pdf (PDF, 1,080,512 bytes, fetched by curl)
   - Local copy: `raw/R44116.11.pdf`; text extract `raw/r44116_11.txt` (pdftotext -layout)
   - Table used: **Table 1, "U.S. Armed Forces and Contractor Personnel in Afghanistan (Q4 FY2007-Q1 FY2017)"**, column "U.S. Armed Forces". Source note in the report: troop levels drawn from "Boots on the Ground" monthly reports to Congress; includes active and reserve components.
   - Values parsed programmatically from the text extract (analysis.py `parse_quarterly`), 37 rows Q4 FY2007 - Q4 FY2016. Q1 FY2017 = "Not Yet Available" (excluded).
   - Output: `troops_quarterly_CRS_R44116_Table1.csv`
   - Version 11 is marked "Updated April 28, 2017" on the PDF cover (checked in `raw/r44116_11.txt`). The later everycrsreport.com copy (Feb 2021, Q4 FY2020 data) was NOT used for values.
   - Calendar mapping (my derivation): FY quarters are Oct-Dec = Q1, Jan-Mar = Q2, Apr-Jun = Q3, Jul-Sep = Q4. Quarter-end snapshot assumed to be the last month of the FY quarter. Calendar 2009Q1 = FY09 Q2 (Mar 2009), ..., calendar 2016Q3 = FY16 Q4 (Sep 2016). Calendar 2016Q4 has no troop value in the source (Q1 FY2017 not yet available).

2. **CRS RL33110, Amy Belasco, "The Cost of Iraq, Afghanistan, and Other Global War on Terror Operations Since 9/11", March 29, 2011**
   - URL: https://www.everycrsreport.com/files/20110329_RL33110_be1a00c99d668bee3b4ec4f6fc82e914f62c39f0.pdf (574,716 bytes, fetched by curl)
   - Local copy: `raw/dl_3bf284.pdf`, text `raw/dl_3bf284.txt` (copies also at `raw/RL33110_Belasco_2011.*`)
   - Table used: **Table A-1, "Boots on the Ground in Iraq and Afghanistan by Month, September 2001-September 2010"**, Afghanistan row (printed PDF pp. CRS-44 to CRS-45).
   - Source note in the table: "DOD, Joint Staff, Summary and Monthly Boots on the Ground Reports to Congress; for troops in country through August 2009; interpolated for October and November 2008 and August 2009 because not reported." Estimates for Afghanistan Jul-Sep 2010 are flagged "b" in the table: "CRS estimates for the rest of FY2010 reflect DOD plans for average strength of 84,000 in Afghanistan" and "CRS estimates the months from June to September 2010 by distributing the difference between the reported May 2010 level and the September goal of 98,000". Note the table prints Jun 2010 (91,775) without a flag although the note mentions June; analysis keeps the table flags as printed.
   - Flags in output: `a` = CRS interpolated (Oct, Nov 2008), Aug 2009 interpolated per note, `b` = CRS estimate (Jul, Aug, Sep 2010).
   - Output: `troops_monthly_CRS_RL33110_TableA1.csv` (2001-2010 rows; 2001 are zeros in source; analysis uses 2009-01..2010-09 only).
   - Monthly series ends Sep 2010 in this source. No monthly Afghanistan series for Oct 2010-Dec 2016 was obtained (see caveats).

3. **Other copy of RL33110 (September 2, 2010 version)** - downloaded from https://www.policyarchive.org/download/2588 (`raw/dl_53464d.pdf`). Its 2009 and 2010 Afghanistan rows match the March 2011 version used above (checked by text grep), so the 2009-2010 values are not version-dependent. Not used for values.

## Examined, not used for numbers

4. **Brookings Afghanistan Index, 2012-02-29 / 2013-02-28 / 2017-05-25 PDFs**
   - URLs: https://www.brookings.edu/wp-content/uploads/2016/07/index20120229.pdf ; .../index20130228.pdf ; .../21csi_20170525_afghanistan_index.pdf
   - Local copies: `raw/index20120229.pdf`, `raw/index20130228.pdf`, `raw/21csi_20170525_afghanistan_index.pdf`
   - Figure 1.1 "American Troops Deployed to Afghanistan" is a vector chart; only a few data labels are extractable (e.g., 2012 index labels 97,000 / 89,000 / 71,700 / 34,400), and the text notes give snapshot values (e.g., "roughly 89,000" end of Feb 2012; "roughly 66,000" Feb 2013; "roughly 8,400" end Mar 2017). Not a complete series, so not used. Brookings index says figures are snapshot approximations and exclude Operation Enduring Freedom troops in some editions.

5. **CRS R40682 (Belasco, July 2, 2009)** and **CRS R44116 earlier pages** (WebFetch summaries via everycrsreport.com) - used only to identify report numbers. R40682 covers FY2001-FY2012 projections and was not used for values.

6. **Search results pointing to DoD "Boots on the Ground" monthly PDFs** - no primary DoD monthly PDF was located via search; the CRS tables above are the secondary compilation of those reports.

## Blocked / failed

- everycrsreport.com HTML pages and crsreports.congress.gov PDF endpoints returned a Cloudflare "Just a moment..." challenge page (not used; no bypass attempted).
- sgp.fas.org CRS PDFs returned empty responses (not used).
- apps.dtic.mil ADA503796.pdf returned a small HTML page (not used).

## Derived series (not from a source; computed in analysis.py)

- Calendar-quarter troop series = quarter-end snapshot mapping from R44116 (above).
- Rhetoric frames = keyword regex on passage + context text in `output/references.csv` (read-only). Keyword lists are in analysis.py (FRAMES dict).
