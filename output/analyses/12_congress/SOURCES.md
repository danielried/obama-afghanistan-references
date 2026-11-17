# SOURCES - 12_congress (retrieved 2026-11-16)

All HTTP requests: Python requests / curl with User-Agent "research-script/1.0". No personal data sent. Rate: 1 request per second.

## Primary, fetched by script (raw files under raw/)
| URL pattern | Used for | Method | Retrieved |
|---|---|---|---|
| https://clerk.house.gov/evslegacy/{2009..2016}/index.asp | House roll-call index (candidate discovery) | curl, saved raw/house/index_YYYY.html | 2026-11-16 |
| https://clerk.house.gov/evslegacy/{YYYY}/ROLL_{000..900}.asp | House roll-call range pages, 5,795 rolls parsed (raw/house/ranges/) | curl, parsed by regex on TR/TD | 2026-11-16 |
| https://clerk.house.gov/evs/{YYYY}/roll{NNN}.xml | Per-vote tallies (totals-by-vote), amendment author, vote-desc (raw/house_xml/) | requests GET | 2026-11-16 |
| https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{111..114}_{1,2}.xml | Senate vote menus: yeas, nays, title, question (raw/senate/) | curl | 2026-11-16 |

House per-vote XML fetched for 2009 rolls 265,348,453,454,460,675,770,985; 2010 rolls 98,312,336,420-425,426-433,650; 2011 rolls 47,130,147,193,373,375,498,530,532,648; 2012 rolls 291,328,498,516; 2013 rolls 62,89,226,244,256,401,414; 2014 rolls 240,338,452; 2015 rolls 239,358,370,532; 2016 rolls 216,329,332. Every vote used appears with its clerk URL in votes.csv.

## Outside sources consulted (WebFetch / WebSearch)
| URL | How obtained | Used for |
|---|---|---|
| https://www.rollcall.com/2010/07/01/anti-war-liberals-put-afghanistan-to-three-votes/ | WebFetch (summary model) | Identifies the three Afghanistan votes of 2010-07-01 (McGovern 162-260; Lee 100-321; strip war money 25-376); matched to House rolls 433, 432, 431 (XML tallies agree) |
| https://livableworld.org/house-vote-on-mcgovern-jones-amendment-president-needs-to-change-afghanistan-policy/ | WebSearch result (snippet, not fetched in full) | Corroborates that 2011 roll 373 (McGovern-Jones Amdt 55, H.R.1540) was an Afghanistan withdrawal amendment; tally 204-215 agrees with XML |
| https://www.thenation.com/article/archive/crucial-day-congress-ongoing-war-afghanistan/ | WebSearch result (snippet) | Same as above (2011-05-26 context) |
| https://www.npr.org/sections/itsallpolitics/2011/03/17/134630813/afghanistan-withdrawal-resolution-rejected-by-bipartisan-house | WebSearch result (snippet) | H.Con.Res.28 (2011 roll 193) Afghanistan withdrawal resolution, 321-93 against; agrees with XML |
| https://himes.house.gov/2010/3/himes-statement-vote-against-removing-troops-afghanistan-30-days | WebSearch result (snippet) | H.Con.Res.248 (2010 roll 98) Afghanistan, 356-65 (XML: 65 yea, 356 nay) |
| https://projects.propublica.org/represent/votes/112/house/1/498 | WebSearch result (snippet) | Checked for 2011-07-06 Kucinich amendment (roll 498). Its summary field is internally inconsistent; XML (253-167) was used instead. Not used for numbers. |

## Not reachable
- https://www.congress.gov/ returned HTTP 403 (Cloudflare challenge). Not used.
- Bill text of H.R.2346, H.R.4899, H.R.2219, and the Kucinich / Jones / McGovern amendments was NOT retrieved. Content links for those rows are flagged in votes.csv (content_status). Their Afghanistan link is unverified.
- The Pew, Gallup, CRS, and Brookings series were NOT needed for this key; no outside time series used.

## Local project inputs (read-only)
output/references.csv, speeches_index.csv, reaction_events.csv (read only). No file under joyce-project was modified.
