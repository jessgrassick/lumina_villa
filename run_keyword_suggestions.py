"""
Canggu Villa keyword suggestions script.
Pulls keyword_suggestions from DataForSEO Labs for a set of seed keywords,
dedupes, and saves a clean summary sorted by search volume.
"""

import sys
import json

sys.path.insert(0, "/Users/classicgrassick/Desktop/Claude/Data For SEO")
from dataforseo_query import DataForSEOQuery

LOGIN = "dataforseo@webprofits.com.au"
PASSWORD = "d84aafdbfa9d2c8a"
OUTPUT_PATH = "/Users/classicgrassick/Desktop/Claude/lumina-villa/keyword_suggestions.json"

# --- Define all queries to run ---
QUERIES = [
    # US market — 5 seed keywords
    {"keyword": "canggu villa",          "location_code": 2840},
    {"keyword": "bali private pool villa","location_code": 2840},
    {"keyword": "rice field villa bali", "location_code": 2840},
    {"keyword": "3 bedroom villa canggu","location_code": 2840},
    {"keyword": "villa rental canggu bali","location_code": 2840},
    # AU market — 2 seed keywords
    {"keyword": "canggu villa",          "location_code": 2036},
    {"keyword": "bali villa rental",     "location_code": 2036},
]


def extract_keywords(response):
    """Parse a keyword_suggestions API response and return a list of keyword dicts."""
    keywords = []
    try:
        tasks = response.get("tasks", [])
        for task in tasks:
            results = task.get("result", []) or []
            for result in results:
                items = result.get("items", []) or []
                for item in items:
                    kw = item.get("keyword", "")
                    kd = item.get("keyword_info", {}) or {}
                    sv = kd.get("search_volume") or 0
                    cpc = kd.get("cpc") or 0.0
                    comp = kd.get("competition") or 0.0
                    if kw:
                        keywords.append({
                            "keyword": kw,
                            "search_volume": sv,
                            "cpc": round(cpc, 2),
                            "competition": round(comp, 3),
                        })
    except Exception as e:
        print(f"  [WARN] Error parsing response: {e}")
    return keywords


def main():
    client = DataForSEOQuery(LOGIN, PASSWORD)

    all_keywords = {}  # keyword -> best (highest volume) record

    for q in QUERIES:
        kw = q["keyword"]
        loc = q["location_code"]
        loc_label = "US" if loc == 2840 else "AU"
        print(f"[QUERY] keyword_suggestions: '{kw}' | location: {loc_label} ({loc})")

        try:
            response = client.keyword_suggestions(kw, location_code=loc, limit=100)
            status = response.get("status_code")
            if status != 20000:
                print(f"  [ERROR] API status {status}: {response.get('status_message')}")
                continue

            extracted = extract_keywords(response)
            print(f"  -> {len(extracted)} keywords returned")

            for rec in extracted:
                existing = all_keywords.get(rec["keyword"])
                if existing is None or rec["search_volume"] > existing["search_volume"]:
                    all_keywords[rec["keyword"]] = rec

        except Exception as e:
            print(f"  [ERROR] Request failed: {e}")
            import traceback
            traceback.print_exc()

    # Sort by search_volume descending
    sorted_keywords = sorted(all_keywords.values(), key=lambda x: x["search_volume"], reverse=True)

    print(f"\n[DONE] Total unique keywords collected: {len(sorted_keywords)}")

    # Save full output
    output = {
        "total_keywords": len(sorted_keywords),
        "keywords": sorted_keywords,
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"[SAVED] Full results -> {OUTPUT_PATH}")

    # Print top 50
    print("\n" + "=" * 80)
    print(f"{'RANK':<5} {'KEYWORD':<45} {'VOLUME':>8}  {'CPC':>6}  {'COMPETITION':>11}")
    print("=" * 80)
    for i, kw in enumerate(sorted_keywords[:50], 1):
        print(f"{i:<5} {kw['keyword']:<45} {kw['search_volume']:>8,}  ${kw['cpc']:>5.2f}  {kw['competition']:>11.3f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
