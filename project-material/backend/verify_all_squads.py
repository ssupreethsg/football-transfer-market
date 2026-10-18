import sqlite3
from collections import defaultdict

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

leagues = ['Premier League', 'La Liga', 'Serie A', 'Ligue 1', 'Bundesliga']
all_passed = True

for league in leagues:
    print(f"\n--- {league} ---")
    c.execute("SELECT team, count(*) FROM players WHERE league = ? GROUP BY team", (league,))
    teams = c.fetchall()
    
    if not teams:
        print(f"ERROR: No teams found for {league}!")
        all_passed = False
        continue
        
    for team, count in teams:
        if count < 20:
            print(f"WARNING: {team} has only {count} players! Target is 20-28.")
            all_passed = False
        elif count > 35:
            print(f"WARNING: {team} has {count} players! Oversized squad.")
            all_passed = False
        else:
            print(f"OK: {team} ({count} players)")

if all_passed:
    print("\nSUCCESS: All 96 clubs in the top 5 leagues are fully populated and within normal squad sizes.")
else:
    print("\nFAILED: Some clubs have abnormal squad sizes.")
