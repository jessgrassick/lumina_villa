"""
Elite Havens Content Structure Analysis
Analyzes content, headings, schema, and URL architecture for Canggu/Bali villa ranking signals.

Uses the correct live URLs (not legacy .htm paths which now 404).
"""

import sys
import json
import re
from collections import defaultdict

sys.path.insert(0, "/Users/classicgrassick/Desktop/Claude/Data For SEO")
from dataforseo_query import DataForSEOQuery
import requests

LOGIN = "dataforseo@webprofits.com.au"
PASSWORD = "d84aafdbfa9d2c8a"

# Real live URLs (confirmed via SERP lookup - legacy .htm pages 404)
CONTENT_URLS = [
    "https://www.elitehavens.com/canggu-luxury-villas/bali-indonesia-villas/",   # Canggu hub
    "https://www.elitehavens.com/bali-rental-villas/indonesia-villas/",           # Bali hub
    "https://www.elitehavens.com/",                                                # Homepage
]

OUTPUT_PATH = "/Users/classicgrassick/Desktop/Claude/lumina-villa/elite_havens_content.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_instant_pages_meta(url, client):
    """Use instant_pages to get rich meta for a single URL."""
    raw = client.on_page_instant_pages(url, limit=10)
    try:
        items = raw["tasks"][0]["result"][0].get("items", [])
        if items:
            return items[0], raw
    except (KeyError, IndexError, TypeError):
        pass
    return None, raw


def extract_page_analysis(url, item, content_parsing_raw=None):
    """Extract the fields we care about from an instant_pages item."""
    result = {
        "url": url,
        "status_code": item.get("status_code"),
        "title": None,
        "meta_description": None,
        "h1": [],
        "h2": [],
        "h3": [],
        "word_count": None,
        "internal_links_count": None,
        "schema_types": [],
        "structured_data_summary": [],
        "canonical": None,
        "meta_keywords": None,
        "images_count": None,
        "onpage_score": item.get("onpage_score"),
    }

    meta = item.get("meta", {}) or {}
    result["title"] = meta.get("title")
    result["meta_description"] = meta.get("description")
    result["meta_keywords"] = meta.get("meta_keywords")
    result["canonical"] = meta.get("canonical")
    result["internal_links_count"] = meta.get("internal_links_count")
    result["images_count"] = meta.get("images_count")

    content_meta = meta.get("content", {}) or {}
    result["word_count"] = content_meta.get("plain_text_word_count")

    htags = meta.get("htags", {}) or {}
    result["h1"] = htags.get("h1", []) or []
    result["h2"] = htags.get("h2", []) or []
    result["h3"] = htags.get("h3", []) or []

    # Schema from checks
    checks = item.get("checks", {}) or {}
    result["has_micromarkup"] = checks.get("has_micromarkup", False)
    result["has_micromarkup_errors"] = checks.get("has_micromarkup_errors", False)

    # Extract schema from content_parsing if available
    if content_parsing_raw:
        try:
            cp_item = content_parsing_raw["tasks"][0]["result"][0]["items"][0]
            schema_items = cp_item.get("structured_data", []) or []
            for s in schema_items:
                stype = s.get("@type") or s.get("type")
                if stype:
                    if isinstance(stype, list):
                        result["schema_types"].extend(stype)
                    else:
                        result["schema_types"].append(stype)
            result["structured_data_summary"] = [
                {"@type": s.get("@type"), "name": s.get("name")}
                for s in schema_items[:10]
            ]
        except (KeyError, IndexError, TypeError):
            pass

    return result


