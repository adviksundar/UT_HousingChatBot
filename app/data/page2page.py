import json
import requests, pandas as pd

#https://www.zillow.com/austin-tx-78705/rentals/5_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A5%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-97.77862197101366%2C%22east%22%3A-97.70128852069628%2C%22south%22%3A30.27176827605616%2C%22north%22%3A30.31419690076741%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A92618%2C%22regionType%22%3A7%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22paymentd%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A15%2C%22usersSearchTerm%22%3A%22Austin%20TX%2078705%22%7D
#"https://www.zillow.com/austin-tx-78705/rentals/
CSV_PATH = 'austin5_78705_listings.csv'
api_url = 'https://www.page2api.com/api/v1/scrape'
payload = {
      "api_key": "09f9dea7228120c1826b8a6306f0ccba9b3513e2",
      "url": "https://www.zillow.com/austin-tx-78705/rentals/5_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A5%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-97.77862197101366%2C%22east%22%3A-97.70128852069628%2C%22south%22%3A30.27176827605616%2C%22north%22%3A30.31419690076741%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A92618%2C%22regionType%22%3A7%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22paymentd%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A15%2C%22usersSearchTerm%22%3A%22Austin%20TX%2078705%22%7D",
      "real_browser": True,
      "merge_loops": True,
      "premium_proxy": "de",
      "scenario": [
        {
          "loop": [
            { "wait_for": "article.property-card" },
            { "execute_js": "var articles = document.querySelectorAll('article')"},
            { "execute_js": "articles[Math.round(articles.length/4)]?.scrollIntoView({behavior: 'smooth'})"},
            { "wait": 1 },
            { "execute_js": "articles[Math.round(articles.length/2)]?.scrollIntoView({behavior: 'smooth'})"},
            { "wait": 1 },
            { "execute_js": "articles[Math.round(articles.length/1.5)]?.scrollIntoView({behavior: 'smooth'})"},
            { "wait": 1 },
            { "execute_js": "articles[Math.round(articles.length/1.3)]?.scrollIntoView({behavior: 'smooth'})"},
            { "wait": 1 },
            { "execute": "parse"},
            { "execute_js": "document.querySelector('.search-pagination a[rel=next]')?.click()" }
          ],
          "iterations": 15
          
        }
      ],
      "parse": {
        "properties": [
          {
            "url": "a >> href",
            "price": "[data-test=property-card-price] >> text",
            "_parent": "article.property-card",
            "address": "[data-test=property-card-addr] >> text",
            "bedrooms": "ul[class*=StyledPropertyCardHomeDetails] li:nth-child(1) b >> text",
            "bathrooms": "ul[class*=StyledPropertyCardHomeDetails] li:nth-child(2) b >> text",
            "living_area": "ul[class*=StyledPropertyCardHomeDetails] li:nth-child(3) b >> text"
          }
        ]
      }
    }

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(api_url, data=json.dumps(payload), headers=headers)
result = json.loads(response.text)

print(result)
# ---------- 1. locate the list of properties ----------
# In Page2API’s response, the properties usually live at:
# result["scrape_result"]["properties"]
# but the exact path can differ by plan.  A small helper keeps it robust:

def find_properties(obj):
    """Depth-first search for a list of dicts with the expected keys."""
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        # basic sanity check: must have at least the 'url' or 'price' field
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
    raise ValueError("Couldn’t find the properties list in the response JSON")

# ---------- 2. dump to CSV ----------
import pandas as pd

df = pd.DataFrame(properties)
csv_path = "redwood_city_listings.csv"
df.to_csv(csv_path, index=False)
print(f"Saved {len(df)} rows → {csv_path}")

