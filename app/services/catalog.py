from urllib.parse import quote_plus

HOME_CATALOG = [
    ("LED Ceiling Light", "Lighting", "Amazon", 1299, "Bright, low-energy lighting"),
    ("Modern Ceiling Fan", "Fans", "Amazon", 2499, "Practical airflow with a clean design"),
    ("Minimal Dining Table", "Furniture", "IKEA", 8990, "Compact modern dining option"),
    ("Wall Art Set", "Decor", "Amazon", 1499, "Adds visual character to a room"),
    ("Storage Cabinet", "Storage", "IKEA", 5990, "Useful for organized living spaces"),
    ("Accent Floor Lamp", "Lighting", "IKEA", 3490, "Warm accent lighting for bedrooms/living rooms"),
]
PARTY_CATALOG = [
    ("Birthday Catering Package", "Catering", "Swiggy", 450, "per guest", 1),
    ("Party Catering Package", "Catering", "Zomato", 550, "per guest", 1),
    ("Decoration Starter Pack", "Decoration", "Amazon", 2999, "basic decor", 1),
    ("Event Sound & Lights", "Entertainment", "Local Vendor", 6500, "event package", 1),
    ("Budget Hotel Stay", "Accommodation", "OYO", 1800, "per room", 1),
]
JEWELRY_CATALOG = [
    ("Pearl Drop Earrings", "Earrings", "Amazon", 899, "Elegant and versatile"),
    ("Gold-Tone Pendant Set", "Necklace", "Flipkart", 1799, "Works well for festive occasions"),
    ("Kundan Statement Set", "Necklace", "Amazon", 2999, "Traditional statement styling"),
    ("Minimal Hoop Earrings", "Earrings", "Flipkart", 699, "Simple everyday styling"),
    ("Crystal Bracelet", "Bracelet", "Amazon", 1199, "Adds subtle sparkle"),
]

def search_link(platform: str, query: str) -> str:
    domains = {"Amazon":"https://www.amazon.in/s?k=", "Flipkart":"https://www.flipkart.com/search?q=", "IKEA":"https://www.ikea.com/in/en/search/?q=", "Swiggy":"https://www.swiggy.com/search?query=", "Zomato":"https://www.zomato.com/search?query=", "OYO":"https://www.oyorooms.com/search?location="}
    return domains.get(platform, "https://www.google.com/search?q=") + quote_plus(query)

def home_fallback(req):
    budget = req.budget
    chosen = []
    weights = {"Lighting": .16, "Fans": .15, "Furniture": .35, "Decor": .16, "Storage": .18}
    for name, cat, platform, price, reason in HOME_CATALOG:
        if cat in weights:
            qty = max(1, min(req.items.get(name.lower().replace(" ", "_"), 1), 10))
            if price * qty <= budget * weights[cat] * 1.35:
                chosen.append((name, cat, platform, price, qty, reason))
    if not chosen: chosen = [(HOME_CATALOG[0][0], HOME_CATALOG[0][1], HOME_CATALOG[0][2], HOME_CATALOG[0][3], 1, HOME_CATALOG[0][4])]
    total = sum(p*q for _,_,_,p,q,_ in chosen)
    while total > budget and len(chosen) > 1:
        chosen.pop(); total = sum(p*q for _,_,_,p,q,_ in chosen)
    recs = [dict(name=n, category=c, platform=p, estimated_price=pr, quantity=q, subtotal=pr*q, reason=f"{r}; selected for {req.style} style.", link=search_link(p,n)) for n,c,p,pr,q,r in chosen]
    allocation = {"Furniture": budget*.35, "Lighting":budget*.16, "Decor":budget*.16, "Storage":budget*.18, "Fans":budget*.15}
    return recs, allocation, total

def party_fallback(req):
    budget = req.budget
    allocation = {"Catering":budget*.50, "Decoration":budget*.15, "Entertainment":budget*.20, "Accommodation":budget*.15}
    recs=[]
    for name,cat,platform,price,unit,qty in PARTY_CATALOG:
        if cat == "Catering": subtotal=price*req.guests; q=req.guests
        else: subtotal=price; q=1
        if subtotal <= allocation.get(cat, budget):
            recs.append(dict(name=name, category=cat, platform=platform, estimated_price=price, quantity=q, subtotal=subtotal, reason=f"Fits the {req.event_type} plan for {req.guests} guests ({unit}).", link=search_link(platform, name)))
    total=sum(x["subtotal"] for x in recs)
    return recs, allocation, min(total,budget)

def jewelry_fallback(req):
    recs=[]
    for name,cat,platform,price,reason in JEWELRY_CATALOG:
        if price <= req.budget*.75:
            recs.append(dict(name=name, category=cat, platform=platform, estimated_price=price, quantity=1, subtotal=price, reason=f"{reason}; suitable for {req.occasion} and {req.style} style.", link=search_link(platform,name)))
    if not recs: recs=[dict(name=JEWELRY_CATALOG[0][0],category=JEWELRY_CATALOG[0][1],platform=JEWELRY_CATALOG[0][2],estimated_price=JEWELRY_CATALOG[0][3],quantity=1,subtotal=JEWELRY_CATALOG[0][3],reason="Budget-friendly fallback option.",link=search_link("Amazon",JEWELRY_CATALOG[0][0]))]
    total=sum(x["subtotal"] for x in recs[:3])
    return recs[:3], {"Jewelry": req.budget}, total
