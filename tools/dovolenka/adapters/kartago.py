"""Kartago Tours – results load via XHR, so only search links for a human."""

from urllib.parse import urlencode

NAME = "Kartago Tours"
HOME = "https://www.kartago.sk"
DEEPLINK_ONLY = True

AIRPORTS = {"VIE": ("3789", "z Viedne")}  # TO= airport id; the BTS id is not known yet


def deeplinks(cfg):
    out = []
    for code, (to, label) in AIRPORTS.items():
        q = {"DS": 0, "TT": 1, "TO": to, "DD": cfg["date_from"].isoformat(), "RD": cfg["date_to"].isoformat(),
             "NN": cfg["nights_min"], "MNN": cfg["nights_min"], "NNM": cfg["nights_max"], "MT": 5,
             "AC1": cfg["adults"], "KC1": len(cfg["children_ages"]), "IC1": 0, "PF": 0, "PT": cfg["price_cap"]}
        out.append({"transport": "flight",
                    "label": f"Letecky {label}, AI, júl–aug, {cfg['nights_min']}–{cfg['nights_max']} nocí, 1+2",
                    "url": f"{HOME}/vysledky-vyhladavania?{urlencode(q)}"})
    out.append({"transport": "flight", "label": "Turecko (ponuky z Bratislavy)", "url": HOME + "/turecko"})
    return out


def search(cfg):
    return []
