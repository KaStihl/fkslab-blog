"""Temporary: diagnostics for parser work (runs on push only, removed at the end)."""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get  # noqa: E402

for u in ["https://www.invia.sk/vytazovanie-textov-a-dat/"]:
    try:
        soup = BeautifulSoup(get(u), "lxml")
        main = soup.find("main") or soup.body
        print("TDM", u, re.sub(r"\s+", " ", main.get_text(" "))[:4000])
    except Exception as e:
        print("TDM", u, type(e).__name__, e)
