"""
Elite Havens Deep Dive - DataForSEO Analysis
"""

import sys
import json
import requests

sys.path.insert(0, "/Users/classicgrassick/Desktop/Claude/Data For SEO")
from dataforseo_query import DataForSEOQuery

LOGIN = "dataforseo@webprofits.com.au"
PASSWORD = "d84aafdbfa9d2c8a"
OUTPUT_FILE = "/Users/classicgrassick/Desktop/Claude/lumina-villa/elite_havens_keywords.json"
DOMAIN = "elitehavens.com"

client = DataForSEOQuery(LOGIN, PASSWORD)

# ── Helper: direct POST with custom location ──────────────────────────────────
def post(endpoint, payload):
    url = f"{client.base_url}/{endpoint}"
    r = requests.post(url, headers=client.headers, json=payload)
    return r.json()

# ── 1. Domain rank overview  (AU + US) ───────────────────────────────────────
print("\n[1/3] Fetching domain_rank_overview (AU + US)...")
rank_au = post("dataforseo_labs/google/domain_rank_overview/live", [{
    "target": DOMAIN, "language_code": "en", "location_code": 2036
}])
rank_us = post("dataforseo_labs/google/domain_rank_overview/live", [{
    "target": DOMAIN, "language_code": "en", "location_code": 2840
}])

# ── 2. Ranked keywords (AU, limit 1000) ──────────────────────────────────────
print("[2/3] Fetching ranked_keywords (AU, limit=1000)...")
ranked_raw = post("dataforseo_labs/google/ranked_keywords/live", [{
    "target": DOMAIN,
    "language_code": "en",
    "location_code": 2036,
    "limit": 1000
}])

# ── 3. Competitor domains (AU, limit 20) ─────────────────────────────────────
print("[3/3] Fetching competitor_domains (AU)...")
comps_raw = post("dataforseo_labs/google/competitors_domain/live", [{
    "target": DOMAIN,
    "language_code": "en",
    "location_code": 2036,
    "limit": 20
}])

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Domain rank overview extraction ──────────────────────────────────────────
def extract_rank_metrics(resp, label):
    try:
        item = resp["tasks"][0]["result"][0]["items"][0]["metrics"]["organic"]
        return {
            "location": label,
            "etv": item.get("etv", 0),
            "count": item.get("count", 0),
            "pos_1": item.get("pos_1", 0),
            "pos_2_3": item.get("pos_2_3", 0),
            "pos_4_10": item.get("pos_4_10", 0),
            "pos_11_20": item.get("pos_11_20", 0),
            "pos_21_30": item.get("pos_21_30", 0),
            "pos_31_40": item.get("pos_31_40", 0),
            "pos_41_50": item.get("pos_41_50", 0),
            "is_new": item.get("is_new", 0),
            "is_up": item.get("is_up", 0),
            "is_down": item.get("is_down", 0),
            "is_lost": item.get("is_lost", 0),
            "estimated_paid_traffic_cost": item.get("estimated_paid_traffic_cost", 0),
        }
    except Exception as e:
        return {"location": label, "error": str(e), "raw_keys": list(resp.get("tasks", [{}])[0].keys())}

metrics_au = extract_rank_metrics(rank_au, "AU (2036)")
metrics_us = extract_rank_metrics(rank_us, "US (2840)")

# ── Ranked keywords extraction ────────────────────────────────────────────────
all_keywords = []
try:
    items = ranked_raw["tasks"][0]["result"][0]["items"]
    for item in items:
        kw = item.get("keyword_data", {}).get("keyword", "")
        sv  = item.get("keyword_data", {}).get("keyword_info", {}).get("search_volume") or 0
        pos = item.get("ranked_serp_element", {}).get("serp_item", {}).get("rank_absolute") or 0
        url = item.get("ranked_serp_element", {}).get("serp_item", {}).get("url") or ""
        all_keywords.append({"keyword": kw, "position": pos, "search_volume": sv, "url": url})
except Exception as e:
    print(f"  WARNING: ranked_keywords extraction error: {e}")

# Position bands
def band(pos):
    if pos <= 3:   return "1-3"
    if pos <= 10:  return "4-10"
    if pos <= 20:  return "11-20"
    if pos <= 50:  return "21-50"
    return "51+"

from collections import defaultdict
bands = defaultdict(list)
for kw in all_keywords:
    bands[band(kw["position"])].append(kw)

# ── Bali / Canggu filter ─────────────────────────────────────────────────────
BALI_TERMS = [
    "bali", "canggu", "seminyak", "ubud", "uluwatu", "jimbaran",
    "sanur", "nusa dua", "kerobokan", "berawa", "pererenan",
    "lombok", "indonesia", "villa bali", "bali villa", "bali villas",
]

def is_bali(kw_str):
    kw_lower = kw_str.lower()
    return any(t in kw_lower for t in BALI_TERMS)

bali_keywords = [kw for kw in all_keywords if is_bali(kw["keyword"])]
bali_keywords.sort(key=lambda x: x["search_volume"], reverse=True)
top50_bali = bali_keywords[:50]

# Group Bali keywords by URL
url_groups = defaultdict(list)
for kw in bali_keywords:
    url_groups[kw["url"]].append(kw)

url_summary = []
for url, kws in url_groups.items():
    kws.sort(key=lambda x: x["search_volume"], reverse=True)
    url_summary.append({
        "url": url,
        "keyword_count": len(kws),
        "total_search_volume": sum(k["search_volume"] for k in kws),
        "top_keywords": kws[:5]
    })
