import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

transfers = [
    ("Bradley Barcola", "Liverpool"),
    ("Carlos Baleba", "Manchester United"),
    ("Savinho", "Tottenham Hotspur"),
    ("Nico Gonzalez", "Newcastle United"),
    ("Ezri Konsa", "Arsenal"),
    ("Bruno Guimares", "Arsenal"),
    ("Bruno Guimarães", "Arsenal"),
    ("Rodri", "FC Barcelona"),
    ("Emiliano Martinez", "Chelsea"),
    ("Jordan Henderson", "Chelsea"),
    ("Maxence Lacroix", "Chelsea"),
    ("Morgan Rogers", "Chelsea")
]

for name, new_team in transfers:
    print(f"Transferring {name} to {new_team}")
    c.execute("UPDATE players SET team = ? WHERE name LIKE ?", (new_team, f"%{name}%"))
    
conn.commit()
conn.close()
print("Late August 2026 transfers completed.")
