import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()
c.execute('''
    SELECT name, age, position, team, league, goals, assists, minutes_played, predicted_market_value_eur 
    FROM players 
    ORDER BY predicted_market_value_eur DESC 
    LIMIT 30
''')
rows = c.fetchall()

header = "{:<4} | {:<22} | {:<4} | {:<4} | {:<20} | {:<16} | {:<7} | {:<6} | {:<18}".format(
    "Rank", "Player", "Age", "Pos", "Team", "League", "G / A", "Mins", "Market Value"
)
print(header)
print("=" * len(header))

for i, r in enumerate(rows, 1):
    name_clean = r[0].encode('ascii', 'replace').decode('ascii')
    team_clean = r[3].encode('ascii', 'replace').decode('ascii')
    val_str = "EUR {:,.0f}".format(r[8])
    ga_str = "{}/{}".format(r[5], r[6])
    print("{:<4} | {:<22} | {:<4} | {:<4} | {:<20} | {:<16} | {:<7} | {:<6} | {:<18}".format(
        i, name_clean, r[1], r[2], team_clean, r[4], ga_str, r[7], val_str
    ))

conn.close()
