"""ONS-inspired mock product catalogue, shops and prices.

Used as fallback when Supabase is not configured.
"""

# ── Shops (spread across South London with real lat/lng) ─────────────────────

SHOPS = [
    {"id": "s1", "name": "Tesco Express",   "address": "12 High Street, Vauxhall",     "lat": 51.4869, "lng": -0.1238},
    {"id": "s2", "name": "Sainsbury's",     "address": "45 The Cut, Waterloo",         "lat": 51.5036, "lng": -0.1143},
    {"id": "s3", "name": "Lidl",            "address": "78 Acre Lane, Brixton",        "lat": 51.4613, "lng": -0.1136},
    {"id": "s4", "name": "Aldi",            "address": "3 Clapham Road, Stockwell",    "lat": 51.4721, "lng": -0.1204},
    {"id": "s5", "name": "Co-op Food",      "address": "22 Kennington Lane",           "lat": 51.4854, "lng": -0.1098},
    {"id": "s6", "name": "Iceland Foods",   "address": "99 Brixton Road",              "lat": 51.4745, "lng": -0.1162},
    {"id": "s7", "name": "Boots",           "address": "6 Lambeth Walk",               "lat": 51.4917, "lng": -0.1186},
    {"id": "s8", "name": "Screwfix",        "address": "15 Miles Street, Vauxhall",    "lat": 51.4861, "lng": -0.1270},
]

# ── Products (ONS Consumer Price Index inspired) ───────────────────────────────

