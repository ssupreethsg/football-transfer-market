import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

print("=" * 80)
print("COMPREHENSIVE DATA AUDIT: TOP 5 EUROPEAN LEAGUES")
print("=" * 80)

# 1. Total players and teams
c.execute("SELECT COUNT(*), COUNT(DISTINCT team) FROM players")
total_players, total_teams = c.fetchone()
print(f"Total Players: {total_players}")
print(f"Total Teams: {total_teams}")

# 2. Teams per League
print("\nTeams & Squad Sizes per League:")
c.execute("""
    SELECT league, COUNT(DISTINCT team), COUNT(*), AVG(predicted_market_value_eur)
    FROM players 
    GROUP BY league 
    ORDER BY COUNT(*) DESC
""")
for l, t_cnt, p_cnt, avg_v in c.fetchall():
    print("  {:<16} : {:>2} teams | {:>4} players (avg {:>2.1f}/team) | Squad Avg: EUR {:>10,.0f}".format(
        l, t_cnt, p_cnt, p_cnt/t_cnt, avg_v
    ))

# 3. Data Integrity & Null Check
c.execute("""
    SELECT 
        SUM(CASE WHEN name IS NULL OR TRIM(name) = '' THEN 1 ELSE 0 END),
        SUM(CASE WHEN age IS NULL OR age < 15 OR age > 45 THEN 1 ELSE 0 END),
        SUM(CASE WHEN position IS NULL OR position NOT IN ('FWD', 'MID', 'DEF', 'GK') THEN 1 ELSE 0 END),
        SUM(CASE WHEN team IS NULL OR TRIM(team) = '' THEN 1 ELSE 0 END),
        SUM(CASE WHEN league IS NULL OR TRIM(league) = '' THEN 1 ELSE 0 END),
        SUM(CASE WHEN minutes_played IS NULL OR minutes_played < 0 THEN 1 ELSE 0 END),
        SUM(CASE WHEN predicted_market_value_eur IS NULL OR predicted_market_value_eur <= 0 THEN 1 ELSE 0 END)
    FROM players
""")
null_res = c.fetchone()
print("\nData Quality Checks across all 2,565 players:")
print(f"  Missing / Empty Names      : {null_res[0]}")
print(f"  Unrealistic / Null Ages    : {null_res[1]}")
print(f"  Invalid / Missing Positions: {null_res[2]}")
print(f"  Missing Teams              : {null_res[3]}")
print(f"  Missing Leagues            : {null_res[4]}")
print(f"  Negative / Null Minutes    : {null_res[5]}")
print(f"  Invalid / Null Market Value: {null_res[6]}")

# 4. List of all 98 Teams
print("\n" + "=" * 80)
print("SQUAD LIST AUDIT BY LEAGUE AND TEAM")
print("=" * 80)

leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
for lg in leagues:
    c.execute("""
        SELECT team, COUNT(*), MAX(predicted_market_value_eur), 
               (SELECT name FROM players p2 WHERE p2.team = p1.team ORDER BY predicted_market_value_eur DESC LIMIT 1)
        FROM players p1
        WHERE league = ?
        GROUP BY team
        ORDER BY team
    """, (lg,))
    team_rows = c.fetchall()
    print(f"\n--- {lg.upper()} ({len(team_rows)} Teams) ---")
    for t_name, count, top_val, top_player in team_rows:
        t_clean = t_name.encode('ascii', 'replace').decode('ascii')
        p_clean = (top_player or 'Unknown').encode('ascii', 'replace').decode('ascii')
        print("  {:<24} | {:>2} players | Top: {:<20} (EUR {:>11,.0f})".format(
            t_clean, count, p_clean, top_val
        ))

conn.close()