url_summary.sort(key=lambda x: x["total_search_volume"], reverse=True)

# ── Competitors extraction ─────────────────────────────────────────────────────
competitors = []
try:
    comp_items = comps_raw["tasks"][0]["result"][0]["items"]
    for item in comp_items[:15]:
        competitors.append({
            "domain": item.get("domain", ""),
            "avg_position": item.get("avg_position", 0),
            "sum_position": item.get("sum_position", 0),
            "intersections": item.get("intersections", 0),
            "competitor_metrics": item.get("metrics", {}).get("organic", {}),
        })
except Exception as e:
    print(f"  WARNING: competitors extraction error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE FULL RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
output = {
    "domain": DOMAIN,
    "domain_rank_overview": {
        "au": rank_au,
        "us": rank_us
    },
    "ranked_keywords_raw": ranked_raw,
    "competitor_domains_raw": comps_raw,
    "analysis": {
        "rank_metrics_au": metrics_au,
        "rank_metrics_us": metrics_us,
        "total_keywords_ranked": len(all_keywords),
        "position_bands": {
            "1-3":   len(bands["1-3"]),
            "4-10":  len(bands["4-10"]),
            "11-20": len(bands["11-20"]),
            "21-50": len(bands["21-50"]),
            "51+":   len(bands["51+"]),
        },
        "bali_canggu_keywords": {
            "total": len(bali_keywords),
            "top_50_by_volume": top50_bali,
            "by_url": url_summary
        },
        "top_15_competitors": competitors
    }
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)
print(f"\n[SAVED] Full results -> {OUTPUT_FILE}")

# ═══════════════════════════════════════════════════════════════════════════════
# STDOUT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
SEP = "=" * 70

print(f"\n{SEP}")
print(f"  ELITE HAVENS — SEO DEEP DIVE  |  {DOMAIN}")
print(SEP)

# Domain overview
print("\n## DOMAIN RANK OVERVIEW")
for m in [metrics_au, metrics_us]:
    if "error" in m:
        print(f"  {m['location']}: ERROR — {m['error']}")
        continue
    print(f"\n  {m['location']}")
    print(f"    Total keywords : {m['count']:,}")
    print(f"    Est. org traffic (ETV) : {m['etv']:,.0f}")
    print(f"    Est. paid traffic cost : ${m['estimated_paid_traffic_cost']:,.0f}")
    print(f"    Pos 1          : {m['pos_1']:,}")
    print(f"    Pos 2-3        : {m['pos_2_3']:,}")
    print(f"    Pos 4-10       : {m['pos_4_10']:,}")
    print(f"    Pos 11-20      : {m['pos_11_20']:,}")
    print(f"    Pos 21-30      : {m['pos_21_30']:,}")
    print(f"    Pos 31-50      : {m['pos_31_40'] + m['pos_41_50']:,}")
    print(f"    KWs trending up   : {m['is_up']:,}")
    print(f"    KWs trending down : {m['is_down']:,}")
    print(f"    New KWs           : {m['is_new']:,}")
    print(f"    Lost KWs          : {m['is_lost']:,}")

# Position bands (AU ranked query)
print(f"\n## RANKED KEYWORDS — AU (position bands)")
print(f"  Total keywords returned : {len(all_keywords):,}")
for b_label in ["1-3", "4-10", "11-20", "21-50", "51+"]:
    print(f"  Pos {b_label:<6}: {len(bands[b_label]):,}")

# Bali / Canggu keywords
print(f"\n## BALI / CANGGU KEYWORDS")
print(f"  Total matching          : {len(bali_keywords):,}")
print(f"\n  Top 50 by search volume:")
print(f"  {'#':<4} {'Keyword':<45} {'Pos':>4}  {'SV':>8}  URL (truncated)")
print(f"  {'-'*4} {'-'*45} {'-'*4}  {'-'*8}  {'-'*40}")
for i, kw in enumerate(top50_bali, 1):
    url_short = kw["url"][-50:] if kw["url"] else ""
    print(f"  {i:<4} {kw['keyword']:<45} {kw['position']:>4}  {kw['search_volume']:>8,}  ...{url_short}")

# By URL
print(f"\n  Bali/Canggu keywords grouped by URL:")
print(f"  {'URL':<65} {'KWs':>4}  {'Total SV':>9}")
print(f"  {'-'*65} {'-'*4}  {'-'*9}")
for u in url_summary[:20]:
    url_short = u["url"][-62:] if u["url"] else "(none)"
    print(f"  ...{url_short:<62} {u['keyword_count']:>4}  {u['total_search_volume']:>9,}")

# Competitors
print(f"\n## TOP 15 COMPETITORS (AU)")
print(f"  {'Domain':<40} {'Intersect':>9}  {'Avg Pos':>8}  {'Count':>7}  {'ETV':>10}")
print(f"  {'-'*40} {'-'*9}  {'-'*8}  {'-'*7}  {'-'*10}")
for c in competitors:
    m = c.get("competitor_metrics", {})
    count = m.get("count", 0)
    etv = m.get("etv", 0)
    print(f"  {c['domain']:<40} {c['intersections']:>9,}  {c['avg_position']:>8.1f}  {count:>7,}  {etv:>10,.0f}")

print(f"\n{SEP}\n")