PRODUCTS = [
    # Groceries — Dairy & Eggs
    {"id": "p01",  "name": "Whole Milk 2L",              "category": "Groceries", "unit": "2 litres"},
    {"id": "p02",  "name": "Semi-Skimmed Milk 2L",       "category": "Groceries", "unit": "2 litres"},
    {"id": "p03",  "name": "Free Range Eggs (6)",        "category": "Groceries", "unit": "6 pack"},
    {"id": "p04",  "name": "Salted Butter 250g",         "category": "Groceries", "unit": "250g"},
    {"id": "p05",  "name": "Cheddar Cheese 400g",        "category": "Groceries", "unit": "400g"},
    {"id": "p06",  "name": "Greek Yoghurt 500g",         "category": "Groceries", "unit": "500g"},
    # Groceries — Bread & Cereals
    {"id": "p07",  "name": "White Bread 800g",           "category": "Groceries", "unit": "800g"},
    {"id": "p08",  "name": "Wholemeal Bread 800g",       "category": "Groceries", "unit": "800g"},
    {"id": "p09",  "name": "Cornflakes 500g",            "category": "Groceries", "unit": "500g"},
    {"id": "p10",  "name": "Porridge Oats 1kg",          "category": "Groceries", "unit": "1kg"},
    # Groceries — Meat
    {"id": "p11",  "name": "Chicken Breast 500g",        "category": "Groceries", "unit": "500g"},
    {"id": "p12",  "name": "Beef Mince 500g",            "category": "Groceries", "unit": "500g"},
    {"id": "p13",  "name": "Back Bacon 300g",            "category": "Groceries", "unit": "300g"},
    # Groceries — Fruit & Veg
    {"id": "p14",  "name": "Bananas (loose)",            "category": "Groceries", "unit": "per kg"},
    {"id": "p15",  "name": "Baby Potatoes 1kg",          "category": "Groceries", "unit": "1kg"},
    {"id": "p16",  "name": "Carrots 1kg",                "category": "Groceries", "unit": "1kg"},
    {"id": "p17",  "name": "Onions 1kg",                 "category": "Groceries", "unit": "1kg"},
    # Groceries — Cupboard staples
    {"id": "p18",  "name": "Pasta 500g",                 "category": "Groceries", "unit": "500g"},
    {"id": "p19",  "name": "Rice 1kg",                   "category": "Groceries", "unit": "1kg"},
    {"id": "p20",  "name": "Tinned Tomatoes 400g",       "category": "Groceries", "unit": "400g"},
    {"id": "p21",  "name": "Baked Beans 400g",           "category": "Groceries", "unit": "400g"},
    {"id": "p22",  "name": "Olive Oil 500ml",            "category": "Groceries", "unit": "500ml"},
    {"id": "p23",  "name": "Tomato Ketchup 460g",        "category": "Groceries", "unit": "460g"},
    {"id": "p24",  "name": "Tea Bags (80)",              "category": "Groceries", "unit": "80 pack"},
    # Groceries — Drinks
    {"id": "p25",  "name": "Orange Juice 1L",            "category": "Groceries", "unit": "1 litre"},
    {"id": "p26",  "name": "Apple Juice 1L",             "category": "Groceries", "unit": "1 litre"},
    # Pharmacy
    {"id": "p27",  "name": "Paracetamol 500mg (16)",     "category": "Pharmacy",  "unit": "16 tablets"},
    {"id": "p28",  "name": "Ibuprofen 200mg (16)",       "category": "Pharmacy",  "unit": "16 tablets"},
    {"id": "p29",  "name": "Children's Paracetamol 100ml","category": "Pharmacy", "unit": "100ml"},
    {"id": "p30",  "name": "Plasters Assorted (40)",     "category": "Pharmacy",  "unit": "40 pack"},
    {"id": "p31",  "name": "Hand Sanitiser 250ml",       "category": "Pharmacy",  "unit": "250ml"},
    {"id": "p32",  "name": "Vitamin C 1000mg (30)",      "category": "Pharmacy",  "unit": "30 tablets"},
    {"id": "p33",  "name": "Antihistamine 10mg (7)",     "category": "Pharmacy",  "unit": "7 tablets"},
    {"id": "p34",  "name": "Cough Syrup 100ml",          "category": "Pharmacy",  "unit": "100ml"},
    {"id": "p35",  "name": "Cold & Flu Capsules (16)",   "category": "Pharmacy",  "unit": "16 capsules"},
    # Hardware
    {"id": "p36",  "name": "AA Batteries (4)",           "category": "Hardware",  "unit": "4 pack"},
    {"id": "p37",  "name": "AAA Batteries (4)",          "category": "Hardware",  "unit": "4 pack"},
    {"id": "p38",  "name": "LED Bulb E27 (806lm)",       "category": "Hardware",  "unit": "single"},
    {"id": "p39",  "name": "LED Bulb B22 (806lm)",       "category": "Hardware",  "unit": "single"},
    {"id": "p40",  "name": "Extension Lead 4-Gang",      "category": "Hardware",  "unit": "single"},
    {"id": "p41",  "name": "Duct Tape 50m",              "category": "Hardware",  "unit": "roll"},
    {"id": "p42",  "name": "Cable Ties (100)",           "category": "Hardware",  "unit": "100 pack"},
    {"id": "p43",  "name": "WD-40 Lubricant 200ml",      "category": "Hardware",  "unit": "200ml"},
    # Household
    {"id": "p44",  "name": "Washing Up Liquid 500ml",    "category": "Household", "unit": "500ml"},
    {"id": "p45",  "name": "Toilet Roll (9 pack)",       "category": "Household", "unit": "9 pack"},
    {"id": "p46",  "name": "Kitchen Roll (2 pack)",      "category": "Household", "unit": "2 pack"},
    {"id": "p47",  "name": "Bin Bags 50L (15)",          "category": "Household", "unit": "15 pack"},
    {"id": "p48",  "name": "Laundry Tablets (20)",       "category": "Household", "unit": "20 pack"},
    {"id": "p49",  "name": "Dishwasher Tablets (20)",    "category": "Household", "unit": "20 pack"},
    {"id": "p50",  "name": "Multi-Surface Spray 500ml",  "category": "Household", "unit": "500ml"},
    {"id": "p51",  "name": "Bleach 750ml",               "category": "Household", "unit": "750ml"},
    {"id": "p52",  "name": "Fabric Softener 1L",         "category": "Household", "unit": "1 litre"},
    {"id": "p53",  "name": "Sponge Scourers (3)",        "category": "Household", "unit": "3 pack"},
]

# ── Prices — (shop availability varies; not every shop stocks everything) ─────
# Format: product_id -> {shop_id: price_£}
# Aldi/Lidl cheapest, Sainsbury's/Co-op priciest, Iceland good on frozen

