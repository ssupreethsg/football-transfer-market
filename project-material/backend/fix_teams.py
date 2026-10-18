import sqlite3
import pandas as pd

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

# 1. Standardize teams
team_updates = [
    ("Bologna FC 1909", "Bologna"),
    ("Cagliari Calcio", "Cagliari"),
    ("Empoli FC", "Empoli"),
    ("Genoa CFC", "Genoa"),
    ("SS Lazio", "Lazio"),
    ("SSC Napoli", "Napoli"),
    ("Torino FC", "Torino"),
    ("Udinese Calcio", "Udinese"),
    ("RC Strasbourg Alsace", "Strasbourg"),
    ("Getafe CF", "Getafe"),
    ("Saint-tienne", "Saint-Etienne"),
    ("AS Saint-Etienne", "Saint-Etienne"),
    ("AS Saint-tienne", "Saint-Etienne"),
]

for old, new in team_updates:
    c.execute("UPDATE players SET team = ? WHERE team LIKE ?", (new, f"%{old}%"))
    c.execute("UPDATE players SET team = ? WHERE team = ?", (new, old))
    
# Standardize Saint Etienne properly via substring
c.execute("UPDATE players SET team = 'Saint-Etienne' WHERE team LIKE '%Saint-%'")
c.execute("UPDATE players SET team = 'Paris Saint-Germain' WHERE team LIKE '%Paris%'")

# 2. We have oversized teams still (e.g. Bologna has 48 players).
# We want exactly the 2024/25 players. The easiest way to get exactly the right players is to DELETE any player with ID <= 2837 for these specific problem teams, because all the 2024/25 players were inserted with ID > 2837.
problem_teams = ['Bologna', 'Cagliari', 'Empoli', 'Genoa', 'Lazio', 'Napoli', 'Torino', 'Udinese', 'Strasbourg', 'Getafe', 'Saint-Etienne', 'Paris Saint-Germain', 'FC Nantes', 'Angers SCO']

for t in problem_teams:
    # Check if there are new players for this team (ID > 2837)
    c.execute("SELECT count(*) FROM players WHERE team = ? AND id > 2837", (t,))
    new_count = c.fetchone()[0]
    
    if new_count > 15:
        # Safe to delete old ones
        c.execute("DELETE FROM players WHERE team = ? AND id <= 2837", (t,))
        print(f"Deleted old players for {t}")
    else:
        # If there are not enough new players, keep them all
        print(f"Skipping {t} (only {new_count} new players)")

conn.commit()
conn.close()
print("Team fix complete.")
