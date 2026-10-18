import sqlite3

conn = sqlite3.connect("sql_app.db")
c = conn.cursor()

print("ALL TEAMS AND PLAYER COUNTS BY LEAGUE:")
for league in ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]:
    print(f"\n--- {league.upper()} ---")
    c.execute("SELECT team, count(*) FROM players WHERE league = ? GROUP BY team ORDER BY team", (league,))
    rows = c.fetchall()
    print(f"Total clubs: {len(rows)}")
    for t, cnt in rows:
        flag = " [UNDERPOPULATED!]" if cnt < 15 else ""
        print(f"  {t:30} : {cnt:2d} players{flag}")
