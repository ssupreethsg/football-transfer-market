import sqlite3

conn = sqlite3.connect("sql_app.db")
c = conn.cursor()
c.execute("SELECT id, name, team FROM players WHERE team = 'Barcelona' OR team = 'FC Barcelona'")
for row in c.fetchall():
    print(row)
