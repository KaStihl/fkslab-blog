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


def main():
    for base in HOSTS:
        print(f"\n===== {base}")
        common.allowed(base + "/")  # dumps robots.txt
        rp = common._robots.get(base)
        print("  robots rules:", [("A" if a else "D") + ":" + p for a, p in (rp.rules if rp else [])][:40])
        r, soup = fetch(base + "/")
        if soup is None:
            continue
        meta = [m.attrs for m in soup.select("meta[name*=tdm], meta[name=robots]")]
        print("  title:", soup.title.get_text(strip=True)[:100] if soup.title else None, "meta:", meta)
        links = {}
        for a in soup.select("a[href]"):
            href = urljoin(r.url, a["href"])
            if urlsplit(href).netloc != urlsplit(r.url).netloc:
                continue
            links.setdefault(href.split("#")[0], re.sub(r"\s+", " ", a.get_text(" ", strip=True))[:50])
        print("  links:", json.dumps(sorted(links.items())[:250], ensure_ascii=False))
        hits = [u for u, t in links.items() if TERMS_RE.search(u) or TERMS_RE.search(t)]
        print("  homepage TDM snippets:", list(snippets(soup))[:5])
        for u in hits[:5] + [base + g for g in GUESS]:
            rr, s2 = fetch(u, dump=True)
            if s2 is not None and rr.ok:
                for sn in list(snippets(s2))[:8]:
                    print("    TDM?", sn)


if __name__ == "__main__":
    main()
