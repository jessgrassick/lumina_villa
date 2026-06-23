"""
Canggu/Bali villa keyword search volume analysis
US (2840) + AU (2036) markets
"""

import sys
import json
import os

sys.path.insert(0, "/Users/classicgrassick/Desktop/Claude/Data For SEO")
from dataforseo_query import DataForSEOQuery

LOGIN = "dataforseo@webprofits.com.au"
PASSWORD = "d84aafdbfa9d2c8a"

client = DataForSEOQuery(LOGIN, PASSWORD)

keywords = [
    # Batch 1 - Core terms
    "canggu villa",
    "villa canggu",
    "canggu villas",
    "villa in canggu",
    "canggu villa rental",
    "private villa canggu",
    "luxury villa canggu",
    "cheap villa canggu",
    "villa canggu bali",
    # Batch 2 - Feature-specific
    "private pool villa canggu",
    "rice field villa bali",
    "3 bedroom villa canggu",
    "villa with pool bali",
    "rice paddy villa canggu",
    "outdoor bathtub villa bali",
    "villa near echo beach",
    "villa near berawa beach",
    # Batch 3 - Intent/booking
    "book villa canggu",
    "canggu villa airbnb",
    "canggu villa booking",
    "best villa canggu",
    "canggu accommodation",
    "where to stay canggu",
    "canggu holiday rental",
    "bali villa direct booking",
    # Batch 4 - Long tail
    "family villa canggu bali",
    "couples villa canggu",
    "honeymoon villa canggu",
    "digital nomad villa bali",
    "villa with concierge bali",
    "canggu villa with rice field view",
    "private chef villa bali",
]

print(f"Fetching US (2840) search volumes for {len(keywords)} keywords...")
us_result = client.keyword_search_volume(keywords, location_code=2840)

print(f"Fetching AU (2036) search volumes for {len(keywords)} keywords...")
au_result = client.keyword_search_volume(keywords, location_code=2036)

# Parse results into dicts keyed by keyword
def parse_volumes(result):
    data = {}
    try:
        items = result["tasks"][0]["result"]
        for item in items:
            kw = item.get("keyword", "").lower()
            data[kw] = {
                "volume": item.get("search_volume") or 0,
                "cpc": item.get("cpc") or 0.0,
                "competition": item.get("competition_index") or 0,
                "competition_level": item.get("competition") or "N/A",
            }
    except (KeyError, TypeError, IndexError) as e:
        print(f"Warning: could not parse result - {e}")
    return data

us_data = parse_volumes(us_result)
au_data = parse_volumes(au_result)

# Build combined rows
rows = []
for kw in keywords:
    kw_lower = kw.lower()
    us = us_data.get(kw_lower, {"volume": 0, "cpc": 0.0, "competition": 0.0, "competition_level": "N/A"})
    au = au_data.get(kw_lower, {"volume": 0, "cpc": 0.0, "competition": 0.0, "competition_level": "N/A"})
    rows.append({
        "keyword": kw,
        "us_volume": us["volume"],
        "au_volume": au["volume"],
        "combined_volume": us["volume"] + au["volume"],
        "us_cpc": us["cpc"],
        "au_cpc": au["cpc"],
        "us_competition": us["competition"],
        "us_competition_level": us["competition_level"],
    })

rows.sort(key=lambda r: r["combined_volume"], reverse=True)

# Print table
col_w = 38
print("\n")
print(f"{'KEYWORD':<{col_w}} {'US VOL':>8} {'AU VOL':>8} {'COMBINED':>10} {'US CPC':>8} {'COMPETITION':>13}")
print("-" * (col_w + 8 + 8 + 10 + 8 + 13 + 5))
for r in rows:
    comp = f"{r['us_competition_level']} ({r['us_competition']})" if r["us_competition_level"] != "N/A" else "N/A"
    print(
        f"{r['keyword']:<{col_w}} "
        f"{r['us_volume']:>8,} "
        f"{r['au_volume']:>8,} "
        f"{r['combined_volume']:>10,} "
        f"${r['us_cpc']:>7.2f} "
        f"{comp:>13}"
    )

# Save to JSON
output = {
    "keywords": rows,
    "raw": {
        "us": us_result,
        "au": au_result,
    }
}

output_path = "/Users/classicgrassick/Desktop/Claude/lumina-villa/search_volumes.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\n[SAVED] {output_path}")
print(f"Total keywords: {len(rows)}")
print(f"Keywords with US volume: {sum(1 for r in rows if r['us_volume'] > 0)}")
print(f"Keywords with AU volume: {sum(1 for r in rows if r['au_volume'] > 0)}")
