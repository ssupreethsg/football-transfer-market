import sqlite3
import pandas as pd
from fuzzywuzzy import fuzz

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

# Get all players
df = pd.read_sql_query('SELECT id, name, team FROM players', conn)

to_delete = set()
count = 0

# Group by team
for team, group in df.groupby('team'):
    players = group.to_dict('records')
    # Compare every player to every other player in the same team
    n = len(players)
    for i in range(n):
        if players[i]['id'] in to_delete:
            continue
            
        for j in range(i+1, n):
            if players[j]['id'] in to_delete:
                continue
                
            name1 = players[i]['name']
            name2 = players[j]['name']
            
            # Use Token Set Ratio to handle "Gabriel Martinelli" vs "Martinelli"
            similarity = fuzz.token_set_ratio(name1, name2)
            
            # Special manual checks for encoding weirdness
            if similarity > 85 or (
                len(name1) > 5 and name1 in name2
            ) or (
                len(name2) > 5 and name2 in name1
            ):
                # Keep the one with the HIGHER ID (the new one we just inserted which has accurate position/stats)
                if players[i]['id'] > players[j]['id']:
                    to_delete.add(players[j]['id'])
                else:
                    to_delete.add(players[i]['id'])
                count += 1

print(f"\nFound {count} fuzzy duplicates. Deleting {len(to_delete)} records...")

for did in to_delete:
    c.execute("DELETE FROM players WHERE id = ?", (did,))

conn.commit()
conn.close()
print("Cleanup complete.")
