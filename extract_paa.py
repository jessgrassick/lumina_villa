"""
Canggu/Bali Villa PAA Extractor
Pulls People Also Ask questions from Google SERPs via DataForSEO
"""

import sys
import json
import time
from collections import defaultdict

sys.path.insert(0, "/Users/classicgrassick/Desktop/Claude/Data For SEO")
from dataforseo_query import DataForSEOQuery

# ── Config ────────────────────────────────────────────────────────────────────

LOGIN    = "dataforseo@webprofits.com.au"
PASSWORD = "d84aafdbfa9d2c8a"

LOCATIONS = {
    "AU": 2036,
    "US": 2840,
}

KEYWORDS = {
    "booking_intent": [
        "canggu villa rental",
        "book villa canggu",
        "private villa canggu bali",
        "canggu villa with pool",
        "3 bedroom villa canggu",
    ],
    "discovery_research": [
        "best area to stay in canggu",
        "where to stay in canggu bali",
        "is canggu good for families",
        "canggu vs seminyak",
        "canggu vs ubud",
    ],
    "accommodation_trust": [
        "bali villa scam",
        "is it safe to book villa in bali",
        "bali villa vs hotel",
        "airbnb canggu bali",
        "canggu accommodation",
    ],
    "concierge_experience": [
        "things to do in canggu",
        "canggu restaurants",
        "canggu surf",
        "canggu yoga",
        "canggu nightlife",
        "bali private chef",
        "bali airport transfer canggu",
    ],
}

# Flatten keyword list with source group tags
ALL_KEYWORDS = []
for group, kws in KEYWORDS.items():
    for kw in kws:
        ALL_KEYWORDS.append((kw, group))

# ── Category classifier ───────────────────────────────────────────────────────

CATEGORIES = [
    "BOOKING & TRUST",
    "LOCATION & AREA",
    "VILLA & ACCOMMODATION",
    "ACTIVITIES & EXPERIENCES",
    "TRAVEL LOGISTICS",
    "FAMILY & GROUP",
]

CATEGORY_SIGNALS = {
    "BOOKING & TRUST": [
        "cancel", "refund", "deposit", "payment", "pay", "scam", "fraud", "safe",
        "book", "booking", "price", "cost", "cheap", "expensive", "deal", "discount",
        "review", "trust", "legit", "reliable", "direct book", "airbnb", "vrbo",
        "fee", "charge", "insurance",
    ],
    "LOCATION & AREA": [
        "area", "where", "neighborhood", "canggu vs", "vs seminyak", "vs ubud",
        "vs kuta", "vs nusa dua", "location", "map", "distance", "far",
        "seminyak", "ubud", "kuta", "sanur", "jimbaran", "uluwatu", "nusa lembongan",
        "north", "south", "west", "east", "berawa", "batu bolong", "pererenan",
    ],
    "VILLA & ACCOMMODATION": [
        "villa", "bedroom", "bathroom", "pool", "private pool", "amenities",
        "staff", "breakfast", "kitchen", "air con", "wifi", "hotel", "resort",
        "hostel", "guesthouse", "include", "what does", "what is included",
        "difference between villa and hotel",
    ],
    "ACTIVITIES & EXPERIENCES": [
        "do in", "things to do", "restaurant", "eat", "food", "drink", "bar",
        "nightlife", "surf", "surfing", "yoga", "spa", "massage", "temple",
        "rice field", "waterfall", "market", "shopping", "cook", "chef",
        "experience", "tour", "activity", "sunset", "beach",
    ],
    "TRAVEL LOGISTICS": [
        "airport", "transfer", "taxi", "grab", "gojek", "transport",
        "visa", "currency", "money", "atm", "exchange", "rupiah",
        "weather", "rainy season", "best time", "when to visit", "flight",
        "scooter", "motorbike", "drive", "license", "sim card", "internet",
        "electricity", "plug", "voltage",
    ],
    "FAMILY & GROUP": [
        "family", "kid", "child", "children", "toddler", "baby", "group",
        "friends", "wedding", "hen", "bachelor", "large group", "how many",
        "stroller", "pram", "school", "teenager",
    ],
}


def classify_question(question: str) -> str:
    q_lower = question.lower()
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, signals in CATEGORY_SIGNALS.items():
        for signal in signals:
            if signal in q_lower:
                scores[cat] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "ACTIVITIES & EXPERIENCES"  # default fallback
    return best


# ── PAA extraction helpers ────────────────────────────────────────────────────

