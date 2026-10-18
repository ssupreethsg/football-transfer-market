import sqlite3
import pandas as pd

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

# Get all players
df = pd.read_sql_query('SELECT id, name, team, league, appearances FROM players', conn)

# Normalize names (e.g. "Mohamed Salah" -> "mohamedsalah")
df['norm_name'] = df['name'].str.lower().str.replace(r'[^a-z]', '', regex=True)
df['norm_team'] = df['team'].str.lower().str.replace(r'[^a-z]', '', regex=True)

# Find duplicates by exact normalized name
dups = df[df.duplicated(subset=['norm_name', 'norm_team'], keep=False)]
print(f'Found {len(dups)} exact duplicates by normalized name & team.')

to_delete = []

# Group by normalized name and team to find duplicates
for (name, team), group in dups.groupby(['norm_name', 'norm_team']):
    # Sort by appearances to keep the one with the most data, or keep the smallest ID (original)
    group = group.sort_values(by=['appearances', 'id'], ascending=[False, True])
    # Keep the first one, delete the rest
    keep_id = group.iloc[0]['id']
    drop_ids = group.iloc[1:]['id'].tolist()
    to_delete.extend(drop_ids)

print(f"Identified {len(to_delete)} exact duplicates to delete.")

# Execute deletion
for did in to_delete:
    c.execute("DELETE FROM players WHERE id = ?", (did,))

conn.commit()
print("Exact duplicates removed.")
