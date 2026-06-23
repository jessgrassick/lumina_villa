"""
Elite Havens backlink profile analysis using DataForSEO
"""

import sys
import json

sys.path.insert(0, "/Users/classicgrassick/Desktop/Claude/Data For SEO")
from dataforseo_query import DataForSEOQuery

LOGIN = "dataforseo@webprofits.com.au"
PASSWORD = "d84aafdbfa9d2c8a"
TARGET = "elitehavens.com"
OUTPUT_PATH = "/Users/classicgrassick/Desktop/Claude/lumina-villa/elite_havens_backlinks.json"

client = DataForSEOQuery(LOGIN, PASSWORD)

print(f"[1/3] Fetching backlinks summary for {TARGET}...")
summary_raw = client.backlinks_summary(TARGET)

print(f"[2/3] Fetching backlinks pages (limit=100) for {TARGET}...")
# domain_pages endpoint does not support order_by — call directly
import requests
pages_raw = requests.post(
    f"{client.base_url}/backlinks/domain_pages/live",
    headers=client.headers,
    json=[{"target": TARGET, "limit": 100}]
).json()

print(f"[3/3] Fetching detailed backlinks (limit=100) for {TARGET}...")
detailed_raw = client.backlinks_detailed(TARGET, limit=100)

# ── Parse summary ────────────────────────────────────────────────────────────
summary_result = {}
try:
    task = summary_raw["tasks"][0]["result"][0]
    summary_result = {
        "total_backlinks": task.get("backlinks", 0),
        "referring_domains": task.get("referring_domains", 0),
        "referring_main_domains": task.get("referring_main_domains", 0),
        "referring_domains_nofollow": task.get("referring_domains_nofollow", 0),
        "referring_pages": task.get("referring_pages", 0),
        "referring_pages_nofollow": task.get("referring_pages_nofollow", 0),
        "domain_rank": task.get("rank", 0),
        "broken_backlinks": task.get("broken_backlinks", 0),
        "broken_pages": task.get("broken_pages", 0),
        "referring_ips": task.get("referring_ips", 0),
        "referring_subnets": task.get("referring_subnets", 0),
        "backlinks_spam_score": task.get("backlinks_spam_score", 0),
        "crawled_pages": task.get("crawled_pages", 0),
    }
except Exception as e:
    print(f"  [WARN] Could not parse summary: {e}")

# ── Parse pages ──────────────────────────────────────────────────────────────
top_pages = []
try:
    items = pages_raw["tasks"][0]["result"][0].get("items", [])
    # Backlink counts are nested inside page_summary
    items_sorted = sorted(
        items,
        key=lambda x: (x.get("page_summary") or {}).get("backlinks", 0),
        reverse=True
    )
    for item in items_sorted[:20]:
        ps = item.get("page_summary") or {}
        top_pages.append({
            "url": item.get("page", ""),
            "backlinks": ps.get("backlinks", 0),
            "referring_domains": ps.get("referring_domains", 0),
        })
except Exception as e:
    print(f"  [WARN] Could not parse pages: {e}")
    import traceback; traceback.print_exc()

# ── Parse detailed backlinks ─────────────────────────────────────────────────
top_referring_domains = []
try:
    items = detailed_raw["tasks"][0]["result"][0].get("items", [])
    for item in items[:30]:
        top_referring_domains.append({
            "source_url": item.get("url_from", ""),
            "domain": item.get("domain_from", ""),
            "rank": item.get("rank", 0),
            "anchor": item.get("anchor", ""),
            "dofollow": item.get("dofollow", False),
            "page_from_rank": item.get("page_from_rank", 0),
        })
except Exception as e:
    print(f"  [WARN] Could not parse detailed backlinks: {e}")

# ── Assemble full output ─────────────────────────────────────────────────────
full_output = {
    "target": TARGET,
    "summary": summary_result,
    "top_20_pages_by_backlinks": top_pages,
    "top_30_referring_domains_by_rank": top_referring_domains,
    "_raw": {
        "summary": summary_raw,
        "pages": pages_raw,
        "detailed": detailed_raw,
    }
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(full_output, f, indent=2)

print(f"\n[SAVED] Full results written to {OUTPUT_PATH}\n")

# ── Print clean summary ──────────────────────────────────────────────────────
print("=" * 65)
print("ELITE HAVENS — BACKLINK PROFILE SUMMARY")
print("=" * 65)

s = summary_result
print(f"\nDomain Rank:                   {s.get('domain_rank', 'N/A')}")
print(f"Total Backlinks:               {s.get('total_backlinks', 0):,}")
print(f"Referring Domains:             {s.get('referring_domains', 0):,}")
print(f"  of which nofollow domains:   {s.get('referring_domains_nofollow', 0):,}")
print(f"Referring Main Domains:        {s.get('referring_main_domains', 0):,}")
print(f"Referring Pages (unique):      {s.get('referring_pages', 0):,}")
print(f"  of which nofollow pages:     {s.get('referring_pages_nofollow', 0):,}")
print(f"Referring IPs:                 {s.get('referring_ips', 0):,}")
print(f"Referring Subnets:             {s.get('referring_subnets', 0):,}")
print(f"Broken Backlinks:              {s.get('broken_backlinks', 0):,}")
print(f"Broken Pages:                  {s.get('broken_pages', 0):,}")
print(f"Spam Score:                    {s.get('backlinks_spam_score', 0)}/100")
print(f"Crawled Pages:                 {s.get('crawled_pages', 0):,}")

print("\n" + "-" * 65)
print("TOP 20 PAGES BY BACKLINKS")
print("-" * 65)
print(f"{'#':<4} {'Backlinks':<12} {'Ref Domains':<14} {'URL'}")
print("-" * 65)
for i, p in enumerate(top_pages, 1):
    url = p["url"]
    if len(url) > 60:
        url = url[:57] + "..."
    print(f"{i:<4} {p['backlinks']:<12,} {p['referring_domains']:<14,} {url}")

print("\n" + "-" * 65)
print("TOP 30 REFERRING DOMAINS BY RANK")
print("-" * 65)
print(f"{'#':<4} {'Rank':<8} {'DF':<5} {'Domain':<35} {'Anchor'}")
print("-" * 65)
for i, r in enumerate(top_referring_domains, 1):
    domain = r["domain"][:33]
    anchor = r["anchor"][:30] if r["anchor"] else "(none)"
    df = "Y" if r["dofollow"] else "N"
    print(f"{i:<4} {r['rank']:<8} {df:<5} {domain:<35} {anchor}")

print("\n" + "=" * 65)
print("Done.")
