import sqlite3

conn = sqlite3.connect("sql_app.db")
c = conn.cursor()
c.execute("SELECT id, name, team, league FROM players WHERE name IN ('Bernd Leno', 'Kepa Arrizabalaga', 'Cole Palmer', 'Tyler Adams', 'Matz Sels', 'Ola Aina', 'Callum Hudson-Odoi', 'Taiwo Awoniyi', 'Donny van de Beek')")
for row in c.fetchall():
    print(row)
