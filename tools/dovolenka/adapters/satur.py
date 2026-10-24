"""Satur.sk – Slovak tour operator. The car + dogs track (so-psom / vlastna facets) plus flights from BTS."""

import json
import re

from bs4 import BeautifulSoup

from common import get, norm_board, norm_country, parse_price

NAME = "Satur.sk"
HOME = "https://www.satur.sk"

# (path, transport, pets_allowed)
PAGES = [
    ("/dovolenka/chorvatsko/so-psom", "car", True),
    ("/dovolenka/taliansko/so-psom", "car", True),
    ("/dovolenka/so-psom", "car", True),
    ("/first-minute/vlastna", "car", None),
    ("/dovolenka/vlastna", "car", None),
    ("/first-minute/letecky/z-bratislavy", "flight", None),
    ("/first-minute/letecky/z-bratislavy/all-inclusive", "flight", None),
    ("/dovolenka/turecko/letecky/z-bratislavy/all-inclusive", "flight", None),
]


def deeplinks(cfg):
    n = f"{cfg['nights_min']}–{cfg['nights_max']} nocí"
    return [
        {"transport": "car", "label": "Chorvátsko so psom, vlastná doprava", "url": HOME + "/dovolenka/chorvatsko/so-psom"},
        {"transport": "car", "label": "Dovolenka so psom (všetky krajiny)", "url": HOME + "/dovolenka/so-psom"},
        {"transport": "car", "label": "First minute, vlastná doprava", "url": HOME + "/first-minute/vlastna"},
        {"transport": "flight", "label": f"First minute letecky z Bratislavy, AI, {n}",
         "url": HOME + "/first-minute/letecky/z-bratislavy/all-inclusive"},
        {"transport": "flight", "label": "Turecko letecky z Bratislavy, AI",
         "url": HOME + "/dovolenka/turecko/letecky/z-bratislavy/all-inclusive"},
    ]


def diagnose(html):
    """One-line summary of what a listing page contains (helps when the markup changes)."""
    soup = BeautifulSoup(html, "lxml")
    ld = soup.find_all("script", type="application/ld+json")
    nxt = soup.find("script", id="__NEXT_DATA__")
    euros = len(re.findall(r"\d\s*€", html))
    links = {a["href"] for a in soup.find_all("a", href=True) if a["href"].count("/") >= 4}
    return (f"title={soup.title.get_text(strip=True)[:80] if soup.title else None!r} ld+json={len(ld)} "
            f"next_data={bool(nxt)} euro_prices={euros} deep_links={len(links)} sample={sorted(links)[:4]}")


def parse_listing(html, transport, pets):
    """Placeholder until the real markup is known: JSON-LD offers only."""
    out = []
    soup = BeautifulSoup(html, "lxml")
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            ld = json.loads(s.string or "")
        except ValueError:
            continue
        for item in ld if isinstance(ld, list) else [ld]:
            if isinstance(item, dict) and item.get("@type") in ("Product", "Hotel", "TouristTrip"):
                print(f"[satur] ld item {json.dumps(item, ensure_ascii=False)[:300]}")
    return out


def search(cfg):
    offers = []
    for path, transport, pets in PAGES:
        try:
            html = get(HOME + path)
        except Exception as e:
            print(f"[satur] {path}: {type(e).__name__} {str(e)[:120]}")
            continue
        got = parse_listing(html, transport, pets)
        print(f"[satur] {path}: {len(html)} B, {len(got)} offers; {diagnose(html)}")
        offers += got
    return offers


_ = (norm_board, norm_country, parse_price)  # used once the card parser exists
