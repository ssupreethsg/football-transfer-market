"""Turn the cached FotMob data into the website's static dataset.

Writes:
  <out>/index.json            one compact row per player (for the list, search, filters)
  <out>/players/<id>.json     full player file: career split by season AND competition,
                              plus cumulative totals split by competition
  <out>/meta.json             build info and coverage counts

Rules:
  - Numbers are copied from the source. Nothing is estimated or projected.
  - A value the source does not have stays null (shown as "-" on the site), never 0.
  - Friendlies are excluded from all totals.
"""

import argparse
import glob
import json
import os
import re
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("FOTMOB_CACHE", os.path.join(HERE, "cache"))
DEFAULT_OUT = os.path.abspath(os.path.join(HERE, "..", "..", "frontend", "public", "data"))

# FotMob localizedTitleId -> our field name. Counting stats are summed in totals;
# RATE_FIELDS are averaged by minutes instead.
DEEP_FIELDS = {
    "minutes_played": "minutes", "matches_uppercase": "matches", "player_started_matches": "started",
    "rating": "rating", "goals": "goals", "assists": "assists",
    "goals_subtitle": "penalty_goals", "expected_goals": "xg", "non_penalty_xg": "npxg",
    "expected_goals_on_target": "xgot", "shots": "shots", "ShotsOnTarget": "shots_on_target",
    "headed_shots": "headed_shots", "expected_assists": "xa", "chances_created": "chances_created",
    "big_chance_created_team_title": "big_chances_created", "successful_passes": "accurate_passes",
    "successful_passes_accuracy": "pass_accuracy", "long_balls_accurate": "accurate_long_balls",
    "long_ball_succeeeded_accuracy": "long_ball_accuracy", "crosses_succeeeded": "accurate_crosses",
    "crosses_succeeeded_accuracy": "cross_accuracy", "line_breaking_passes": "line_breaking_passes",
    "dribbles_succeeded": "dribbles", "won_contest_subtitle": "dribble_success_rate",
    "touches": "touches", "touches_opp_box": "touches_opp_box", "duel_won": "duels_won",
    "duel_won_percent": "duels_won_pct", "aerials_won": "aerials_won", "aerials_won_percent": "aerials_won_pct",
    "dispossessed": "dispossessed", "fouls_won": "fouls_won", "penalty_won_title": "penalties_won",
    "matchstats.headers.tackles": "tackles", "interceptions": "interceptions", "clearances": "clearances",
    "blocked_shots": "blocks", "recoveries": "recoveries", "dribbled_past": "dribbled_past",
    "defensive_actions": "defensive_actions", "poss_won_att_3rd_team_title": "possession_won_final_third",
    "fouls": "fouls_committed", "yellow_cards": "yellow_cards", "red_cards": "red_cards",
    "clean_sheet_team_title": "clean_sheets", "goals_conceded_while_on_pitch": "goals_conceded",
    "expected_goals_against_while_on_pitch": "xg_against",
    # goalkeeping
    "saves": "saves", "save_percentage": "save_pct", "goals_prevented": "goals_prevented",
    "keeper_high_claim": "high_claims", "keeper_sweeper": "sweeper_actions",
    "penalties_saved": "penalties_saved", "error_led_to_goal": "errors_led_to_goal",
}
RATE_FIELDS = {"rating", "pass_accuracy", "long_ball_accuracy", "cross_accuracy",
               "dribble_success_rate", "duels_won_pct", "aerials_won_pct", "save_pct"}
FLOAT_FIELDS = RATE_FIELDS | {"xg", "npxg", "xgot", "xa", "xg_against", "goals_prevented"}

CONTINENTAL = re.compile(r"champions league|europa|conference league|uefa super cup|club world cup|"
                         r"libertadores|sudamericana|afc champions|caf champions|concacaf champions", re.I)
DOMESTIC_CUP = re.compile(r"\bcup\b|copa|coppa|pokal|coupe|shield|supercopa|supercoppa|supercup|"
                          r"super cup|trophée|trophy|taça|beker|play-?off|mesterskap|pokalen|cupen", re.I)


