"""Invia.sk – aggregator of ~100 tour operators.

robots.txt on invia.sk disallows every search filter (nl_*, d_start_from, d_end_to, sort, page=) and the
/direct/tour_hotel/ term-picker JSON (which also answers 403 to non-browser clients), so the exact
"1 adult + 2 kids, Jul–Aug 2027" search cannot be run automatically. What is allowed are the SSR destination
landing pages (and their /2/, /3/ path pagination). Each hotel card there carries one term – the one Invia
picks for 2 adults, usually the nearest/cheapest one – with structured analytics data. We keep the cards whose
term falls into our window (run.py filters); everything else is left to the human deeplinks below.
"""

import json
import re
from datetime import date
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from common import get, norm_board, norm_country, parse_price

NAME = "Invia.sk"
HOME = "https://www.invia.sk"

AIRPORTS = {"BTS": "3_5", "VIE": "3_6"}  # invia.sk nl_transportation_id (for the human deeplinks)
MEALS = ["5", "11"]  # 5 = All Inclusive, 11 = Ultra All Inclusive
MAX_REQUESTS = 60
PAGES_PER_LANDING = 3

# Landing pages per favourite destination (SSR, allowed by robots.txt). Pagination is <path><n>/.
LANDINGS = [
    "/dovolenka/turecko/all-inclusive/", "/dovolenka/first-minute/turecko/",
    "/dovolenka/cyprus/all-inclusive/", "/dovolenka/first-minute/cyprus/",
    "/dovolenka/grecko/kreta/", "/dovolenka/grecko/rodos/", "/dovolenka/grecko/kos/",
    "/dovolenka/grecko/korfu/", "/dovolenka/grecko/zakynthos/", "/dovolenka/first-minute/grecko/",
    "/dovolenka/spanielsko/mallorca/", "/dovolenka/spanielsko/all-inclusive/", "/dovolenka/first-minute/spanielsko/",
    "/dovolenka/taliansko/sicilia/", "/dovolenka/taliansko/sardinia-sardegna/",
    "/dovolenka/chorvatsko/", "/dovolenka/first-minute/chorvatsko/", "/dovolenka/malta/",
]


def _fmt(d):
    return d.strftime("%d.%m.%Y")


def deeplinks(cfg):
    base = {
        "d_start_from": _fmt(cfg["date_from"]), "d_end_to": _fmt(cfg["date_to"]),
        "nl_length_from": cfg["nights_min"] + 1, "nl_length_to": cfg["nights_max"] + 1,  # invia counts days
        "nl_occupancy_adults": cfg["adults"], "nl_occupancy_children": len(cfg["children_ages"]),
        "sort": "c_price", "sort_order": "asc",
    }
    ages = [("nl_ages_children[]", a) for a in cfg["children_ages"]]
    meals = [("nl_meal_id[]", m) for m in MEALS]
    n = f"{cfg['nights_min']}–{cfg['nights_max']} nocí"
    out = []
    for code, label in (("BTS", "z Bratislavy"), ("VIE", "z Viedne")):
        q = urlencode(list(base.items()) + [("nl_transportation_id[]", AIRPORTS[code])] + meals + ages)
        out.append({"transport": "flight", "label": f"Letecky {label}, AI/UAI, júl–aug, {n}, 1+2",
                    "url": f"{HOME}/dovolenka/?{q}"})
    out.append({"transport": "car", "label": "Vlastná doprava (psy overiť v detaile hotela)",
                "url": f"{HOME}/dovolenka/vlastna-doprava/"})
    return out


# --- parsing (pure functions, tested offline) -------------------------------

def _kv(s):
    """'departure:_2027-04-01_return:_2027-04-07' -> {'departure': '2027-04-01', 'return': '2027-04-07'}"""
    return dict(re.findall(r"([a-z]+):_([^_]*)", s or ""))


