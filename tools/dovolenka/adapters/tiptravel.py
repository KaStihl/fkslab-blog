"""TIP travel – destination pages only (CeSYS platform, no known search URL scheme)."""

NAME = "TIP travel"
HOME = "https://exotika.tiptravel.sk"
DEEPLINK_ONLY = True


def deeplinks(cfg):
    return [
        {"transport": "flight", "label": "Turecko, odlety z Bratislavy / Košíc / Viedne", "url": HOME + "/turecko"},
        {"transport": "flight", "label": "Grécke ostrovy", "url": HOME + "/grecko/grecko-ostrovy"},
    ]


def search(cfg):
    return []
