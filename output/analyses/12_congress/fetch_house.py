import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "output" / "references.csv").is_file())
ANALYSES = PROJECT / "output" / "analyses"
# Fetch House clerk roll-call XML for shortlisted rolls. Run: python -I fetch_house.py
import os, time, requests
BASE = str(ANALYSES) + "/12_congress/raw/house_xml"
UA = {"User-Agent": "research-script/1.0"}
ROLLS = {
 2009: [265,348,453,454,460,675,770,985],
 2010: [98,186,336,426,427,428,429,430,650],
 2011: [47,130,146,147,193,373,375,411,412,530,532,648],
 2012: [290,291,328,498,516],
 2013: [62,89,226,244,256,401,414],
 2014: [240,338,452],
 2015: [239,358,370,532],
 2016: [216,329,332],
}
os.makedirs(BASE, exist_ok=True)
for y, rolls in ROLLS.items():
    for r in rolls:
        out = os.path.join(BASE, f"{y}_{r:03d}.xml")
        if os.path.exists(out) and os.path.getsize(out) > 200:
            continue
        url = f"https://clerk.house.gov/evs/{y}/roll{r:03d}.xml"
        resp = requests.get(url, headers=UA, timeout=60)
        with open(out, "wb") as f:
            f.write(resp.content)
        print(y, r, resp.status_code, len(resp.content), flush=True)
        time.sleep(1)
