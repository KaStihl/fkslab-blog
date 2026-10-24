from pathlib import Path

import run
from adapters import invia
from config import CONFIG

FX = Path(__file__).parent / "fixtures"


def test_parse_landing_cards():
    cards = invia.parse_cards((FX / "invia_landing.html").read_text())
    assert [c["hotel"] for c in cards] == ["Orfeus Park", "Horus Paradise Luxury Resort"]
    c = cards[1]
    assert (c["departure"], c["date_from"], c["date_to"]) == ("VIE", "2027-04-15", "2027-04-21")
    assert (c["price_person"], c["price_room"], c["adults"], c["children"]) == (572, 1144, 2, 0)
    assert (c["stars"], c["rating"], c["country"], c["region"]) == (5.0, 8.4, "Turecko", "Side")
    assert c["hotel_url"] == "https://www.invia.sk/hotel/turecko/side/horus-paradise-luxury-resort/"


def test_to_offer_per_person_approximation():
    c = invia.parse_cards((FX / "invia_landing.html").read_text())[0]
    o = invia.to_offer(c, 3)
    assert (o["board"], o["transport"], o["departure"], o["nights"]) == ("AI", "flight", "BTS", 6)
    assert o["price_total"] == 341 * 3 and "orientačne" in o["discount_label"]
    assert o["url"].startswith("https://www.invia.sk/hotel/turecko/side/orfeus-park/zajazd/")
    # April term + 6 nights: outside the Jul–Aug / 7–14 nights window
    assert run.normalise(o, "invia", "Invia.sk", CONFIG) is None
    summer = dict(o, date_from="2027-07-01", date_to="2027-07-08", nights=7)
    assert run.normalise(summer, "invia", "Invia.sk", CONFIG)["country_code"] == "TR"


def test_exact_party_uses_room_price():
    c = dict(invia.parse_cards((FX / "invia_landing.html").read_text())[0], adults=1, children=2)
    assert invia.to_offer(c, 3)["price_total"] == 682 and invia.to_offer(c, 3)["discount_label"] is None


def test_deeplinks():
    links = invia.deeplinks(CONFIG)
    assert {d["transport"] for d in links} == {"flight", "car"}
    assert all(d["url"].startswith("https://www.invia.sk/") for d in links)
    assert "nl_transportation_id%5B%5D=3_6" in links[1]["url"] and "d_start_from=01.07.2027" in links[1]["url"]