def parse_cards(html):
    """Raw card data from a landing page, read from each card's analytics JSON (machine-made, stable)."""
    soup = BeautifulSoup(html, "lxml")
    out = []
    for card in soup.find_all("article", class_="b-product-list-2"):
        a = card.select_one("a.b-product-list-2__link[data-ga-click-data-value]")
        if not a:
            continue
        try:
            item = json.loads(a["data-ga-click-data-value"])["ecommerce"]["items"][0]
        except (ValueError, KeyError, IndexError):
            continue
        price = _kv(item.get("item_parameter_1"))
        dates = _kv(item.get("item_parameter_7"))
        quality = _kv(item.get("item_parameter_4"))
        pax = _kv(item.get("item_parameter_9"))
        board = re.search(r"board:_(.+)$", item.get("item_parameter_8_local") or "")
        hotel_link = card.select_one('a[href^="https://www.invia.sk/hotel/"]:not([href*="zajazd"])')
        img = card.find("img", src=re.compile(r"^https://"))
        out.append({
            "hotel": item.get("item_name"), "hotel_url": hotel_link["href"] if hotel_link else None,
            "offer_url": a.get("href"), "country": item.get("item_category_local"),
            "region": item.get("item_category2_local"), "place": item.get("item_category3_local"),
            "departure": item.get("item_parameter_3") or None, "date_from": dates.get("departure"),
            "date_to": dates.get("return"), "board": board[1] if board else None,
            "stars": float(quality["s"]) if quality.get("s") else None,
            "rating": round(float(quality["r"]) * 2, 1) if quality.get("r") else None,  # 0–5 -> 0–10
            "price_person": parse_price(price.get("per")), "price_room": parse_price(price.get("room")),
            "adults": int(pax.get("adult") or 0), "children": int(pax.get("child") or 0),
            "operator": item.get("item_brand"), "image": img["src"] if img else None,
        })
    return out


def to_offer(c, party):
    """Card -> offer. Cards are priced for Invia's default party (2 adults); like Satur we approximate the
    1 adult + 2 kids price as per-person x 3 – child discounts are only known after a real search."""
    if not (c["date_from"] and c["date_to"] and c["price_person"] and c["hotel"]):
        return None
    d1, d2 = date.fromisoformat(c["date_from"]), date.fromisoformat(c["date_to"])
    exact = c["adults"] == 1 and c["children"] == party - 1
    url = c["offer_url"] if (c["offer_url"] or "").startswith("https://") else c["hotel_url"]
    return {
        "hotel": c["hotel"], "url": url, "image": c["image"], "stars": c["stars"], "rating": c["rating"],
        "country": c["country"], "country_code": norm_country(c["country"]), "region": c["region"],
        "place": c["place"], "board": norm_board(c["board"]), "transport": "flight" if c["departure"] else "car",
        "departure": c["departure"], "date_from": d1.isoformat(), "date_to": d2.isoformat(),
        "nights": (d2 - d1).days,
        "price_total": c["price_room"] if exact else c["price_person"] * party,
        "discount_label": None if exact else "Cena za os. × 3 (orientačne)",
    }


def search(cfg):
    party = cfg["adults"] + len(cfg["children_ages"])
    left, offers, seen, months = MAX_REQUESTS, [], set(), {}
    for path in LANDINGS:
        for n in range(1, PAGES_PER_LANDING + 1):
            if left <= 0:
                break
            left -= 1
            url = HOME + path + (f"{n}/" if n > 1 else "")
            try:
                cards = parse_cards(get(url))
            except Exception as e:
                print(f"[invia] {url}: {type(e).__name__} {str(e)[:120]}")
                if "403" in str(e) and not offers and left >= MAX_REQUESTS - 3:
                    raise RuntimeError("invia.sk answers 403 (CloudFront 'Request blocked') to this runner") from e
                break
            for c in cards:
                m = (c["date_from"] or "?")[:7]
                months[m] = months.get(m, 0) + 1
            fresh = [o for o in (to_offer(c, party) for c in cards)
                     if o and (o["hotel"], o["date_from"], o["departure"]) not in seen]
            seen.update((o["hotel"], o["date_from"], o["departure"]) for o in fresh)
            offers += fresh
            print(f"[invia] {url}: {len(cards)} cards, first={cards[:1]}")
            if len(cards) < 10:
                break
    lo, hi = cfg["date_from"].isoformat(), cfg["date_to"].isoformat()
    window = sum(lo <= o["date_from"] <= hi for o in offers)
    print(f"[invia] {len(offers)} cards with terms, {window} in the date window; term months: "
          f"{dict(sorted(months.items()))}")
    return offers
