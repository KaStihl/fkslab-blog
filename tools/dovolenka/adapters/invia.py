"""Invia.sk – aggregator of ~100 tour operators. Main source.

Pipeline (robots.txt-friendly: filtered search URLs are disallowed, landing/hotel pages and /direct/ are not):
  1. a few SSR landing pages per favourite destination -> hotel URLs
  2. hotel page -> nl_hotel_id (+ name, stars, rating)
  3. /direct/ term-picker JSON with our exact party, dates, airports and boards -> priced terms
"""

import json
import re
from datetime import date, datetime
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from common import get, norm_board, norm_country, parse_price

NAME = "Invia.sk"
HOME = "https://www.invia.sk"

AIRPORTS = {"BTS": "3_5", "VIE": "3_6"}  # invia.sk nl_transportation_id
MEALS = ["5", "11"]  # 5 = All Inclusive, 11 = Ultra All Inclusive
MAX_REQUESTS = 150
MAX_HOTELS = 45
TERMS_PER_HOTEL = 3

# Landing pages per favourite destination (SSR, not robots-disallowed). Missing ones just 404.
LANDINGS = {
    "TR": ["/dovolenka/turecko/all-inclusive/", "/dovolenka/turecko/letecky-z-bratislavy/"],
    "CY": ["/dovolenka/cyprus/", "/dovolenka/cyprus/all-inclusive/"],
    "GR": ["/dovolenka/grecko/kreta/all-inclusive/", "/dovolenka/grecko/rodos/all-inclusive/",
           "/dovolenka/grecko/kos/", "/dovolenka/grecko/korfu/", "/dovolenka/grecko/zakynthos/"],
    "ES": ["/dovolenka/spanielsko/mallorca/", "/dovolenka/spanielsko/kanarske-ostrovy/",
           "/dovolenka/spanielsko/all-inclusive/"],
    "IT": ["/dovolenka/taliansko/sicilia/", "/dovolenka/taliansko/sardinia/"],
    "HR": ["/dovolenka/chorvatsko/letecky-z-bratislavy/", "/dovolenka/chorvatsko/"],
    "MT": ["/dovolenka/malta/"],
}

HOTEL_RE = re.compile(r"(?:https://www\.invia\.sk)?(/hotel/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9-]+/)")
HOTEL_ID_RE = re.compile(r"nl_hotel_id[/=\"':\s]+(\d{3,})")
TERMS_URL = HOME + "/direct/tour_hotel/ajax-term-picker-data/?selectedTab=tours&useFilterForm=true"


class Budget:
    def __init__(self, n):
        self.left = n

    def take(self):
        self.left -= 1
        return self.left >= 0


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

def parse_landing(html):
    """Hotel paths linked from a landing page, in page order."""
    seen = []
    for m in HOTEL_RE.finditer(html):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def parse_hotel(html, path):
    """Hotel meta from its detail page."""
    m = HOTEL_ID_RE.search(html)
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    name = h1.get_text(" ", strip=True) if h1 else path.strip("/").split("/")[-1].replace("-", " ").title()
    country_slug, place_slug = path.strip("/").split("/")[1:3]
    meta = {"hotel_id": int(m.group(1)) if m else None, "hotel": name, "url": HOME + path,
            "country": norm_country(country_slug.replace("-", " ")) or country_slug,
            "place": place_slug.replace("-", " ").title(), "stars": None, "rating": None, "image": None}
    og = soup.find("meta", property="og:image")
    if og and og.get("content", "").startswith("https://"):
        meta["image"] = og["content"]
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            ld = json.loads(s.string or "")
        except ValueError:
            continue
        for item in ld if isinstance(ld, list) else [ld]:
            if not isinstance(item, dict):
                continue
            stars = (item.get("starRating") or {}).get("ratingValue") if isinstance(item.get("starRating"), dict) else None
            if stars:
                meta["stars"] = float(stars)
            agg = item.get("aggregateRating")
            if isinstance(agg, dict) and agg.get("ratingValue"):
                best = float(agg.get("bestRating") or 10)
                meta["rating"] = round(float(agg["ratingValue"]) * 10 / best, 1)
            if item.get("name") and item.get("@type") in ("Hotel", "LodgingBusiness", "Resort"):
                meta["hotel"] = item["name"]
    return meta


def _date(v):
    if not v:
        return None
    s = str(v).strip()
    for fmt, n in (("%Y-%m-%d", 10), ("%d.%m.%Y", 10), ("%Y%m%d", 8)):
        try:
            return datetime.strptime(s[:n], fmt).date()
        except ValueError:
            pass
    m = re.search(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})", s)
    return date(int(m[3]), int(m[2]), int(m[1])) if m else None


