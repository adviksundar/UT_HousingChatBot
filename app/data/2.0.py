import requests, json, pandas as pd

CSV_PATH = "austin6_78705_listings.csv"
API_URL  = "https://www.page2api.com/api/v1/scrape"

payload = {
    "api_key": "09f9dea7228120c1826b8a6306f0ccba9b3513e2",
    "url": "https://www.zillow.com/austin-tx-78705/rentals/6_p/",
    "real_browser": True,
    "merge_loops": True,
    "premium_proxy": "de",
    "scenario": [
        {
            "loop": [
                { "wait_for": "article.property-card" },
                { "execute_js": "var articles = document.querySelectorAll('article')" },
                { "execute_js": "articles[Math.round(articles.length/4)]?.scrollIntoView({behavior: 'smooth'})" },
                { "wait": 1 },
                { "execute_js": "articles[Math.round(articles.length/2)]?.scrollIntoView({behavior: 'smooth'})" },
                { "wait": 1 },
                { "execute_js": "articles[Math.round(articles.length/1.5)]?.scrollIntoView({behavior: 'smooth'})" },
                { "wait": 1 },
                { "execute": "parse" },
                { "execute_js": "document.querySelector('.search-pagination a[rel=next]')?.click()" }
            ],
            "iterations": 15,
            "stop_condition": (
                "var next=document.querySelector('.search-pagination a[rel=next]');"
                "next===null||next.getAttributeNames().includes('disabled')"
            )
        }
    ],
    "parse": {
        "properties": [
            {
                "_parent":   "article.property-card",
                "url":        "a >> href",
                "price":      "[data-test=property-card-price] >> text",
                "address":    "[data-test=property-card-addr] >> text",
                "bedrooms":   "ul[class*=StyledPropertyCardHomeDetails] li:nth-child(1) b >> text",
                "bathrooms":  "ul[class*=StyledPropertyCardHomeDetails] li:nth-child(2) b >> text",
                "living_area":"ul[class*=StyledPropertyCardHomeDetails] li:nth-child(3) b >> text"
            }
        ]
    }
}

# ------------ call Page2API ------------
resp = requests.post(
    API_URL,
    json=payload,
    headers={"Accept": "application/json"},
    timeout=60
)

print("HTTP", resp.status_code)
if resp.status_code != 200:
    print("Body preview:", resp.text[:400])
resp.raise_for_status()

result = resp.json()

# ------------ find listings list ------------
def find_properties(obj):
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        if {"url", "price"} & obj[0].keys():
            return obj
    if isinstance(obj, dict):
        for v in obj.values():
            found = find_properties(v)
            if found is not None:
                return found
    return None

properties = find_properties(result)
if not properties:
    raise ValueError("Couldn't locate the properties array in the JSON")

# ------------ save CSV ------------
df = pd.DataFrame(properties).drop_duplicates(subset="url")
df.to_csv(CSV_PATH, index=False)
print(f"Saved {len(df)} rows → {CSV_PATH}")
