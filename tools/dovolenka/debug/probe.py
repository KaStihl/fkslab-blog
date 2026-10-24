"""Temporary: dump home/search pages of link-only sites to learn their parameter ids."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get  # noqa: E402

for u in ["https://www.invia.sk/dovolenka/", "https://www.invia.sk/dovolenka/vlastna-doprava/",
          "https://www.kartago.sk/", "https://www.kartago.sk/turecko", "https://www.fischer.sk/",
          "https://www.eximtours.sk/", "https://exotika.tiptravel.sk/turecko", "https://www.satur.sk/"]:
    try:
        print(u, len(get(u)))
    except Exception as e:
        print(u, type(e).__name__, str(e)[:150])
