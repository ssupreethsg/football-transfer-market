"""Collect real player data for every club in the top 5 European leagues.

Source: FotMob's public data API (match data provided by Opta / Stats Perform).
Every response is cached on disk, so the run can be stopped and resumed safely.

Stages:
  squads   league tables -> club squads (current season)
  profiles one profile per player: bio + full career split by season and competition
  deep     detailed stats (minutes, shots, dribbles, ...) per season and competition

Usage:
  python scrape_fotmob.py squads
  python scrape_fotmob.py profiles
  python scrape_fotmob.py deep --seasons 4
"""

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE = "https://www.fotmob.com/api/data"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("FOTMOB_CACHE", os.path.join(HERE, "cache"))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

# FotMob league ids for the top 5 leagues
LEAGUES = {47: "Premier League", 87: "La Liga", 55: "Serie A", 54: "Bundesliga", 53: "Ligue 1"}

_session = threading.local()
_rate_lock = threading.Lock()
_last_call = [0.0]
MIN_INTERVAL = float(os.environ.get("FOTMOB_MIN_INTERVAL", "0.35"))  # seconds between requests, all threads


def _http():
    if not hasattr(_session, "s"):
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept": "application/json"})
        _session.s = s
    return _session.s


def fetch(path, params, cache_file, trim=None):
    """GET BASE/path with params, cached as JSON at cache_file. Returns parsed JSON or None."""
    if os.path.exists(cache_file):
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)
    for attempt in range(5):
        with _rate_lock:
            wait = _last_call[0] + MIN_INTERVAL - time.time()
            if wait > 0:
                time.sleep(wait)
            _last_call[0] = time.time()
        try:
            r = _http().get(f"{BASE}/{path}", params=params, timeout=30)
        except requests.RequestException:
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 200:
            data = r.json()
            if trim:
                data = trim(data)
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            tmp = cache_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp, cache_file)
            return data
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(5 * (attempt + 1))
            continue
        return None  # 404 etc.: nothing to fetch
    return None


# ---------- trimming: keep only what the pipeline uses ----------

def trim_team(d):
    return {"details": d.get("details"), "squad": d.get("squad")}


def trim_profile(d):
    keep = ["id", "name", "birthDate", "contractEnd", "primaryTeam", "positionDescription",
            "playerInformation", "mainLeague", "careerHistory", "statSeasons", "marketValues",
            "injuryInformation", "dataProvider"]
    return {k: d.get(k) for k in keep}


def trim_deep(d):
    return {"statsSection": d.get("statsSection"), "topStatCard": d.get("topStatCard")}


# ---------- stages ----------

def stage_squads():
    # league -> country list, used to label competitions like "Bundesliga (Austria)"
    fetch("allLeagues", {}, os.path.join(CACHE, "all_leagues.json"))
    out = {}
    for lid, lname in LEAGUES.items():
        league = fetch("leagues", {"id": lid}, os.path.join(CACHE, "leagues", f"{lid}.json"),
                       trim=lambda d: {"details": d.get("details"), "table": d.get("table")})
        table = league["table"][0]["data"]["table"]["all"]
        season = league["details"].get("selectedSeason")
        clubs = []
        for row in table:
            team = fetch("teams", {"id": row["id"]}, os.path.join(CACHE, "teams", f"{row['id']}.json"), trim=trim_team)
            players = []
            for group in team["squad"]["squad"]:
                if group.get("title") == "coach":
                    continue
                for m in group.get("members", []):
                    players.append({"id": m["id"], "name": m["name"], "group": group.get("title")})
            clubs.append({"id": row["id"], "name": row["name"], "players": players})
            print(f"  {lname}: {row['name']} ({len(players)} players)", flush=True)
        out[lname] = {"league_id": lid, "season": season, "clubs": clubs}
    path = os.path.join(CACHE, "squads.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    total = sum(len(c["players"]) for l in out.values() for c in l["clubs"])
    print(f"squads: {sum(len(l['clubs']) for l in out.values())} clubs, {total} players -> {path}")


ONLY_PLAYERS = []  # set from --player to restrict a stage to specific ids


def _player_ids():
    if ONLY_PLAYERS:
        return ONLY_PLAYERS
    with open(os.path.join(CACHE, "squads.json"), encoding="utf-8") as f:
        squads = json.load(f)
    ids = []
    for l in squads.values():
        for c in l["clubs"]:
            ids.extend(p["id"] for p in c["players"])
    return sorted(set(ids))


def _run_parallel(jobs, workers, label):
    done = failed = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(fn) for fn in jobs]
        for f in as_completed(futs):
            if f.result() is None:
                failed += 1
            done += 1
            if done % 200 == 0 or done == len(jobs):
                print(f"  {label}: {done}/{len(jobs)} (missing {failed})", flush=True)
    return failed


def stage_profiles(workers):
    ids = _player_ids()
    jobs = [lambda pid=pid: fetch("playerData", {"id": pid}, os.path.join(CACHE, "players", f"{pid}.json"),
                                  trim=trim_profile) for pid in ids]
    _run_parallel(jobs, workers, "profiles")


def stage_deep(workers, seasons):
    jobs = []
    for pid in _player_ids():
        path = os.path.join(CACHE, "players", f"{pid}.json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            prof = json.load(f)
        for s in (prof.get("statSeasons") or [])[:seasons]:
            for t in s.get("tournaments", []):
                if not t.get("hasDeepStats"):
                    continue
                key = f"{s['seasonName'].replace('/', '-')}_{t['tournamentId']}"
                jobs.append(lambda pid=pid, e=t["entryId"], key=key: fetch(
                    "playerStats", {"playerId": pid, "seasonId": e, "isFirstSeason": "false"},
                    os.path.join(CACHE, "deep", str(pid), f"{key}.json"), trim=trim_deep))
    print(f"deep: {len(jobs)} season/competition entries")
    _run_parallel(jobs, workers, "deep")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["squads", "profiles", "deep"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seasons", type=int, default=4, help="most recent seasons to pull deep stats for")
    ap.add_argument("--player", type=int, action="append", default=[], help="limit to this player id (repeatable)")
    a = ap.parse_args()
    ONLY_PLAYERS.extend(a.player)
    if a.stage == "squads":
        stage_squads()
    elif a.stage == "profiles":
        stage_profiles(a.workers)
    else:
        stage_deep(a.workers, a.seasons)
    sys.exit(0)
