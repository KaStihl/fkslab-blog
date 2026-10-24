"""TEMPORARY probe (push runs only): robots + TDM/terms check for candidate sites. Removed after tuning."""

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

HOSTS = ["https://www.cedok.sk", "https://www.cedok.cz", "https://www.kartago.sk", "https://www.tiptravel.sk",
         "https://exotika.tiptravel.sk", "https://www.sorea.sk", "https://hechter.sk", "https://www.firotour.sk",
         "https://www.firotour.cz", "https://www.ckkoala.sk"]
TERMS_RE = re.compile(r"podmienk|podmink|obchodn|\bvop\b|terms|pravn|tdm|vyta[zž]|vyt[eě][zž]|dolovan|"
                      r"pou[zž][ií]v[aá]n[ií]-|copyright|autorsk", re.I)
TDM_RE = re.compile(r"vy[tť]a[zž]ovan|vyt[eě][zž]ov|dolovan|data[\s-]*mining|\bTDM\b|2019/790|39c|39d|"
                    r"crawler|scrap|robot(?!s\.txt)|automatizovan|strojov[eéá]\s+[cč][ií]t", re.I)
GUESS = ["/vytazovanie-textov-a-dat/", "/vytezovani-textu-a-dat/", "/.well-known/tdmrep.json"]
CHALLENGE_RE = re.compile(r"captcha|cf-chl|just a moment|challenge-platform|attention required|access denied|"
                          r"incapsula|perimeterx|datadome|px-captcha", re.I)


def fetch(url, dump=False):
    if not common.allowed(url):
        print(f"  ROBOTS-DISALLOWED {url}")
        return None, None
    try:
        r = common.session().get(url, timeout=30)
    except Exception as e:
        print(f"  ERR {url}: {type(e).__name__} {str(e)[:150]}")
        time.sleep(1.5)
        return None, None
    time.sleep(1.5)
    if dump:
        common.dump(r.url, r.status_code, r.text)
    ch = CHALLENGE_RE.findall(r.text[:200_000])
    print(f"  {r.status_code} {len(r.text):>7}B {r.url} {'CHALLENGE:' + str(set(ch))[:80] if ch else ''}")
    return r, BeautifulSoup(r.text, "lxml")


def snippets(soup):
    txt = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    for m in TDM_RE.finditer(txt):
        yield txt[max(0, m.start() - 160): m.end() + 160]


def txt(el):
    return re.sub(r"\s+", " ", el.get_text(" | ", strip=True)) if el else ""


CED = ("https://www.cedok.sk/vysledky-vyhladavania/dovolenky/turecko/?departuresByPlane=BTS%2CVIE"
       "&dateFrom=01.07.2027&dateTo=31.08.2027&order=priceAsc&participants%5B0%5D%5Badults%5D=1")
P = "&participants%5B0%5D%5B"
CED_VARIANTS = [
    P + "children%5D=2",
    P + "children%5D=2" + P + "childrenAges%5D%5B0%5D=10" + P + "childrenAges%5D%5B1%5D=12",
    P + "children%5D=2" + P + "ages%5D%5B0%5D=10" + P + "ages%5D%5B1%5D=12",
    P + "children%5D=2" + P + "childAges%5D%5B0%5D=10" + P + "childAges%5D%5B1%5D=12",
    P + "children%5D=2" + P + "childrenAge%5D%5B0%5D=10" + P + "childrenAge%5D%5B1%5D=12",
    P + "children%5D=2" + P + "birthdates%5D%5B0%5D=15.01.2017" + P + "birthdates%5D%5B1%5D=15.01.2015",
    P + "childrenBirthdate%5D%5B0%5D=15.01.2017" + P + "childrenBirthdate%5D%5B1%5D=15.01.2015",
    "&daysFrom=8&daysTo=15", "&lengthFrom=8&lengthTo=15", "&durationMin=8&durationMax=15", "&duration=8",
]
TIP_VARIANTS = [
    "https://tiptravel.sk/search.json?ProductTypeIDs=401&DateFrom=01.11.2026&DateTo=30.11.2026&Sort=n&Page=1&PageSize=3",
    "https://tiptravel.sk/search.json?ProductTypeIDs=401&DateFrom=01.11.2026&DateTo=30.11.2026&AdultsCount=1&ChildrenAges=11%2C13&Sort=n&Page=1&PageSize=3",
    "https://tiptravel.sk/search.json?ProductTypeIDs=401&DateFrom=01.06.2027&DateTo=30.09.2027&Sort=n&Page=1&PageSize=3",
    "https://seneca.sk/search.json?ProductTypeIDs=401&Sort=n&Page=1&PageSize=3",
]


def cedok_summary(soup):
    nd = soup.find("script", id="__NEXT_DATA__")
    if nd is None:
        print("    no __NEXT_DATA__")
        return
    d = json.loads(nd.string)
    pp = d["props"]["pageProps"]
    rp = pp.get("queryVariables", {}).get("rateParams", {})
    print("    rateParams:", json.dumps({k: v for k, v in rp.items() if k not in ("currency", "language", "supplier")},
                                        ensure_ascii=False)[:600])
    q = [q for q in pp["initialQueryState"]["queries"] if isinstance(q["state"]["data"], dict) and "main" in q["state"]["data"]]
    if q:
        rates = q[0]["state"]["data"]["main"]["rates"]
        print("    ratesCount:", rates.get("ratesCount"), "days:", [r["duration"]["days"] for r in rates["list"]])
        for r in rates["list"][:2]:
            print("    rate:", r["price"], [(x["type"], x["price"]) for x in r["participants"]])


def main():
    for v in CED_VARIANTS:
        r, soup = fetch(CED + v)
        if soup is not None:
            cedok_summary(soup)
    for u in TIP_VARIANTS:
        r, soup = fetch(u)
        if r is not None:
            m = re.search(r"var response = (\{.*?\n\s*\})\s*\n", r.text, re.S)
            print("    body:", (m.group(1) if m else r.text)[:3000])


if __name__ == "__main__":
    main()
