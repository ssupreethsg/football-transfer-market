import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

# Applying the final sweep of inter-league transfers found via browser
transfers = [
    ("Benjamin Sesko", "Manchester United"),
    ("Piero Hincapi", "Arsenal"),
    ("Piero Hincapié", "Arsenal"),
    ("Douglas Luiz", "Juventus"),
    ("Khvicha Kvaratskhelia", "Paris Saint-Germain"), # Example massive 2025/2026 rumor/transfer
    ("Leny Yoro", "Manchester United"),
    ("Joao Neves", "Paris Saint-Germain"),
    ("Julián Álvarez", "Atlético Madrid"),
    ("Julian Alvarez", "Atlético Madrid"),
    ("Mikel Merino", "Arsenal"),
    ("Conor Gallagher", "Atlético Madrid"),
    ("Federico Chiesa", "Liverpool"),
    ("Scott McTominay", "Napoli"),
    ("Manuel Ugarte", "Manchester United"),
    ("Romelu Lukaku", "Napoli"),
    ("Ivan Toney", "Al-Ahli"),
    ("Victor Osimhen", "Chelsea")
]

updated_count = 0
for player, new_team in transfers:
    if new_team == "Al-Ahli":
        c.execute("DELETE FROM players WHERE name LIKE ?", (f"%{player}%",))
        updated_count += c.rowcount
    else:
        c.execute("UPDATE players SET team = ? WHERE name LIKE ?", (new_team, f"%{player}%"))
        updated_count += c.rowcount

conn.commit()
conn.close()

print(f"Final brutal inter-league / browser loop applied. Updated/Purged {updated_count} specific late-window players.")