PRICES: dict[str, dict[str, float]] = {
    # Dairy
    "p01": {"s1": 1.39, "s2": 1.45, "s3": 1.09, "s4": 1.05, "s5": 1.55, "s6": 1.25},
    "p02": {"s1": 1.29, "s2": 1.35, "s3": 0.99, "s4": 0.95, "s5": 1.45, "s6": 1.15},
    "p03": {"s1": 1.80, "s2": 2.00, "s3": 1.49, "s4": 1.45, "s5": 2.10},
    "p04": {"s1": 1.60, "s2": 1.75, "s3": 1.35, "s4": 1.30, "s5": 1.85},
    "p05": {"s1": 2.75, "s2": 3.00, "s3": 2.45, "s4": 2.40, "s5": 3.20},
    "p06": {"s1": 1.10, "s2": 1.30, "s3": 0.95, "s4": 0.89, "s5": 1.40},
    # Bread & Cereals
    "p07": {"s1": 0.95, "s2": 1.10, "s3": 0.79, "s4": 0.75, "s5": 1.20, "s6": 0.89},
    "p08": {"s1": 1.10, "s2": 1.25, "s3": 0.89, "s4": 0.85, "s5": 1.35},
    "p09": {"s1": 1.45, "s2": 1.65, "s3": 1.19, "s4": 1.09, "s5": 1.75},
    "p10": {"s1": 1.29, "s2": 1.45, "s3": 0.99, "s4": 0.95, "s5": 1.55},
    # Meat
    "p11": {"s1": 3.50, "s2": 3.80, "s3": 3.10, "s4": 3.00, "s5": 4.00},
    "p12": {"s1": 2.80, "s2": 3.10, "s3": 2.49, "s4": 2.39, "s5": 3.25},
    "p13": {"s1": 2.25, "s2": 2.50, "s3": 1.99, "s4": 1.89, "s5": 2.75},
    # Fruit & Veg
    "p14": {"s1": 0.89, "s2": 0.99, "s3": 0.69, "s4": 0.65, "s5": 1.05},
    "p15": {"s1": 1.10, "s2": 1.25, "s3": 0.89, "s4": 0.85, "s5": 1.35},
    "p16": {"s1": 0.59, "s2": 0.69, "s3": 0.49, "s4": 0.45, "s5": 0.75},
    "p17": {"s1": 0.65, "s2": 0.75, "s3": 0.49, "s4": 0.45, "s5": 0.85},
    # Cupboard
    "p18": {"s1": 0.85, "s2": 0.90, "s3": 0.65, "s4": 0.62, "s5": 0.99},
    "p19": {"s1": 1.25, "s2": 1.40, "s3": 1.09, "s4": 0.99, "s5": 1.50},
    "p20": {"s1": 0.55, "s2": 0.60, "s3": 0.45, "s4": 0.42, "s5": 0.65},
    "p21": {"s1": 0.50, "s2": 0.55, "s3": 0.39, "s4": 0.37, "s5": 0.60},
    "p22": {"s1": 2.50, "s2": 2.75, "s3": 2.19, "s4": 2.09, "s5": 2.95},
    "p23": {"s1": 1.35, "s2": 1.50, "s3": 1.09, "s4": 0.99, "s5": 1.60},
    "p24": {"s1": 1.89, "s2": 2.10, "s3": 1.59, "s4": 1.49, "s5": 2.25},
    # Drinks
    "p25": {"s1": 1.20, "s2": 1.35, "s3": 0.99, "s4": 0.95, "s5": 1.45},
    "p26": {"s1": 1.15, "s2": 1.30, "s3": 0.95, "s4": 0.89, "s5": 1.40},
    # Pharmacy
    "p27": {"s1": 0.65, "s2": 0.85, "s3": 0.65, "s4": 0.62, "s5": 0.90, "s7": 0.99},
    "p28": {"s1": 0.75, "s2": 0.90, "s3": 0.72, "s4": 0.69, "s5": 0.99, "s7": 1.10},
    "p29": {"s1": 3.50, "s2": 3.75, "s5": 3.95, "s7": 4.20},
    "p30": {"s1": 1.25, "s2": 1.50, "s5": 1.60, "s7": 1.75},
    "p31": {"s1": 1.55, "s2": 1.75, "s5": 1.80, "s7": 1.99},
    "p32": {"s1": 2.80, "s2": 3.10, "s7": 3.50},
    "p33": {"s1": 2.25, "s2": 2.50, "s7": 2.99},
    "p34": {"s1": 3.20, "s2": 3.50, "s7": 3.99},
    "p35": {"s1": 2.65, "s2": 2.90, "s7": 3.25},
    # Hardware
    "p36": {"s1": 2.45, "s2": 2.65, "s4": 1.99, "s8": 1.79},
    "p37": {"s1": 2.25, "s2": 2.45, "s4": 1.89, "s8": 1.69},
    "p38": {"s1": 3.50, "s2": 3.75, "s8": 2.49},
    "p39": {"s1": 3.50, "s2": 3.75, "s8": 2.49},
    "p40": {"s1": 6.00, "s2": 6.50, "s8": 4.99},
    "p41": {"s1": 3.25, "s8": 2.99},
    "p42": {"s8": 2.49, "s1": 3.00},
    "p43": {"s1": 4.50, "s8": 3.99},
    # Household
    "p44": {"s1": 0.99, "s2": 1.15, "s3": 0.79, "s4": 0.75, "s5": 1.25, "s6": 0.89},
    "p45": {"s1": 3.25, "s2": 3.50, "s3": 2.79, "s4": 2.69, "s5": 3.75, "s6": 2.99},
    "p46": {"s1": 1.10, "s2": 1.25, "s3": 0.89, "s4": 0.85, "s5": 1.35},
    "p47": {"s1": 2.10, "s2": 2.35, "s3": 1.79, "s4": 1.69, "s5": 2.50},
    "p48": {"s1": 4.50, "s2": 5.00, "s3": 3.99, "s4": 3.89, "s5": 5.25, "s6": 4.25},
    "p49": {"s1": 4.25, "s2": 4.75, "s3": 3.79, "s4": 3.69, "s5": 5.00},
    "p50": {"s1": 1.25, "s2": 1.45, "s3": 0.99, "s4": 0.95, "s5": 1.55},
    "p51": {"s1": 0.89, "s2": 1.05, "s3": 0.75, "s4": 0.69, "s5": 1.15},
    "p52": {"s1": 2.75, "s2": 3.00, "s3": 2.39, "s4": 2.29, "s5": 3.25},
    "p53": {"s1": 1.20, "s2": 1.35, "s3": 0.99, "s4": 0.95, "s5": 1.45},
}

