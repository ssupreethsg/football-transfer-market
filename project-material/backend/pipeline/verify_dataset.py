"""Verify the built dataset.

1. Cross-check league appearances / goals / assists against Understat (an independent source)
   for every top-5 league season we have detailed data for.
2. Internal checks: season totals equal the sum of their competitions, detailed stats agree
   with the headline numbers, no negative values, every player file is present.

Writes verification_report.json and prints a summary. Exit code 1 if a hard check fails.
"""

import difflib
import json
import os
import re
import sys
import time
import unicodedata
from collections import defaultdict

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "understat")
DATA = os.path.abspath(os.path.join(HERE, "..", "..", "frontend", "public", "data"))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

# FotMob league id -> Understat league slug
UNDERSTAT = {47: "EPL", 87: "La_liga", 55: "Serie_A", 54: "Bundesliga", 53: "Ligue_1"}
SEASONS = ["2023/2024", "2024/2025", "2025/2026"]  # completed seasons


def fold(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s).split()


def understat(slug, start_year):
    path = os.path.join(CACHE, f"{slug}_{start_year}.json")
    if not os.path.exists(path):
        r = requests.get(f"https://understat.com/getLeagueData/{slug}/{start_year}",
                         headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest"}, timeout=60)
        r.raise_for_status()
        os.makedirs(CACHE, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(r.json()["players"], f)
        time.sleep(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def team_score(teams, understat_team):
    """How well any of our club names matches Understat's team field ("A,B" after a transfer)."""
    best = 0.0
    for ut in understat_team.split(","):
        for t in teams:
            a, b = " ".join(fold(t)), " ".join(fold(ut))
            best = max(best, 1.0 if a and (a in b or b in a) else difflib.SequenceMatcher(None, a, b).ratio())
    return best


def best_match(name, candidates, teams):
    """candidates: list of (tokens, row). Same name AND same club first, then fuzzy name within the club."""
    toks = set(fold(name))
    exact = [row for ct, row in candidates if set(ct) == toks and team_score(teams, row["team_title"]) >= 0.6]
    if exact:
        return exact[0], 1.0
    candidates = [(ct, row) for ct, row in candidates if team_score(teams, row["team_title"]) >= 0.6]
    # surname + something
    best, score = None, 0.0
    for ct, row in candidates:
        s = difflib.SequenceMatcher(None, " ".join(sorted(toks)), " ".join(sorted(ct))).ratio()
        if toks & set(ct) and s > score:
            best, score = row, s
    return (best, score) if score >= 0.8 else (None, score)


def main():
    with open(os.path.join(DATA, "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    players = {}
    for row in index:
        with open(os.path.join(DATA, "players", f"{row['id']}.json"), encoding="utf-8") as f:
            players[row["id"]] = json.load(f)

    hard_errors, internal = [], defaultdict(int)
    # ---- internal checks
    for p in players.values():
        for s in p["seasons"]:
            for k in ("appearances", "goals", "assists"):
                vals = [c[k] for c in s["competitions"] if c[k] is not None]
                if vals and s["totals"][k] != sum(vals):
                    hard_errors.append(f"{p['name']} {s['season']} {k}: total {s['totals'][k]} != sum {sum(vals)}")
            for c in s["competitions"]:
                for k in ("appearances", "goals", "assists"):
                    if c[k] is not None and c[k] < 0:
                        hard_errors.append(f"{p['name']} {s['season']} {c['competition']} negative {k}")
                d = c["detailed"]
                if d:
                    internal["detailed_entries"] += 1
                    # the two FotMob endpoints should agree on goals and assists
                    for k in ("goals", "assists"):
                        if c[k] is not None and d.get(k) is not None and c[k] != d[k]:
                            internal[f"detail_vs_career_{k}_differs"] += 1

    # ---- Understat cross-check
    compared = matched = 0
    diffs = []
    per_field = defaultdict(lambda: [0, 0])  # field -> [equal, compared]
    for lid, slug in UNDERSTAT.items():
        for season in SEASONS:
            us = understat(slug, int(season[:4]))
            cands = [(fold(u["player_name"]), u) for u in us]
            # FotMob totals for this league season, summed across clubs (mid-season transfers)
            for p in players.values():
                s = next((x for x in p["seasons"] if x["season"] == season), None)
                if not s:
                    continue
                comps = [c for c in s["competitions"] if c["competition_id"] == lid]
                if not comps:
                    continue
                apps = sum(c["appearances"] or 0 for c in comps)
                if apps == 0:
                    continue
                compared += 1
                u, score = best_match(p["name"], cands, [c["team"] for c in comps])
                if not u:
                    continue
                matched += 1
                ours = {"appearances": apps, "goals": sum(c["goals"] or 0 for c in comps),
                        "assists": sum(c["assists"] or 0 for c in comps)}
                theirs = {"appearances": int(u["games"]), "goals": int(u["goals"]), "assists": int(u["assists"])}
                bad = {}
                for k in ours:
                    per_field[k][1] += 1
                    if ours[k] == theirs[k]:
                        per_field[k][0] += 1
                    else:
                        bad[k] = (ours[k], theirs[k])
                if bad:
                    diffs.append({"player": p["name"], "id": p["id"], "league": slug, "season": season,
                                  "fotmob_vs_understat": bad})

    report = {
        "players": len(players),
        "internal": dict(internal),
        "hard_errors": hard_errors[:200],
        "hard_error_count": len(hard_errors),
        "understat": {
            "league_seasons_compared": compared, "matched_by_name": matched,
            "agreement": {k: f"{e}/{n} ({100 * e / n:.1f}%)" for k, (e, n) in per_field.items() if n},
            "differences": diffs,
        },
    }
    out = os.path.join(HERE, "verification_report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    print(f"players: {len(players)}")
    print(f"internal: {dict(internal)}  hard errors: {len(hard_errors)}")
    for e in hard_errors[:10]:
        print("  !", e)
    print(f"understat: {compared} player-league-seasons, {matched} matched by name")
    for k, v in report["understat"]["agreement"].items():
        print(f"  {k:12} agree {v}")
    print(f"report -> {out}")
    return 1 if hard_errors else 0


if __name__ == "__main__":
    sys.exit(main())
