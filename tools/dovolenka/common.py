"""Shared helpers for adapters: polite HTTP, normalisation, offer construction."""

import hashlib
import re
import time
import unicodedata
import urllib.robotparser
from urllib.parse import urlsplit

import requests

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36 fkslab-dovolenka-tracker/1.0 (+https://fkslab.com/dovolenka/)"
)

_session = None
_robots = {}


def session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "User-Agent": UA,
            "Accept-Language": "sk-SK,sk;q=0.9,cs;q=0.8,en;q=0.7",
        })
    return _session


class RobotsDisallowed(Exception):
    pass


def allowed(url):
    """robots.txt check, cached per host. Unreachable robots.txt counts as allowed."""
    parts = urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    rp = _robots.get(base)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = session().get(base + "/robots.txt", timeout=15)
            rp.parse(r.text.splitlines() if r.ok else [])
        except requests.RequestException:
            rp.parse([])
        _robots[base] = rp
    return rp.can_fetch(UA, url)


def get(url, *, params=None, headers=None, retries=2, delay=1.5, as_json=False, method="GET", json_body=None):
    """GET/POST with robots check, small retry loop and a pause between calls."""
    if not allowed(url):
        raise RobotsDisallowed(url)
    last = None
    for attempt in range(retries + 1):
        try:
            r = session().request(method, url, params=params, headers=headers, json=json_body, timeout=30)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(delay * (attempt + 2))
                continue
            r.raise_for_status()
            time.sleep(delay)
            return r.json() if as_json else r.text
        except requests.RequestException as e:
            last = e
            if attempt < retries:
                time.sleep(delay * (attempt + 2))
    raise last


# --- normalisation ---------------------------------------------------------

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


_BOARD_PATTERNS = [
    ("UAI", r"ultra\s*all|uai|ultra\s*all\s*inclusive|ultra\s*a\.?i"),
    ("AI", r"all\s*inclusive|\bai\b|all\s*incl|vsetko\s*v\s*cene|all-inclusive"),
    ("FB", r"plna\s*penzia|\bfb\b|full\s*board"),
    ("HB", r"polpenzia|\bhb\b|half\s*board|polopenze"),
    ("BB", r"ranajky|\bbb\b|snidane|breakfast"),
    ("RO", r"bez\s*stravy|\bro\b|room\s*only|\bos\b"),
]


def norm_board(text):
    if not text:
        return None
    t = strip_accents(str(text)).lower()
    for code, pat in _BOARD_PATTERNS:
        if re.search(pat, t):
            return code
    return None


_COUNTRIES = {
    "HR": ["chorvatsko", "croatia", "hrvatska"],
    "TR": ["turecko", "turkey", "turkiye"],
    "CY": ["cyprus", "kypr", "cypr"],
    "IT": ["taliansko", "italie", "italy", "italia", "sicilia", "sardinia", "sardinie", "sicilie"],
    "GR": ["grecko", "recko", "greece"],
    "ES": ["spanielsko", "spanelsko", "spain", "kanarske", "mallorca", "malorka", "tenerife", "gran canaria", "fuerteventura", "lanzarote", "ibiza", "menorca"],
    "MT": ["malta"],
    "PT": ["portugalsko", "portugal", "madeira"],
    "ME": ["cierna hora", "cerna hora", "montenegro"],
    "AL": ["albansko", "albanie", "albania"],
    "BG": ["bulharsko", "bulharsko", "bulgaria"],
    "EG": ["egypt"],
    "TN": ["tunisko", "tunisia"],
    "SI": ["slovinsko", "slovinsko", "slovenia"],
    "FR": ["francuzsko", "francie", "france", "korzika"],
    "MA": ["maroko", "morocco"],
    "AE": ["emiraty", "sae", "dubaj", "dubai"],
}


def norm_country(text):
    """Country code from a free-text country/region name, or None."""
    if not text:
        return None
    t = strip_accents(str(text)).lower()
    if len(t) == 2 and t.upper() in _COUNTRIES:
        return t.upper()
    for code, names in _COUNTRIES.items():
        if any(n in t for n in names):
            return code
    return None


def parse_price(text):
    """'2 780 €' / '2.780,00 EUR' / 2780 -> 2780 (int) or None."""
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return int(round(text))
    t = re.sub(r"[^\d,.]", "", str(text))
    if not t:
        return None
    # thousands separators: dots or commas followed by exactly 3 digits
    t = re.sub(r"[.,](?=\d{3}(\D|$))", "", t)
    t = t.replace(",", ".")
    try:
        return int(round(float(t)))
    except ValueError:
        return None


def offer_id(source, hotel, date_from, nights, transport, departure):
    key = "|".join(str(x or "").lower() for x in (source, hotel, date_from, nights, transport, departure))
    return f"{source}:{hashlib.sha1(key.encode()).hexdigest()[:12]}"


def https_or_none(url):
    return url if isinstance(url, str) and url.startswith("https://") else None