def load_league_names():
    """{leagueId: (country, display name)}; the country is appended when a name is used by several countries."""
    path = os.path.join(CACHE, "all_leagues.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    rows = []
    for group in d.get("international", []):
        rows += [(l["id"], l["name"], None) for l in group.get("leagues", [])]
    for c in d.get("countries", []):
        rows += [(l["id"], l["name"], c["name"]) for l in c.get("leagues", [])]
    name_count = defaultdict(int)
    for _, name, _ in rows:
        name_count[name] += 1
    generic = re.compile(r"^(super |league )?cup$|^supercup$|^super league$|^first division$|^pokal$", re.I)
    return {lid: (country, f"{name} ({country})" if country and (name_count[name] > 1 or generic.match(name)) else name)
            for lid, name, country in rows}


LEAGUE_NAMES = load_league_names()


def num(v, as_float=False):
    """Parse a FotMob value. Missing / 'undefined' -> None (unknown), never 0."""
    if v is None or v == "" or v == "undefined":
        return None
    try:
        f = float(str(v).replace(",", "").replace("%", ""))
    except ValueError:
        return None
    return f if as_float else int(round(f))


def comp_type(name, national):
    if national:
        return "international"
    if CONTINENTAL.search(name):
        return "continental"
    if DOMESTIC_CUP.search(name):
        return "domestic_cup"
    return "league"


def season_sort_key(s):
    m = re.match(r"(\d{4})(?:/(\d{4}))?", s or "")
    if not m:
        return (0, 0)
    start = int(m.group(1))
    # a calendar-year season like "2026" is played in the spring/summer of that year
    return (start if m.group(2) else start - 1, 1 if m.group(2) else 0)


def read_deep(pid):
    """{(statSeasonName, tournamentId): {field: value}}"""
    out = {}
    for f in glob.glob(os.path.join(CACHE, "deep", str(pid), "*.json")):
        season_part, tid = os.path.basename(f)[:-5].rsplit("_", 1)
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        stats = {}
        items = list((d.get("topStatCard") or {}).get("items", []))
        for g in (d.get("statsSection") or {}).get("items", []):
            items.extend(g.get("items", []))
        for it in items:
            key = DEEP_FIELDS.get(it.get("localizedTitleId"))
            if key and key not in stats:
                stats[key] = num(it.get("statValue"), key in FLOAT_FIELDS)
        out[(season_part.replace("-", "/"), int(tid))] = stats
    return out


def add_into(total, stats, weight_minutes):
    for k, v in stats.items():
        if v is None:
            continue
        if k in RATE_FIELDS:
            w = weight_minutes or 0
            if w:
                total.setdefault("_w", {}).setdefault(k, [0.0, 0])
                total["_w"][k][0] += v * w
                total["_w"][k][1] += w
        else:
            total[k] = (total.get(k) or 0) + v


def finish(total):
    w = total.pop("_w", {})
    for k, (s, n) in w.items():
        total[k] = round(s / n, 2) if n else None
    for k in list(total):
        if isinstance(total[k], float) and k not in RATE_FIELDS:
            total[k] = round(total[k], 2)
    return total


def basic(ts):
    return {"appearances": num(ts.get("appearances")), "goals": num(ts.get("goals")),
            "assists": num(ts.get("assists")), "rating": num((ts.get("rating") or {}).get("rating"), True)}


def merge_basic(total, b):
    """Sum the known values; remember which fields had an unknown part ("incomplete")."""
    unknown = total.setdefault("_unknown", set())
    unknown.update(b.get("incomplete") or [])
    for k in ("appearances", "goals", "assists"):
        if b.get(k) is not None:
            total[k] = (total.get(k) or 0) + b[k]
        else:
            total.setdefault(k, None)
            unknown.add(k)


def close_basic(total):
    unknown = total.pop("_unknown", set())
    out = {k: total.get(k) for k in ("appearances", "goals", "assists")}
    out["incomplete"] = sorted(unknown)
    return out


def build_player(prof, deep, squad_info):
    ch = (prof.get("careerHistory") or {}).get("careerItems") or {}
    seasons = OrderedDict()   # season -> {teams, competitions}
    deep_used = set()
    # which FotMob stat season lists each tournament, so calendar-year entries land in the same season
    stat_season_of = defaultdict(set)
    for ss in prof.get("statSeasons") or []:
        for t in ss.get("tournaments", []):
            stat_season_of[t.get("tournamentId")].add(ss.get("seasonName"))

    def collect(section, national):
        for se in (ch.get(section) or {}).get("seasonEntries", []) or []:
            sname = se.get("seasonName")
            bucket = sname
            span = re.fullmatch(r"(\d{4})/(\d{4})", sname or "")
            if span and int(span.group(2)) - int(span.group(1)) > 1:
                # FotMob labels some national-team editions over two years (Nations League 2024/25 -> "2024/2026");
                # they are played inside the first club season.
                y = int(span.group(1))
                bucket = f"{y}/{y + 1}"
            elif re.fullmatch(r"\d{4}", sname or "") and national:
                y = int(sname)
                lids = {ts.get("leagueId") for ts in se.get("tournamentStats", []) or []}
                later = f"{y}/{y + 1}"
                # follow FotMob's grouping when it files this tournament under the next season
                bucket = later if any(later in stat_season_of.get(l, ()) for l in lids) else f"{y - 1}/{y}"
            s = seasons.setdefault(bucket, {"season": bucket, "teams": [], "competitions": []})
            team = se.get("team")
            if team and team not in s["teams"]:
                s["teams"].append(team)
            for ts in se.get("tournamentStats", []) or []:
                if ts.get("isFriendly"):
                    continue
                b = basic(ts)
                lid = ts.get("leagueId")
                d = deep.get((bucket, lid)) or deep.get((sname, lid))
                if d is not None:
                    deep_used.add((bucket, lid))
                country, display = LEAGUE_NAMES.get(lid, (None, ts.get("leagueName")))
                comp = OrderedDict(
                    competition=display, competition_id=lid, country=country,
                    type=comp_type(ts.get("leagueName") or "", national),
                    team=team, edition=ts.get("seasonName"),
                    appearances=b["appearances"], goals=b["goals"], assists=b["assists"], rating=b["rating"],
                    detailed=d,
                )
                s["competitions"].append(comp)

    collect("senior", False)
    collect("national team", True)

    season_list = []
    career_by_comp = OrderedDict()
    career_total, career_detail = {}, {}
    detail_seasons = set()
    for s in sorted(seasons.values(), key=lambda x: season_sort_key(x["season"]), reverse=True):
        if not s["competitions"]:
            continue
        tot, det = {}, {}
        for c in s["competitions"]:
            merge_basic(tot, c)
            if c["detailed"]:
                add_into(det, c["detailed"], c["detailed"].get("minutes"))
            key = (c["competition_id"], c["type"])
            agg = career_by_comp.setdefault(key, {"competition": c["competition"], "competition_id": c["competition_id"],
                                                  "type": c["type"], "seasons": 0, "basic": {}, "detail": {}})
            agg["seasons"] += 1
            merge_basic(agg["basic"], c)
            if c["detailed"]:
                add_into(agg["detail"], c["detailed"], c["detailed"].get("minutes"))
        s["totals"] = close_basic(tot)
        s["totals_detailed"] = finish(det) if det else None
        if det:
            detail_seasons.add(s["season"])
        merge_basic(career_total, s["totals"])
        if s["totals_detailed"]:
            add_into(career_detail, s["totals_detailed"], s["totals_detailed"].get("minutes"))
        season_list.append(s)

    by_comp = []
    for agg in career_by_comp.values():
        by_comp.append(OrderedDict(
            competition=agg["competition"], competition_id=agg["competition_id"], type=agg["type"],
            seasons=agg["seasons"], **close_basic(agg["basic"]),
            detailed=finish(agg["detail"]) if agg["detail"] else None,
        ))
    by_comp.sort(key=lambda c: (["league", "domestic_cup", "continental", "international"].index(c["type"]),
                                -(c["appearances"] or 0)))
    info = {i.get("title"): i.get("value") for i in prof.get("playerInformation") or []}
    mv = None
    vals = (prof.get("marketValues") or {}).get("values") or []
    if vals:
        mv = {"value_eur": vals[-1].get("value"), "date": vals[-1].get("date", "")[:10], "source": vals[-1].get("source")}
    contract = (prof.get("contractEnd") or {}).get("utcTime")
    primary = prof.get("primaryTeam") or {}
    pos = (prof.get("positionDescription") or {}).get("primaryPosition") or {}
    birth = (prof.get("birthDate") or {}).get("utcTime")

    return OrderedDict(
        id=prof["id"], name=prof.get("name"),
        team=squad_info.get("club") or primary.get("teamName"), team_id=squad_info.get("club_id") or primary.get("teamId"),
        league=squad_info.get("league"), on_loan=primary.get("onLoan"),
        position=pos.get("label") or squad_info.get("group"), position_group=squad_info.get("group"),
        nationality=(info.get("Country") or {}).get("fallback") if isinstance(info.get("Country"), dict) else None,
        birth_date=birth[:10] if birth else None,
        age=num((info.get("Age") or {}).get("fallback")) if isinstance(info.get("Age"), dict) else None,
        height_cm=num(str((info.get("Height") or {}).get("fallback", "")).replace("cm", "")) if isinstance(info.get("Height"), dict) else None,
        preferred_foot=(info.get("Preferred foot") or {}).get("fallback") if isinstance(info.get("Preferred foot"), dict) else None,
        contract_end=contract[:10] if contract else None,
        market_value=mv,
        career_totals={**close_basic(career_total),
                       "detailed": finish(career_detail) if career_detail else None,
                       "detailed_seasons": sorted(detail_seasons, key=season_sort_key, reverse=True)},
        career_by_competition=by_comp,
        seasons=season_list,
        source={"provider": "FotMob (data: Opta / Stats Perform)", "url": f"https://www.fotmob.com/players/{prof['id']}"},
    )


def index_row(p, current):
    cur = next((s for s in p["seasons"] if s["season"] == current), None)
    last = next((s for s in p["seasons"] if season_sort_key(s["season"]) < season_sort_key(current)
                 and "/" in s["season"]), None)
    pick = lambda s: {k: s["totals"].get(k) for k in ("appearances", "goals", "assists")} | {
        "minutes": (s["totals_detailed"] or {}).get("minutes")} if s else None
    return OrderedDict(
        id=p["id"], name=p["name"], team=p["team"], team_id=p["team_id"], league=p["league"],
        position=p["position"], position_group=p["position_group"], nationality=p["nationality"], age=p["age"],
        market_value_eur=(p["market_value"] or {}).get("value_eur"),
        current_season=pick(cur), last_season=pick(last), last_season_name=last["season"] if last else None,
        career={k: p["career_totals"].get(k) for k in ("appearances", "goals", "assists")},
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--player", type=int, action="append", default=[])
    a = ap.parse_args()

    with open(os.path.join(CACHE, "squads.json"), encoding="utf-8") as f:
        squads = json.load(f)
    roster, current = {}, None
    for lname, l in squads.items():
        current = current or l["season"]
        for c in l["clubs"]:
            for p in c["players"]:
                roster[p["id"]] = {"league": lname, "club": c["name"], "club_id": c["id"], "group": p["group"]}

    ids = a.player or sorted(roster)
    os.makedirs(os.path.join(a.out, "players"), exist_ok=True)
    rows, missing = [], []
    for pid in ids:
        path = os.path.join(CACHE, "players", f"{pid}.json")
        if not os.path.exists(path):
            missing.append(pid)
            continue
        with open(path, encoding="utf-8") as f:
            prof = json.load(f)
        p = build_player(prof, read_deep(pid), roster.get(pid, {}))
        with open(os.path.join(a.out, "players", f"{pid}.json"), "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, separators=(",", ":"))
        rows.append(index_row(p, current))

    if not a.player:
        rows.sort(key=lambda r: -(r["market_value_eur"] or 0))
        with open(os.path.join(a.out, "index.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
        meta = {"built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "current_season": current,
                "players": len(rows), "missing_profiles": len(missing),
                "clubs": sum(len(l["clubs"]) for l in squads.values()),
                "leagues": {k: len(v["clubs"]) for k, v in squads.items()},
                "source": "FotMob (Opta / Stats Perform); league goals and assists cross-checked with Understat"}
        with open(os.path.join(a.out, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
    print(f"built {len(rows)} players, {len(missing)} without a profile -> {a.out}")


if __name__ == "__main__":
    main()
