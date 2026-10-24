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
       "&dateFrom=01.07.2027&dateTo=31.08.2027&order=priceAsc")
CED_VARIANTS = [
    "", "&participants%5B0%5D%5Badults%5D=1&participants%5B0%5D%5BchildAges%5D%5B%5D=10&participants%5B0%5D%5BchildAges%5D%5B%5D=12",
    "&participants%5B0%5D%5Badults%5D=1&participants%5B0%5D%5Bchildren%5D%5B0%5D=10&participants%5B0%5D%5Bchildren%5D%5B1%5D=12",
    "&participants%5B0%5D%5Badults%5D=1&participants%5B0%5D%5BchildrenAges%5D%5B0%5D=10&participants%5B0%5D%5BchildrenAges%5D%5B1%5D=12",
    "&participants%5B0%5D%5Badults%5D=1&participants%5B0%5D%5Bchildren%5D=10%2C12",
    "&nights=7-14", "&duration=8-15", "&lengthOfStay=7-14", "&tripLength=8%2C9%2C10%2C11%2C12%2C13%2C14%2C15",
]
KAR = "https://www.kartago.sk/turecko"
KAR_VARIANTS = ["", "?TO=483%7C3789&DD=2027-07-01&RD=2027-08-31&MNN=7%7C8%7C9%7C10%7C11%7C12%7C13%7C14&NNM=7%7C8%7C9%7C10%7C11%7C12%7C13%7C14&AC1=1&KC1=2&KA1=10%7C12&TT=1",
                "?to=483%7C3789&dd=2027-07-01&rd=2027-08-31&nn=7%7C8%7C9%7C10%7C11%7C12%7C13%7C14&ac1=1&kc1=2&ka1=10%7C12&tt=1"]
TIP_Q = "&ProductTypeIDs=401&DateFrom=01.07.2027&DateTo=31.08.2027&TransportationTypeID=201&AirportID=2&Sort=n&Page=1&PageSize=15"
TIP_VARIANTS = ["https://tiptravel.sk/search.json?DestinationID=62&AdultsCount=1&ChildrenAges=11%2C13" + TIP_Q,
                "https://tiptravel.sk/search.json?DestinationID=62&AdultsCount=1&ChildrenAges=10%2C12" + TIP_Q,
                "https://tiptravel.sk/search.json?AdultsCount=2" + TIP_Q,
                "https://tiptravel.sk/search.json?DestinationID=62&AdultsCount=1&ChildrenAges=11%2C13&callback=cb" + TIP_Q,
                "https://seneca.sk/search.json?DestinationID=72&AdultsCount=1&ChildrenAges=11%2C13" + TIP_Q]


def cedok_summary(soup):
    who = soup.select_one("[data-testid=participants-filter-input]")
    cards = soup.select("[data-testid=offer-list-item]")
    days = re.findall(r"\((\d+) dní\)", " ".join(txt(c) for c in cards))
    print("    who:", txt(who), "cards:", len(cards), "days:", days[:40])
    for c in cards[:3]:
        print("    card:", txt(c)[:300])


def main():
    for v in CED_VARIANTS:
        r, soup = fetch(CED + v)
        if soup is not None:
            cedok_summary(soup)
            if not v:
                (common.DUMP_DIR / "cedok_full.html").write_text(r.text, encoding="utf-8")
    for v in KAR_VARIANTS:
        r, soup = fetch(KAR + v)
        if soup is None:
            continue
        arts = soup.select("article")
        hrefs = [a["href"] for a in soup.select("article h3 a[href]")]
        q = lambda k: sorted({m for h in hrefs for m in re.findall(rf"[?&]{k}=([^&]*)", h)})[:15]
        print("    articles:", len(arts), "TO:", q("TO"), "DD:", q("DD"), "NN:", q("NN"), "AC1:", q("AC1"), "KC1:", q("KC1"))
        for a in arts[:3]:
            print("    art:", txt(a)[:300])
        if v and hrefs:
            fetch(urljoin(KAR, hrefs[0]), dump=True)
    for u in TIP_VARIANTS:
        r, soup = fetch(u)
        if r is not None:
            print("    body:", r.text[:2500])
    r, soup = fetch("https://koala.sk/")
    if r is not None:
        print("    koala:", r.text[:3000])


if __name__ == "__main__":
    main()
