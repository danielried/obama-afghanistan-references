import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
# Build votes.csv from saved raw official files only (no network).
# House: raw/house_xml/YYYY_RRR.xml (clerk.house.gov roll XML). Senate: raw/senate/vote_menu_C_S.xml (senate.gov menus).
import re, csv, os, html
from datetime import datetime
BASE = str(ANALYSES) + "/12_congress"
RAW = f"{BASE}/raw"
# group: afg = Afghanistan-specific (content verified); supp = war-funding-bearing supplemental (bill-level, content not verified);
#        withdraw_unverified = House McGovern/Jones/Kucinich amendments (author only in XML, content not verified);
#        ndaa_dod = final-passage/conference milestones of NDAA and DoD appropriations (not Afghanistan-specific); oco = Senate OCO limit amendment
# content_status: how the Afghanistan link was established
HOUSE = [
 (2009,265,"supp","bill_level_unverified"),(2009,348,"supp","bill_level_unverified"),
 (2009,453,"withdraw_unverified","author_only"),(2009,454,"withdraw_unverified","author_only"),
 (2009,460,"ndaa_dod","milestone"),(2009,675,"ndaa_dod","milestone"),(2009,770,"ndaa_dod","milestone"),(2009,985,"ndaa_dod","milestone"),
 (2010,98,"afg","xml_title"),(2010,431,"afg","rollcall_article"),(2010,432,"afg","rollcall_article"),(2010,433,"afg","rollcall_article"),
 (2010,312,"withdraw_unverified","author_only"),(2010,336,"ndaa_dod","milestone"),(2010,650,"ndaa_dod","milestone"),
 (2011,47,"withdraw_unverified","author_only"),(2011,130,"withdraw_unverified","author_only"),(2011,147,"ndaa_dod","milestone"),
 (2011,193,"afg","xml_title+npr"),(2011,373,"afg","council_livable_world+the_nation"),(2011,375,"ndaa_dod","milestone"),
 (2011,498,"withdraw_unverified","author_only"),(2011,530,"withdraw_unverified","author_only"),(2011,532,"ndaa_dod","milestone"),(2011,648,"withdraw_unverified","author_only"),
 (2012,291,"ndaa_dod","milestone"),(2012,328,"withdraw_unverified","author_only"),(2012,498,"ndaa_dod","milestone"),(2012,516,"withdraw_unverified","author_only"),
 (2013,62,"ndaa_dod","milestone"),(2013,226,"withdraw_unverified","author_only"),(2013,244,"ndaa_dod","milestone"),(2013,256,"withdraw_unverified","author_only"),
 (2013,401,"withdraw_unverified","author_only"),(2013,414,"ndaa_dod","milestone"),
 (2014,240,"ndaa_dod","milestone"),(2014,338,"ndaa_dod","milestone"),
 (2015,239,"ndaa_dod","milestone"),(2015,358,"ndaa_dod","milestone"),(2015,532,"ndaa_dod","milestone"),
 (2016,216,"ndaa_dod","milestone"),(2016,329,"withdraw_unverified","author_only"),(2016,332,"ndaa_dod","milestone"),
]
SENATE = [  # (congress, session, vote_number, group, content_status)
 (111,1,"202","supp","bill_level_unverified"),(111,1,"210","supp","bill_level_unverified"),
 (111,1,"304","afg","senate_menu_title"),(111,1,"305","afg","senate_menu_title"),
 (111,1,"242","ndaa_dod","milestone"),(111,1,"315","ndaa_dod","milestone"),(111,1,"327","ndaa_dod","milestone"),
 (111,2,"168","afg","senate_menu_title"),(111,2,"176","supp","bill_level_unverified"),(111,2,"219","supp","bill_level_unverified"),
 (112,1,"218","ndaa_dod","milestone"),(112,1,"230","ndaa_dod","milestone"),
 (112,2,"210","afg","senate_menu_title"),(112,2,"221","ndaa_dod","milestone"),
 (113,1,"245","ndaa_dod","milestone"),(113,1,"284","ndaa_dod","milestone"),
 (113,2,"101","ndaa_dod","milestone"),(113,2,"325","ndaa_dod","milestone"),
 (114,1,"205","oco","senate_menu_title"),(114,1,"215","ndaa_dod","milestone"),
 (114,2,"98","ndaa_dod","milestone"),(114,2,"159","ndaa_dod","milestone"),
]
def tag(x, t):
    m = re.search(rf"<{t}>(.*?)</{t}>", x, re.S)
    return html.unescape(re.sub(r"\s+"," ",m.group(1))).strip() if m else ""
rows = []
for y, r, grp, cs in HOUSE:
    f = f"{RAW}/house_xml/{y}_{r:03d}.xml"
    x = open(f, encoding="utf-8", errors="replace").read()
    tv = re.search(r"<totals-by-vote>(.*?)</totals-by-vote>", x, re.S).group(1)
    yea = int(tag(tv,"yea-total")); nay = int(tag(tv,"nay-total"))
    desc = tag(x,"vote-desc") or tag(x,"amendment-author")
    if tag(x,"vote-desc") and "Portion of the Divided" in tag(x,"vote-question"):
        desc = tag(x,"vote-question") + " :: " + desc
    rows.append(dict(chamber="House", date=datetime.strptime(tag(x,"action-date"),"%d-%b-%Y").date().isoformat(),
        congress=tag(x,"congress"), roll=str(r), measure=tag(x,"legis-num"), question=tag(x,"vote-question"),
        result=tag(x,"vote-result"), yea=yea, nay=nay, description=desc, group=grp, content_status=cs,
        url=f"https://clerk.house.gov/evs/{y}/roll{r:03d}.xml", source_file=os.path.relpath(f, BASE)))
for c, s, n, grp, cs in SENATE:
    f = f"{RAW}/senate/vote_menu_{c}_{s}.xml"
    t = open(f, encoding="utf-8", errors="replace").read()
    cy = tag(t, "congress_year")
    hit = None
    for v in re.findall(r"<vote>(.*?)</vote>", t, re.S):
        if tag(v,"vote_number").lstrip("0") == n.lstrip("0"):
            hit = v; break
    assert hit is not None, (c,s,n)
    rows.append(dict(chamber="Senate", date=datetime.strptime(tag(hit,"vote_date")+"-"+cy,"%d-%b-%Y").date().isoformat(),
        congress=str(c), roll=n, measure=tag(hit,"issue"), question=tag(hit,"question"), result=tag(hit,"result"),
        yea=int(tag(hit,"yeas")), nay=int(tag(hit,"nays")), description=tag(hit,"title"), group=grp, content_status=cs,
        url=f"https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{c}_{s}.xml#vote{n}",
        source_file=os.path.relpath(f, BASE)))
rows.sort(key=lambda r: (r["date"], r["chamber"]))
cols = ["chamber","congress","date","roll","measure","question","result","yea","nay","description","group","content_status","url","source_file"]
with open(f"{BASE}/votes.csv","w",newline="",encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow({k:r[k] for k in cols})
print(len(rows), "votes written")