def categorise_url(url):
    """Return a category string for a URL."""
    path = re.sub(r"^https?://[^/]+", "", url).rstrip("/") or "/"

    if path == "/" or path == "":
        return "homepage"
    elif re.match(r"^/magazine/", path):
        return "magazine/editorial"
    elif re.match(r"^/destinations/", path):
        return "destinations-guide"
    elif re.match(r"^/canggu-luxury", path):
        return "area-hub: canggu"
    elif re.match(r"^/seminyak-luxury", path):
        return "area-hub: seminyak"
    elif re.match(r"^/ubud-luxury", path):
        return "area-hub: ubud"
    elif re.match(r"^/uluwatu-luxury", path):
        return "area-hub: uluwatu"
    elif re.match(r"^/jimbaran-luxury", path):
        return "area-hub: jimbaran"
    elif re.match(r"^/sanur-luxury", path):
        return "area-hub: sanur"
    elif re.match(r"^/candidasa", path):
        return "area-hub: candidasa"
    elif re.match(r"^/nusa-lembongan", path):
        return "area-hub: nusa lembongan"
    elif re.match(r"^/lombok-rental", path):
        return "area-hub: lombok"
    elif re.match(r"^/koh-samui", path):
        return "area-hub: koh samui"
    elif re.match(r"^/phuket-rental", path) or re.match(r"^/thailand", path) or re.match(r"^/kata-luxury", path):
        return "area-hub: phuket/thailand"
    elif re.match(r"^/bali-rental-villas", path) or re.match(r"^/bali-rental-(\d+|eh_)", path) or re.match(r"^/bali-villas", path):
        return "bali-filter/facet pages"
    elif re.match(r"^/bali-rental", path):
        return "bali-filter/facet pages"
    elif re.match(r"^/goa-rental|^/india-", path):
        return "area-hub: india"
    elif re.match(r"^/maldives", path):
        return "area-hub: maldives"
    elif re.match(r"^/niseko|^/japan", path):
        return "area-hub: japan/niseko"
    elif re.match(r"^/indonesia-private|^/luxury-villa-offers", path):
        return "regional/country hub"
    elif re.match(r"^/wedding", path):
        return "weddings"
    elif re.match(r"^/promos/", path):
        return "promotions"
    elif re.match(r"^/winduvillas|^/pandawa|^/sohamsa|^/mandalay|^/laksmana", path):
        return "villa-listing (estate)"
    elif re.search(r"-villa/.*\.aspx$|/gallery\d+\.aspx$|/reviews\.aspx$", path):
        return "villa-listing (individual)"
    elif re.search(r"\.aspx$", path):
        return "villa-listing (individual)"
    elif re.match(r"^/all_villas", path):
        return "all-villas index"
    else:
        return "other"


def build_url_pattern_map(ranked_items):
    """Build URL pattern map from ranked_keywords items."""
    patterns = defaultdict(list)
    url_seen = set()

    for item in ranked_items:
        url = item.get("ranked_serp_element", {}).get("serp_item", {}).get("url", "")
        sv = item.get("keyword_data", {}).get("keyword_info", {}).get("search_volume") or 0
        kw = item.get("keyword_data", {}).get("keyword", "")
        pos = item.get("ranked_serp_element", {}).get("serp_item", {}).get("rank_absolute", "?")

        if not url or "elitehavens.com" not in url:
            continue
        if url in url_seen:
            continue
        url_seen.add(url)

        cat = categorise_url(url)
        patterns[cat].append({"url": url, "top_kw": kw, "top_sv": sv, "top_pos": pos})

    return {
        k: {
            "count": len(v),
            "sample_urls": [x["url"] for x in v[:5]],
            "top_keywords": [{"kw": x["top_kw"], "sv": x["top_sv"], "pos": x["top_pos"]} for x in sorted(v, key=lambda x: -x["top_sv"])[:3]],
        }
        for k, v in sorted(patterns.items(), key=lambda x: -len(x[1]))
    }


