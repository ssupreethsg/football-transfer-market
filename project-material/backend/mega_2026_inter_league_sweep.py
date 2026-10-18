import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

transfers = [
    # 2026 Summer
    ("Elliot Anderson", "Manchester City"),
    ("Yan Diomande", "Real Madrid"),
    ("Sandro Tonali", "Tottenham Hotspur"),
    ("Mateus Fernandes", "Tottenham Hotspur"),
    ("Nicolas Jackson", "Aston Villa"),
    ("Johan Manzambi", "Aston Villa"),
    # 2025 Summer 
    ("Gianluigi Donnarumma", "Manchester City"),
    ("Alexander Isak", "Liverpool"),
    ("Florian Wirtz", "Liverpool")
]

updated_count = 0
for player, new_team in transfers:
    c.execute("UPDATE players SET team = ? WHERE name LIKE ?", (new_team, f"%{player}%"))
    updated_count += c.rowcount
    if c.rowcount > 0:
        print(f"Updated {player} to {new_team}")

conn.commit()
conn.close()
print(f"Sweep complete. Updated {updated_count} inter-league and domestic megadeals from 2025/2026.")
