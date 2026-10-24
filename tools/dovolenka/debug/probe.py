"""Temporary: diagnostics for parser work (runs on push only, removed at the end)."""
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import UA, dump, get, session  # noqa: E402

# 1) why does invia.sk answer 403? (robots.txt only: same block for every UA = IP-level WAF)
for host in ["https://www.invia.sk", "https://www.invia.cz"]:
    for ua in [UA, "python-requests/2.32"]:
        try:
            r = requests.get(host + "/robots.txt", headers={"User-Agent": ua}, timeout=20)
            print("ROBOTS", host, ua[:50], r.status_code, r.headers.get("server"), r.headers.get("x-cache"), len(r.text))
        except Exception as e:
            print("ROBOTS", host, ua[:50], type(e).__name__, e)

# 2) satur: product pages and the searchbox form submit (where does it redirect?)
for u in ["https://www.satur.sk/produkt/zaton-holiday-resort",
          "https://www.satur.sk/produkt/zaton-holiday-resort?termin=01.07.2027-31.08.2027&doprava=vlastna",
          "https://www.satur.sk/produkt/kouros-palace--328482?termin=01.07.2027-31.08.2027&doprava=letecky&odlet=BTS"]:
    try:
        print(u, len(get(u)))
    except Exception as e:
        print(u, type(e).__name__, str(e)[:150])
for date_val, pax in [("01.07.2027 - 31.08.2027", "3"), ("01.07.2027 - 31.08.2027", "1,10,12")]:
    try:
        r = session().post("https://www.satur.sk/dovolenka", data={
            "category": "408", "homepage_category": "1", "length": "", "tolerance": "0", "seasonEvent": "",
            "date": date_val, "passengers": pax, "numberOfRooms": "1"}, timeout=30, allow_redirects=False)
        print("SATUR POST", pax, r.status_code, r.headers.get("location"), len(r.text))
        dump("https://www.satur.sk/dovolenka#post", r.status_code, r.text)
        loc = r.headers.get("location")
        if loc:
            print("  follow", len(get(requests.compat.urljoin("https://www.satur.sk/", loc))))
    except Exception as e:
        print("SATUR POST", type(e).__name__, e)
try:
    js = session().get("https://www.satur.sk/build/app.546e2767.js", timeout=30).text
    print("APPJS", len(js))
    for m in list(re.finditer(r"passengers|numberOfRooms|seasonEvent|childAge|childrenAge|\bages\b|termin|odlet|strava|dospel|vek", js))[:50]:
        print("  JS", js[max(0, m.start() - 200):m.end() + 200].replace("\n", " "))
except Exception as e:
    print("APPJS", type(e).__name__, e)
