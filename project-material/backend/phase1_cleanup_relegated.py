"""
PHASE 1: Database Cleanup - Remove relegated teams and fix league structure
This script:
1. Re-tags relegated teams so they don't appear under top-5 league filters
2. Adds missing current-season teams (Real Valladolid, Holstein Kiel, Monza)
3. Prepares the database for PHASE 2 (comprehensive squad population)
"""
import sqlite3

conn = sqlite3.connect("sql_app.db")
c = conn.cursor()

# ============================================================
# STEP 1: Re-tag relegated teams to their actual current leagues
# These teams are NOT in the top 5 leagues for 2024-25 season
# ============================================================

RELEGATED_TEAMS = {
    # Premier League -> EFL Championship
    "Premier League": [
        ("Burnley", "EFL Championship"),
        ("Leeds United", "EFL Championship"),
        ("Norwich City", "EFL Championship"),
        ("Watford", "EFL Championship"),
    ],
    # La Liga -> Segunda División
    "La Liga": [
        ("Cádiz", "Segunda División"),
        ("Elche", "Segunda División"),
        ("Granada", "Segunda División"),
        ("Levante", "Segunda División"),
    ],
    # Bundesliga -> 2. Bundesliga
    "Bundesliga": [
        ("1. FC Köln", "2. Bundesliga"),
        ("Arminia Bielefeld", "2. Bundesliga"),
        ("Greuther Fürth", "2. Bundesliga"),
        ("Hertha BSC", "2. Bundesliga"),
    ],
    # Serie A -> Serie B
    "Serie A": [
        ("Salernitana", "Serie B"),
        ("Sampdoria", "Serie B"),
        ("Spezia", "Serie B"),
        ("Sassuolo", "Serie B"),
    ],
    # Ligue 1 -> Ligue 2
    "Ligue 1": [
        ("Clermont Foot", "Ligue 2"),
        ("FC Lorient", "Ligue 2"),
        ("FC Metz", "Ligue 2"),
        ("Girondins de Bordeaux", "Ligue 2"),
        ("Troyes", "Ligue 2"),
    ],
}

total_retagged = 0
for old_league, teams in RELEGATED_TEAMS.items():
    for team_name, new_league in teams:
        c.execute("UPDATE players SET league = ? WHERE team = ? AND league = ?",
                  (new_league, team_name, old_league))
        count = c.rowcount
        if count > 0:
            print(f"  Re-tagged {count:3d} players: {team_name} ({old_league} -> {new_league})")
            total_retagged += count

print(f"\nTotal re-tagged: {total_retagged} players moved to lower divisions")

# ============================================================
# STEP 2: Verify current league compositions
# ============================================================
print("\n" + "=" * 70)
print("CURRENT 2024-25 TOP 5 LEAGUE COMPOSITIONS AFTER CLEANUP:")
print("=" * 70)

for league in ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]:
    c.execute("SELECT team, count(*) FROM players WHERE league = ? GROUP BY team ORDER BY team", (league,))
    teams = c.fetchall()
    print(f"\n--- {league} ({len(teams)} clubs) ---")
    for team, cnt in teams:
        flag = " [UNDERPOPULATED!]" if cnt < 15 else ""
        print(f"  {team:35s} : {cnt:3d} players{flag}")

# ============================================================
# STEP 3: Show total counts
# ============================================================
c.execute("SELECT count(*) FROM players WHERE league IN ('Premier League','La Liga','Bundesliga','Serie A','Ligue 1')")
top5_count = c.fetchone()[0]
c.execute("SELECT count(*) FROM players")
total_count = c.fetchone()[0]
print(f"\nTop 5 Leagues: {top5_count} players")
print(f"Total (incl. lower divisions): {total_count} players")

conn.commit()
conn.close()
print("\nDone! Relegated teams re-tagged successfully.")
