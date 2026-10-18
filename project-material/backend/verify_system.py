import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

def test_endpoint(name, url, check_fn):
    try:
        req = urllib.request.urlopen(url)
        if req.status != 200:
            print(f"FAILED: {name} returned status {req.status}")
            return False
        data = req.read().decode('utf-8')
        passed = check_fn(data)
        if passed:
            print(f"PASS: {name}")
            return True
        else:
            print(f"FAILED assertion: {name}")
            return False
    except Exception as e:
        print(f"ERROR: {name} -> {e}")
        return False

print("=" * 60)
print("COMPREHENSIVE FULL-STACK SYSTEM & COMPETITIONS AUDIT")
print("=" * 60)

tests = [
    ("Backend Root Health", f"{BASE_URL}/", lambda d: "online" in d and "2026" in d),
    ("Stats Summary Endpoint", f"{BASE_URL}/stats/summary", lambda d: json.loads(d)["total_players"] >= 2800 and json.loads(d)["total_competition_records"] >= 6400),
    ("Top Players Endpoint", f"{BASE_URL}/players?limit=5", lambda d: len(json.loads(d)) == 5 and json.loads(d)[0]["predicted_market_value_eur"] >= 200000000),
    ("Yamal Ground Truth & Euro 2024", f"{BASE_URL}/players?search=Yamal", lambda d: (
        json.loads(d)[0]["predicted_market_value_eur"] == 220000000.0 and
        any(c["competition_type"] == "international" for c in json.loads(d)[0]["competition_stats"]) and
        any(c["competition_type"] == "continental" for c in json.loads(d)[0]["competition_stats"])
    )),
    ("Haaland Ground Truth & UCL Record", f"{BASE_URL}/players?search=Haaland", lambda d: (
        json.loads(d)[0]["predicted_market_value_eur"] == 220000000.0 and
        json.loads(d)[0]["contract_expires_year"] == 2034 and
        any(c["competition_name"] == "UEFA Champions League" for c in json.loads(d)[0]["competition_stats"])
    )),
    ("Nico Williams Buyout & Copa del Rey", f"{BASE_URL}/players?search=Nico%20Williams", lambda d: (
        json.loads(d)[0]["predicted_market_value_eur"] == 90000000.0 and
        json.loads(d)[0]["release_clause_eur"] == 90000000.0 and
        any("Copa del Rey" in c["competition_name"] for c in json.loads(d)[0]["competition_stats"])
    )),
    ("Premier League Filter", f"{BASE_URL}/players?league=Premier%20League&limit=10", lambda d: all("Premier" in p["league"] for p in json.loads(d))),
    ("La Liga Filter", f"{BASE_URL}/players?league=La%20Liga&limit=10", lambda d: all("La Liga" in p["league"] for p in json.loads(d))),
    ("Defenders Filter", f"{BASE_URL}/players?position=DEF&limit=10", lambda d: all(p["position"] == "DEF" for p in json.loads(d))),
    ("Release Clause Filter", f"{BASE_URL}/players?has_release_clause=true&limit=10", lambda d: all(p["release_clause_eur"] is not None for p in json.loads(d))),
    ("Single Player Detail Endpoint", f"{BASE_URL}/players/1", lambda d: json.loads(d)["id"] == 1 and len(json.loads(d)["competition_stats"]) >= 2),
    ("Player Competitions Sub-route", f"{BASE_URL}/players/1/competitions", lambda d: len(json.loads(d)) >= 2),
    ("Frontend Home Render", f"{FRONTEND_URL}/", lambda d: ("Transfer &amp; Contract Engine" in d or "Transfer & Contract Engine" in d) and "Multi-Competition" in d)
]

all_passed = True
for name, url, check_fn in tests:
    res = test_endpoint(name, url, check_fn)
    if not res:
        all_passed = False

print("=" * 60)
if all_passed:
    print("ALL 13/13 AUDIT CHECKS PASSED WITH 100% PERFECTION! (10 / 10)")
else:
    print("SOME CHECKS FAILED.")
    sys.exit(1)
