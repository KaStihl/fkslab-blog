"""Temporary: diagnostics for parser work (runs on push only, removed at the end)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get, session  # noqa: E402

try:
    print("INVIA robots", get("https://www.invia.sk/robots.txt")[:3000])
except Exception as e:
    print("INVIA robots", type(e).__name__, e)

# satur: which query parameter carries the stay length, and does pagination work?
for length in ["7", "7-14", "8-15"]:
    r = session().post("https://www.satur.sk/dovolenka", data={
        "category": "408", "homepage_category": "1", "length": length, "tolerance": "0", "seasonEvent": "",
        "date": "01.07.2027 - 31.08.2027", "passengers": "1-10-12", "numberOfRooms": "1"},
        timeout=30, allow_redirects=False)
    print("SATUR POST length", length, r.status_code, r.headers.get("location"))
for q in ["termin=01.07.2027-31.08.2027&stranka=2", "termin=01.07.2027-31.08.2027&strana=2",
          "termin=01.07.2027-31.08.2027&page=2"]:
    try:
        print(q, len(get("https://www.satur.sk/first-minute/letecky/z-bratislavy?" + q)))
    except Exception as e:
        print(q, type(e).__name__, e)
