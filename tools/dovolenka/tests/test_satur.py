from pathlib import Path

from adapters import satur
from config import CONFIG
import run

FX = Path(__file__).parent / "fixtures"


def test_parse_cards_car_dogs():
    cards = satur.parse_cards((FX / "satur_so_psom.html").read_text())
    assert len(cards) == 3
    c = cards[1]
    assert c["hotel"] == "Aminess Vival Velaris Resort"
    assert c["url"] == "https://www.satur.sk/produkt/aminess-vival-velaris-resort"
    assert (c["price_person"], c["price_person_original"], c["price_group"]) == (188, 269, 376)
    assert (c["nights"], c["stars"], c["rating"]) == (4, 4.0, 9.0)
    assert (c["country"], c["region"], c["place"]) == ("Chorvátsko", "Ostrov Brač", "Supetar")
    o = satur.to_offer(c, "car", True, 3)
    assert o["transport"] == "car" and o["pets_allowed"] is True and o["departure"] is None
    assert (o["date_from"], o["date_to"], o["board"]) == ("2026-10-24", "2026-10-28", "HB")
    assert (o["price_total"], o["price_original"]) == (564, 807)


def test_parse_cards_flight():
    cards = satur.parse_cards((FX / "satur_letecky.html").read_text())
    o = satur.to_offer(cards[1], "flight", None, 3)
    assert o["hotel"] == "Hotel Kouros Palace Active Lifestyle" and o["country_code"] == "GR"
    assert (o["transport"], o["departure"], o["board"], o["nights"]) == ("flight", "BTS", "AI", 7)
    assert (o["date_from"], o["price_total"]) == ("2027-09-11", 3459)
    # September is outside the Jul–Aug window, so run.py drops it
    assert run.normalise(o, "satur", "Satur.sk", CONFIG) is None
    jul = dict(o, date_from="2027-07-11", date_to="2027-07-18")
    assert run.normalise(jul, "satur", "Satur.sk", CONFIG)["price_total"] == 3459


def test_year_crossing_dates():
    assert satur._dates("28.12. - 4.1.2027")[0].isoformat() == "2026-12-28"


def test_pets_from_perks():
    cards = satur.parse_cards((FX / "satur_so_psom.html").read_text())
    assert all(c["pets"] for c in cards)
    o = satur.to_offer(cards[0], "car", None, 3)  # e.g. a /vlastna page: perks still say "so psom"
    assert o["pets_allowed"] is True


def test_deeplinks_and_pages():
    assert all(d["url"].startswith("https://www.satur.sk/") for d in satur.deeplinks(CONFIG))
    assert all(p[1] in ("car", "flight") for p in satur.PAGES)