def extract_paa_from_result(api_response: dict) -> list[dict]:
    """Walk the DataForSEO SERP response and pull out all people_also_ask blocks."""
    paa_items = []
    try:
        tasks = api_response.get("tasks", [])
        for task in tasks:
            result_list = task.get("result", []) or []
            for result in result_list:
                items = result.get("items", []) or []
                for item in items:
                    if item.get("type") == "people_also_ask":
                        for paa in item.get("items", []) or []:
                            question = paa.get("title", "").strip()
                            if not question:
                                continue
                            paa_items.append({
                                "question": question,
                                "title":    paa.get("title", ""),
                                "url":      paa.get("url", ""),
                                "snippet":  paa.get("description", "") or paa.get("snippet", ""),
                            })
    except Exception as e:
        print(f"  [WARN] Error parsing response: {e}")
    return paa_items


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    client = DataForSEOQuery(LOGIN, PASSWORD)

    # question_text -> {count, appearances (list of {keyword, location, url, snippet, title})}
    question_index: dict[str, dict] = {}
    raw_serp_data = {}  # store all raw API responses for the JSON output

    total_queries = len(ALL_KEYWORDS) * len(LOCATIONS)
    completed = 0

    print(f"\nRunning {total_queries} SERP queries ({len(ALL_KEYWORDS)} keywords x {len(LOCATIONS)} locations)...\n")

    for keyword, group in ALL_KEYWORDS:
        for loc_name, loc_code in LOCATIONS.items():
            completed += 1
            print(f"[{completed}/{total_queries}] {loc_name} | {keyword}")

            try:
                response = client.serp_google_organic(keyword, loc_code)
            except Exception as e:
                print(f"  [ERROR] API call failed: {e}")
                continue

            # Store raw response
            key = f"{keyword}::{loc_name}"
            raw_serp_data[key] = response

            paa_items = extract_paa_from_result(response)
            print(f"  -> {len(paa_items)} PAA items found")

            for item in paa_items:
                q = item["question"]
                # Normalise key: lowercase, strip trailing punctuation
                q_key = q.lower().rstrip("?").strip()

                if q_key not in question_index:
                    question_index[q_key] = {
                        "question":    q,
                        "count":       0,
                        "category":    classify_question(q),
                        "appearances": [],
                    }
                question_index[q_key]["count"] += 1
                question_index[q_key]["appearances"].append({
                    "keyword":  keyword,
                    "group":    group,
                    "location": loc_name,
                    "title":    item["title"],
                    "url":      item["url"],
                    "snippet":  item["snippet"],
                })

            # Polite delay to avoid rate-limiting
            time.sleep(0.5)

    # ── Build output structure ────────────────────────────────────────────────

    unique_questions = list(question_index.values())
    unique_questions.sort(key=lambda x: x["count"], reverse=True)

    by_category: dict[str, list] = defaultdict(list)
    for q in unique_questions:
        by_category[q["category"]].append(q)

    # Sort within each category by frequency
    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["count"], reverse=True)

    output = {
        "meta": {
            "total_unique_questions": len(unique_questions),
            "total_queries_run":      total_queries,
            "keywords_queried":       [kw for kw, _ in ALL_KEYWORDS],
            "locations":              list(LOCATIONS.keys()),
        },
        "questions_by_category": {cat: by_category[cat] for cat in CATEGORIES},
        "all_questions_by_frequency": unique_questions,
        "raw_serp_data": raw_serp_data,
    }

    out_path = "/Users/classicgrassick/Desktop/Claude/lumina-villa/paa_research.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] {out_path}")

    # ── Stdout report ─────────────────────────────────────────────────────────

    print(f"\n{'='*70}")
    print(f"TOTAL UNIQUE PAA QUESTIONS: {len(unique_questions)}")
    print(f"{'='*70}")

    for cat in CATEGORIES:
        questions = by_category.get(cat, [])
        if not questions:
            continue
        print(f"\n{'─'*70}")
        print(f"  {cat}  ({len(questions)} questions)")
        print(f"{'─'*70}")
        for q in questions:
            priority = "  *** HIGH PRIORITY — answer on site ***" if q["count"] >= 3 else ""
            print(f"  [{q['count']:2d}x]  {q['question']}{priority}")

    high_priority = [q for q in unique_questions if q["count"] >= 3]
    print(f"\n{'='*70}")
    print(f"HIGH PRIORITY QUESTIONS (3+ SERPs): {len(high_priority)}")
    print(f"{'='*70}")
    for q in high_priority:
        print(f"  [{q['count']:2d}x]  [{q['category']}]  {q['question']}")

    print()


if __name__ == "__main__":
    main()