PRODUCT_BY_ID: dict[str, dict] = {p["id"]: p for p in PRODUCTS}
SHOP_BY_ID:    dict[str, dict] = {s["id"]: s for s in SHOPS}

CATEGORIES = sorted({p["category"] for p in PRODUCTS})

CATEGORY_ICONS = {
    "Groceries": "🛒",
    "Pharmacy":  "💊",
    "Hardware":  "🔧",
    "Household": "🧹",
}


def search_products(terms: list[str], category: str | None = None) -> list[dict]:
    """Return products matching any search term, optionally filtered by category."""
    matched = []
    seen = set()
    for term in terms:
        t = term.lower()
        for p in PRODUCTS:
            if p["id"] in seen:
                continue
            if category and p["category"] != category:
                continue
            if t in p["name"].lower() or t in p["category"].lower():
                matched.append(p)
                seen.add(p["id"])
    return matched


def products_by_category(category: str) -> list[dict]:
    return [p for p in PRODUCTS if p["category"] == category]


def get_price_rows(product_id: str, user_lat: float, user_lng: float) -> list[dict]:
    """Return price rows for a product sorted cheapest first, with distance."""
    import math

    def _haversine(lat1, lng1, lat2, lng2):
        R = 6371.0
        φ1, φ2 = math.radians(lat1), math.radians(lat2)
        dφ = math.radians(lat2 - lat1)
        dλ = math.radians(lng2 - lng1)
        a = math.sin(dφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(dλ / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    rows = []
    for shop_id, price in PRICES.get(product_id, {}).items():
        shop = SHOP_BY_ID.get(shop_id)
        if not shop:
            continue
        dist = _haversine(user_lat, user_lng, shop["lat"], shop["lng"])
        rows.append({
            "shop_id":  shop_id,
            "shop":     shop["name"],
            "address":  shop["address"],
            "lat":      shop["lat"],
            "lng":      shop["lng"],
            "price":    price,
            "distance": round(dist, 2),
        })
    return sorted(rows, key=lambda r: (r["price"], r["distance"]))
