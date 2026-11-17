# Sources (retrieved 2026-11-16, generic UA via WebFetch/WebSearch tools; no personal info sent)

| # | URL | Used for | How obtained |
|---|---|---|---|
| S1 | https://news.gallup.com/file/poll/352841/210727Afghanistan.pdf | Gallup "mistake" trend table (2008-2021), Q25 and comparison series, wording | WebFetch returned binary; saved PDF text extracted with `pdftotext -layout` (local tool-results copy). Values read directly from extracted text. PRIMARY, highest confidence |
| S2 | https://news.gallup.com/poll/122816/americans-say-afghanistan-going-badly-not-mistake.aspx | Aug 31-Sep 2 2009 = 37/61 cross-check | WebFetch summary of page |
| S3 | https://news.gallup.com/poll/144965/obama-gets-lowest-marks-deficit-highest-foreign-affairs.aspx | Obama handling Afghanistan approval: Nov 2009 35, Jul-Aug 2010 36 (article: "last November" = 35) | WebFetch summary of page |
| S4 | https://news.gallup.com/poll/144944/americans-less-pessimistic-progress-afghanistan.aspx | Nov 19-21 2010: approve 44, disapprove 49; Feb 2010 48; mistake 58 not-mistake | WebFetch summary of page |
| S5 | https://news.gallup.com/poll/141716/New-High-Call-Afghanistan-War-Mistake.aspx | Jul 27-Aug 1 2010 mistake 43 (cross-check with S1) | WebFetch summary of page |
| S6 | https://www.pewresearch.org/politics/2014/01/30/more-now-see-failure-than-success-in-iraq-afghanistan/ | Right-decision series Jan 2006 69, Jan 2009 64, Nov 2011 56, Jan 2014 51 (fieldwork Jan 15-19 2014, n=1,504) | WebFetch summary of page; question wording NOT verified (page does not quote it in extraction) |
| S7 | https://www.pewresearch.org/politics/2011/06/21/record-number-favors-removing-u-s-troops-from-afghanistan/ | June 2011 right 57 / wrong 35 | WebFetch summary of page; exact fieldwork dates not extracted |

## Not obtained
- Pew right-decision readings for 2012, 2015, 2016: not found in fetched pages.
- Gallup mistake readings for 2012, 2016: not in S1 table.
- Obama approval on Afghanistan 2011-2016 from pollsters in the same series: search results mentioned ABC/WaPo, AP-GfK, Quinnipiac, Pew values but PDFs were not readable (binary/compressed) and were not used. Not in analysis.
- ABC/WaPo PDFs (abcnews 1095a3, langer 1119a6) not readable; not used.
- Pew Foreign Policy 2015-05-28 PDF (search result) not fetched.

## Caveats
- Values in S2-S7 come from WebFetch small-model summaries of HTML pages, not byte-level reads. S1 is the only value set read directly from source text.
- Question wording changed: "military forces" (2008-2011 comparison block) vs "sending troops to fight" (2013-2021 block). Gallup printed both on same topline, so 2013-2015 are from a different item block.
