# Adapter modules run by run.py, in this order. Each module defines NAME, HOME, deeplinks(cfg) and
# search(cfg) -> list of offer dicts (see static/dovolenka/data/offers.json for the shape).
# A module with DEEPLINK_ONLY = True only contributes search links (its site needs JavaScript).
ADAPTERS = []
