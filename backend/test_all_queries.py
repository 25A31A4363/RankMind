import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/v1/intelligence'

queries = [
    'Java tutorials for beginners',
    'coding problem solving websites',
    'best free photography courses',
    'best places to visit in Hyderabad',
    'how to make pizza',
    'best laptops for students under 60000',
    'Indian history',
    'how does solar energy work',
    'best books to learn psychology',
    'C++ tutorials',
    'best tourist places in Kerala',
    'quantum mechanics for children'
]

print("=== 1. VERIFYING 12 GENERAL-PURPOSE QUERIES ===")
for q in queries:
    resp = requests.post(f"{BASE_URL}/search", json={"query": q})
    assert resp.status_code == 200, f"Failed for {q}: {resp.status_code}"
    data = resp.json()
    u = data["query_understanding"]
    results = data["results"]
    insufficient = data.get("insufficient_results", False)
    
    print(f"\nQuery: '{q}'")
    print(f"  Topic: {u['topic']} | Intent: {u['intent']} | Goal: {u['user_goal']} | Type: {u['resource_type_preference']}")
    if u.get('location'):
        print(f"  Location Identified: {u['location']}")
    if u.get('price_constraint'):
        print(f"  Price Constraint: {u['price_constraint']}")
    if u.get('audience_level') and u['audience_level'] != 'General':
        print(f"  Audience: {u['audience_level']}")
    if insufficient:
        print(f"  [OK] Negative filter triggered: '{data['message']}'")
    else:
        print(f"  Found: {len(results)} relevant resources.")
        for r in results[:2]:
            cls = r['classification']
            print(f"    - RankMind #{r['rankmind_position']} (Search #{r['search_position']}): {r['title']} [{cls['resource_type']} - {cls['access_type']}] Score={r['rankmind_score']}/100")
            print(f"      Why: {r['why_this_position']['summary'][:80]}...")
            print(f"      Popularity: {r['factors'].get('popularity_label')} | Freshness: {r['factors'].get('freshness_label')}")
            print(f"      Key Points: {len(r['key_points'])} extracted ({r['key_points_source']})")

print("\n=== 2. VERIFYING HINDSIGHT RETAIN / RECALL LOOP ===")
interact_payload = {
    "query": "Java tutorials",
    "domain": "w3schools.com",
    "url": "https://www.w3schools.com/java/",
    "rankmind_position": 4,
    "interaction_type": "open_website",
    "details": {"rating": 5}
}
i_resp = requests.post(f"{BASE_URL}/interact", json=interact_payload)
print("Retain Response:", json.dumps(i_resp.json(), indent=2))

recall_resp = requests.post(f"{BASE_URL}/search", json={"query": "Java tutorials for beginners"})
recall_data = recall_resp.json()
top_r = [r for r in recall_data["results"] if r["domain"] == "w3schools.com"][0]
print(f"Post-Interaction W3Schools Score: {top_r['rankmind_score']} (RankMind Position #{top_r['rankmind_position']})")
print(f"Hindsight Insight: {top_r.get('hindsight_insight')}")
print(f"Signals: {top_r['why_this_position']['positive_signals']}")