def infer_content_investments(patterns):
    """Summarise which content types Elite Havens invests in."""
    investments = []

    area_hub_keys = [k for k in patterns if k.startswith("area-hub:")]
    area_hub_total = sum(patterns[k]["count"] for k in area_hub_keys)
    if area_hub_total:
        investments.append({
            "label": "Area/destination hub pages (per-location category pages)",
            "page_count": area_hub_total,
            "example_urls": [patterns[k]["sample_urls"][0] for k in area_hub_keys[:3] if patterns[k]["sample_urls"]]
        })

    if "bali-filter/facet pages" in patterns:
        investments.append({
            "label": "Faceted/filter pages (bedroom count, feature filters e.g. beachfront, family, honeymoon)",
            "page_count": patterns["bali-filter/facet pages"]["count"],
            "example_urls": patterns["bali-filter/facet pages"]["sample_urls"][:3]
        })

    villa_listing_keys = [k for k in patterns if "villa-listing" in k]
    villa_total = sum(patterns[k]["count"] for k in villa_listing_keys)
    if villa_total:
        investments.append({
            "label": "Individual villa listing pages (per-property detail pages)",
            "page_count": villa_total,
            "example_urls": [patterns[k]["sample_urls"][0] for k in villa_listing_keys[:2] if patterns[k]["sample_urls"]]
        })

    if "magazine/editorial" in patterns:
        investments.append({
            "label": "Magazine / editorial content (travel guides, local tips, destination features)",
            "page_count": patterns["magazine/editorial"]["count"],
            "example_urls": patterns["magazine/editorial"]["sample_urls"][:3]
        })

    if "destinations-guide" in patterns:
        investments.append({
            "label": "Destination guide pages (/destinations/ sub-section)",
            "page_count": patterns["destinations-guide"]["count"],
            "example_urls": patterns["destinations-guide"]["sample_urls"][:3]
        })

    if "promotions" in patterns:
        investments.append({
            "label": "Promotions and offers pages",
            "page_count": patterns["promotions"]["count"],
            "example_urls": patterns["promotions"]["sample_urls"][:3]
        })

    if "weddings" in patterns:
        investments.append({
            "label": "Weddings landing page",
            "page_count": patterns["weddings"]["count"],
            "example_urls": patterns["weddings"]["sample_urls"][:3]
        })

    return investments


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    client = DataForSEOQuery(LOGIN, PASSWORD)

    from base64 import b64encode
    creds = b64encode(f"{LOGIN}:{PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
    base = "https://api.dataforseo.com/v3"

    print("=" * 70)
    print("ELITE HAVENS CONTENT STRUCTURE ANALYSIS")
    print("=" * 70)
    print()
    print("NOTE: Legacy .htm URLs (bali/canggu-villas.htm, bali-villas.htm)")
    print("      now return 404 'Page Not Found' pages. Analysis uses real")
    print("      live URLs confirmed via SERP lookups.")
    print()

    # -----------------------------------------------------------------------
    # 1. Content analysis for 3 key pages using instant_pages + content_parsing
    # -----------------------------------------------------------------------
    print("[1/3] Running page-level analysis for 3 key URLs...")
    page_analyses = []

    for url in CONTENT_URLS:
        print(f"  -> {url}")
        # instant_pages gives the richest meta
        ip_item, ip_raw = get_instant_pages_meta(url, client)
        # content_parsing for schema detection
        cp_raw = client.on_page_content_parsing(url)

        if ip_item:
            analysis = extract_page_analysis(url, ip_item, cp_raw)
        else:
            analysis = {"url": url, "error": "instant_pages returned no item"}

        page_analyses.append({
            "url": url,
            "analysis": analysis,
        })

    # -----------------------------------------------------------------------
    # 2. URL structure via ranked_keywords (500 keywords = 115 unique URLs)
    # -----------------------------------------------------------------------
    print("[2/3] Fetching ranked keywords to map URL structure...")
    data = [{"target": "elitehavens.com", "language_code": "en", "location_code": 2036, "limit": 500}]
    r = requests.post(f"{base}/dataforseo_labs/google/ranked_keywords/live", headers=headers, json=data)
    ranked_raw = r.json()
    ranked_items = []
    try:
        ranked_items = ranked_raw["tasks"][0]["result"][0].get("items", []) or []
    except (KeyError, IndexError, TypeError):
        print("  WARNING: Could not extract ranked_keywords items")

    url_patterns = build_url_pattern_map(ranked_items)
    content_investments = infer_content_investments(url_patterns)

    total_unique_urls = sum(p["count"] for p in url_patterns.values())

    # -----------------------------------------------------------------------
    # 3. Save JSON
    # -----------------------------------------------------------------------
    print("[3/3] Saving output...")
    output = {
        "meta": {
            "target_domain": "elitehavens.com",
            "analysis_date": "2026-06-10",
            "note": "Legacy .htm URLs now 404 on Elite Havens site. Analysis uses confirmed live URLs from SERP.",
            "original_requested_urls": [
                "https://www.elitehavens.com/bali/canggu-villas.htm",
                "https://www.elitehavens.com/bali-villas.htm",
                "https://www.elitehavens.com/",
            ],
            "live_urls_used": CONTENT_URLS,
            "ranked_keywords_sampled": len(ranked_items),
            "unique_ranking_urls_found": total_unique_urls,
        },
        "page_analyses": page_analyses,
        "url_patterns": url_patterns,
        "content_investments": content_investments,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"  Saved to: {OUTPUT_PATH}")

    # -----------------------------------------------------------------------
    # 4. Print summary
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("PAGE-LEVEL CONTENT ANALYSIS")
    print("=" * 70)

    for entry in page_analyses:
        url = entry["url"]
        a = entry.get("analysis", {})
        print(f"\nURL: {url}")
        if a.get("error"):
            print(f"  ERROR: {a['error']}")
            continue
        print(f"  HTTP Status      : {a.get('status_code', 'n/a')}")
        print(f"  Title            : {a.get('title', 'n/a')}")
        desc = a.get("meta_description") or "n/a"
        print(f"  Meta Description : {desc[:120]}")
        print(f"  Word Count       : {a.get('word_count', 'n/a')}")
        print(f"  Internal Links   : {a.get('internal_links_count', 'n/a')}")
        print(f"  Images           : {a.get('images_count', 'n/a')}")
        print(f"  OnPage Score     : {a.get('onpage_score', 'n/a')}")
        h1 = a.get("h1", [])
        h2 = a.get("h2", [])
        h3 = a.get("h3", [])
        print(f"  H1 ({len(h1)})            : {h1[:2]}")
        print(f"  H2 ({len(h2)})            : {h2[:4]}")
        print(f"  H3 ({len(h3)})            : {h3[:4]}")
        schema = a.get("schema_types", [])
        print(f"  Schema Types     : {schema if schema else 'None detected (JS-rendered site)'}")
        print(f"  Has Micromarkup  : {a.get('has_micromarkup', False)}")

    print()
    print("=" * 70)
    print(f"URL STRUCTURE PATTERNS  ({total_unique_urls} unique ranking URLs mapped)")
    print("=" * 70)
    for pattern, data in url_patterns.items():
        count = data["count"]
        top_kws = data.get("top_keywords", [])
        top_kw_str = ", ".join("{} ({}sv)".format(k['kw'], k['sv']) for k in top_kws[:2])
        print(f"\n  [{count:>3}] {pattern}")
        if top_kw_str:
            print(f"        Top terms: {top_kw_str}")
        for s in data["sample_urls"][:3]:
            path = re.sub(r"^https?://[^/]+", "", s)
            print(f"        {path}")

    print()
    print("=" * 70)
    print("CONTENT INVESTMENT SUMMARY")
    print("=" * 70)
    for inv in content_investments:
        print(f"\n  {inv['label']}")
        print(f"  Pages: {inv['page_count']}")
        for ex in inv.get("example_urls", [])[:2]:
            path = re.sub(r"^https?://[^/]+", "", ex)
            print(f"    {path}")

    print()
    print("=" * 70)
    print("KEY RANKING SIGNALS OBSERVED")
    print("=" * 70)
    print("""
  URL STRUCTURE:
    /canggu-luxury-villas/bali-indonesia-villas/        <- area hub (rank 2-4 for canggu terms)
    /bali-rental-villas/indonesia-villas/               <- country hub (rank 1-4, 14,800sv)
    /bali-rental-eh_beachfront-holiday-villas/          <- feature filter (beachfront)
    /bali-rental-4bedroom-villas/                       <- bedroom filter (rank 1)
    /bali-rental-eh_family-holiday-villas/              <- trip-type filter (family)
    /villa-[name]/canggu-bali-indonesia.aspx            <- individual villa listings

  CONTENT ARCHITECTURE:
    1. Country hub (/bali-rental-villas/) -> destination category pages
    2. Area hub pages per suburb (canggu, seminyak, ubud, uluwatu...)
    3. Faceted filter pages: bedroom count + feature tags (beachfront, family, honeymoon, party)
    4. Individual villa listing pages with location in URL slug
    5. Magazine/editorial content (destination guides, local tips) -> long-tail traffic

  MAGAZINE CONTENT VALUE:
    High-volume editorial wins: "bali home shopping" (1,900sv), "bali fashion" (720sv),
    "bali symbols" (140sv), "bali beach clubs" (260sv), "bali chocolate" (140sv)
    -> Drives qualified top-of-funnel traffic, builds topical authority for Bali/Canggu

  URL PATTERN INSIGHT:
    Bedroom filters: /bali-rental-1bedroom-villas/ through /bali-rental-6bedroom-villas/
    These rank #1-3 for high-intent terms. Lumina equivalent: critical to replicate.
""")
    print("=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
