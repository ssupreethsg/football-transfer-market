import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

minor_transfers = [
    ("Sebastiano Esposito", "Sassuolo"),
    ("Kristjan Asllani", "Al-Jazira"),
    ("Samuele Ricci", "Como"),
    ("Cyril Ngonge", "Monza"),
    ("Daniel Maldini", "Atalanta"),
    ("Javi Montero", "CD Legans"),
    ("Javi Muñoz", "Almeria"),
    ("Harry Winks", "Sampdoria")
]

updated = 0
for name, new_team in minor_transfers:
    # See if player exists
    c.execute("UPDATE players SET team = ? WHERE name LIKE ?", (new_team, f"%{name}%"))
    updated += c.rowcount

conn.commit()
conn.close()
print(f"Updated {updated} minor transfers for late August 2026.")
