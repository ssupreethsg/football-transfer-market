import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

transfers = [
    ("Kevin De Bruyne", "Napoli")
]

updated_count = 0
for player, new_team in transfers:
    c.execute("UPDATE players SET team = ? WHERE name LIKE ?", (new_team, f"%{player}%"))
    updated_count += c.rowcount

conn.commit()
conn.close()
print(f"Brutal targeted fix applied for KDB. Updated {updated_count} players.")
