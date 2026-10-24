"""Exim Tours – dates and prices are rendered by JavaScript, so only search links for a human."""

from urllib.parse import urlencode

NAME = "Exim Tours"
HOME = "https://www.eximtours.sk"
DEEPLINK_ONLY = True


def deeplinks(cfg):
    nights = "|".join(str(n) for n in range(cfg["nights_min"], cfg["nights_max"] + 1))
    q = {"tt": 1, "dd": cfg["date_from"].isoformat(), "rd": cfg["date_to"].isoformat(), "nn": nights,
         "ac1": cfg["adults"], "kc1": len(cfg["children_ages"]), "m": 5}
    return [{"transport": "flight",
             "label": f"Letecky, AI, júl–aug, {cfg['nights_min']}–{cfg['nights_max']} nocí (odlet vybrať na stránke)",
             "url": f"{HOME}/vysledky-vyhledavani?{urlencode(q)}"}]


def search(cfg):
    return []