def parse_terms(data, meta, departure):
    """Offers from a term-picker JSON response."""
    rows = data.get("data") if isinstance(data, dict) else None
    if isinstance(rows, dict):
        rows = rows.get("terms") or rows.get("items") or list(rows.values())
    out = []
    for t in rows or []:
        if not isinstance(t, dict):
            continue
        od = (t.get("favouriteData") or {}).get("offerData") or {}
        d1 = _date(t.get("outboundDate") or od.get("dateStart"))
        d2 = _date(t.get("returnDate") or od.get("dateEnd"))
        price = parse_price(t.get("priceGroup") or t.get("priceTotal"))
        if not (d1 and d2 and price):
            continue
        orig = parse_price(t.get("priceGroupOriginal") or t.get("originalPriceGroup"))
        out.append(dict(meta, board=norm_board(t.get("meal")) or t.get("meal"), transport="flight",
                        departure=departure, date_from=d1.isoformat(), date_to=d2.isoformat(),
                        nights=(d2 - d1).days, price_total=price, price_original=orig,
                        discount_label=t.get("promotionName") or None))
    return sorted(out, key=lambda o: o["price_total"])


# --- network ------------------------------------------------------------------

def _terms(cfg, meta, airport):
    body = {
        "filter": {
            "nl_transportation_id": [AIRPORTS[airport]],
            "nl_length_from": cfg["nights_min"] + 1, "nl_length_to": cfg["nights_max"] + 1,
            "nl_meal_id": MEALS,
            "nl_occupancy_adults": cfg["adults"], "nl_occupancy_children": len(cfg["children_ages"]),
            "nl_ages_children": cfg["children_ages"],
            "d_start_from": _fmt(cfg["date_from"]), "d_end_to": _fmt(cfg["date_to"]),
            "page": 1, "nl_tourop_id": [], "domestic_tour_operator": "foreign", "offsets": "",
            "duration": "Custom range", "nl_promotion_category_id": "", "nl_hotel_id": meta["hotel_id"],
        },
        "sorter": {"sort_ascent_by": "price"},
    }
    headers = {"Content-Type": "text/plain;charset=UTF-8", "Origin": HOME, "Referer": meta["url"],
               "X-Requested-With": "XMLHttpRequest", "Accept": "application/json, text/plain, */*"}
    return get(TERMS_URL, method="POST", data=json.dumps(body), headers=headers, as_json=True)


def search(cfg):
    budget = Budget(MAX_REQUESTS)
    per_dest, blocked = {}, 0
    for cc, paths in LANDINGS.items():
        hotels = per_dest.setdefault(cc, [])
        for p in paths:
            if not budget.take():
                break
            try:
                html = get(HOME + p)
            except Exception as e:
                print(f"[invia] landing {p}: {type(e).__name__} {str(e)[:120]}")
                blocked += "403" in str(e)
                if blocked >= 3 and not any(per_dest.values()):
                    raise RuntimeError("invia.sk answers 403 (CloudFront 'Request blocked') to this runner") from e
                continue
            found = parse_landing(html)
            print(f"[invia] landing {p}: {len(html)} B, {len(found)} hotels, "
                  f"zajazd-links={html.count('/zajazd/')}, first={found[:2]}")
            hotels += [h for h in found if h not in hotels]
    # round-robin across destinations so every favourite gets some hotels
    order, i = [], 0
    while len(order) < MAX_HOTELS and any(i < len(v) for v in per_dest.values()):
        order += [v[i] for v in per_dest.values() if i < len(v) and v[i] not in order]
        i += 1
    order = order[:MAX_HOTELS]
    print(f"[invia] {sum(map(len, per_dest.values()))} hotels found, checking {len(order)}")

    offers, priced, seen_any = [], 0, False
    for path in order:
        if budget.left < 1 + len(AIRPORTS):
            print("[invia] request budget exhausted")
            break
        budget.take()
        try:
            meta = parse_hotel(get(HOME + path), path)
        except Exception as e:
            print(f"[invia] hotel {path}: {type(e).__name__} {str(e)[:120]}")
            continue
        if not meta["hotel_id"]:
            print(f"[invia] hotel {path}: no nl_hotel_id")
            continue
        hotel_offers = []
        for airport in AIRPORTS:
            budget.take()
            try:
                data = _terms(cfg, meta, airport)
            except Exception as e:
                print(f"[invia] terms {meta['hotel_id']} {airport}: {type(e).__name__} {str(e)[:120]}")
                continue
            got = parse_terms(data, meta, airport)
            if not seen_any:
                keys = list(data)[:12] if isinstance(data, dict) else type(data).__name__
                print(f"[invia] first term response keys={keys} parsed={len(got)} first={got[:1]}")
                seen_any = True
            hotel_offers += got
        hotel_offers.sort(key=lambda o: o["price_total"])
        priced += bool(hotel_offers)
        offers += hotel_offers[:TERMS_PER_HOTEL]
    print(f"[invia] {priced} hotels with 2027 terms, {len(offers)} offers, {budget.left} requests left")
    if order and not priced:
        print("[invia] no priced terms for Jul–Aug 2027 – season possibly not bookable yet")
    return offers
