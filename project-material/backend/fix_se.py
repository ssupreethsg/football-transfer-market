import sqlite3

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

# Delete Saint-Etienne old players explicitly (ID <= 2837)
c.execute("DELETE FROM players WHERE team = 'Saint-Etienne' AND id <= 2837")

# Paris Saint-Germain was deleted. Let's recover them.
# The `insert_all_missing_players.py` script checks if a player exists.
# We will just run the insert logic for missing ones!

# ... Actually, running `insert_all_missing_players.py` will automatically re-insert PSG, Napoli, and Getafe because it checks if they exist in DB!
conn.commit()
conn.close()
print("Cleaned up Saint-Etienne.")
