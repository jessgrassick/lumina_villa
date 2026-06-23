"""
Canggu Villa SERP Analysis
Runs serp_google_organic for 8 target keywords (US location)
Extracts top 10 organic results, SERP features, and domain frequency
"""

import sys
import json
from collections import defaultdict
from urllib.parse import urlparse

sys.path.insert(0, "/Users/classicgrassick/Desktop/Claude/Data For SEO")
from dataforseo_query import DataForSEOQuery

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
LOGIN = "dataforseo@webprofits.com.au"
PASSWORD = "d84aafdbfa9d2c8a"
LOCATION_CODE = 2840  # USA
OUTPUT_PATH = "/Users/classicgrassick/Desktop/Claude/lumina-villa/serp_analysis.json"

KEYWORDS = [
    "canggu villa",
    "private pool villa canggu",
    "bali villa with rice field view",
    "villa rental canggu",
    "best villas in canggu",
    "3 bedroom villa canggu bali",
    "luxury villa canggu",
    "canggu accommodation",
]

# SERP feature type labels we care to surface
FEATURE_TYPES = {
    "featured_snippet",
    "local_pack",
    "paid",
    "people_also_ask",
    "knowledge_graph",
    "top_stories",
    "image_pack",
    "shopping",
    "hotels_pack",
    "related_searches",
    "video",
}


def extract_domain(url):
    """Return bare domain (no www) from a URL string."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url


def run_serp(client, keyword):
    """Call the API and return the raw JSON response."""
    print(f"  Querying: {keyword!r} ...", flush=True)
    result = client.serp_google_organic(keyword, location_code=LOCATION_CODE)
    return result


def parse_serp(raw):
    """
    Extract:
      - top 10 organic results  (position, domain, title, url)
      - list of SERP feature type strings present
    from a DataForSEO serp/google/organic/live/advanced response.
    """
    organic_results = []
    serp_features = set()

    try:
        task = raw["tasks"][0]
        result = task["result"][0]
        items = result.get("items") or []
    except (KeyError, IndexError, TypeError):
        return organic_results, list(serp_features)

    for item in items:
        itype = item.get("type", "")

        # Collect SERP features (non-organic items)
        if itype != "organic":
            label = itype.lower()
            # normalise a few common variants
            if label in ("paid", "ad", "ads"):
                serp_features.add("paid")
            elif label in ("featured_snippet",):
                serp_features.add("featured_snippet")
            elif label in ("local_pack", "local_pack_with_map"):
                serp_features.add("local_pack")
            elif label in ("people_also_ask", "people_also_ask_expanded"):
                serp_features.add("people_also_ask")
            elif label in ("hotels_pack",):
                serp_features.add("hotels_pack")
            elif label in ("knowledge_graph", "knowledge_box"):
                serp_features.add("knowledge_graph")
            elif label in ("top_stories", "news_box"):
                serp_features.add("top_stories")
            elif label in ("image_pack", "images"):
                serp_features.add("image_pack")
            elif label in ("shopping",):
                serp_features.add("shopping")
            elif label in ("related_searches",):
                serp_features.add("related_searches")
            elif label in ("video", "video_carousel"):
                serp_features.add("video")
            else:
                # Still record unknown features for transparency
                serp_features.add(label)
            continue

        # Organic result
        rank_absolute = item.get("rank_absolute") or item.get("position")
        url = item.get("url", "")
        title = item.get("title", "")
        domain = extract_domain(url)

        if rank_absolute is not None and rank_absolute <= 10:
            organic_results.append({
                "position": rank_absolute,
                "domain": domain,
                "title": title,
                "url": url,
            })

    # Sort by position and keep top 10
    organic_results.sort(key=lambda x: x["position"])
    organic_results = organic_results[:10]

    return organic_results, sorted(serp_features)


def main():
    client = DataForSEOQuery(LOGIN, PASSWORD)

    all_results = {}
    domain_frequency = defaultdict(int)  # domain -> number of SERPs it appears in

    print("\n=== Canggu Villa SERP Analysis ===\n")

    for keyword in KEYWORDS:
        raw = run_serp(client, keyword)
        organic, features = parse_serp(raw)

        # Track domain frequency (unique per keyword)
        seen_domains = set()
        for r in organic:
            d = r["domain"]
            if d not in seen_domains:
                domain_frequency[d] += 1
                seen_domains.add(d)

        all_results[keyword] = {
            "organic_top10": organic,
            "serp_features": features,
            "raw_response": raw,
        }

    # ---------------------------------------------------------------------------
    # Save full JSON
    # ---------------------------------------------------------------------------
    output = {
        "keywords_analysed": KEYWORDS,
        "location_code": LOCATION_CODE,
        "results": {
            kw: {
                "organic_top10": v["organic_top10"],
                "serp_features": v["serp_features"],
                "raw_response": v["raw_response"],
            }
            for kw, v in all_results.items()
        },
        "domain_frequency": dict(
            sorted(domain_frequency.items(), key=lambda x: x[1], reverse=True)
        ),
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] Full results written to: {OUTPUT_PATH}\n")

    # ---------------------------------------------------------------------------
    # Print clean summary
    # ---------------------------------------------------------------------------
    print("=" * 70)
    print("SUMMARY: TOP 5 DOMAINS PER KEYWORD + SERP FEATURES")
    print("=" * 70)

    for kw in KEYWORDS:
        data = all_results[kw]
        print(f"\n  Keyword: \"{kw}\"")
        print(f"  SERP features: {', '.join(data['serp_features']) if data['serp_features'] else 'none detected'}")
        print("  Top 5 organic domains:")
        for r in data["organic_top10"][:5]:
            print(f"    {r['position']:>2}. {r['domain']:<45} {r['title'][:60]}")

    print("\n" + "=" * 70)
    print("DOMAIN FREQUENCY TABLE (appearances across all 8 SERPs)")
    print("=" * 70)
    sorted_domains = sorted(domain_frequency.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  {'Domain':<45} {'SERPs'}")
    print(f"  {'-'*45} {'-----'}")
    for domain, count in sorted_domains:
        bar = "#" * count
        print(f"  {domain:<45} {count:>2}  {bar}")

    print("\n")


if __name__ == "__main__":
    main()
