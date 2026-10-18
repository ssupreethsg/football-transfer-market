import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(__file__), 'sql_app.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Starting database remediation...")

# 1. Purge tier-2 relegated league players and cascade delete competition stats
relegated_leagues = ('2. Bundesliga', 'EFL Championship', 'Ligue 2', 'Segunda División', 'Segunda Divisin', 'Serie B')
placeholders = ','.join(['?'] * len(relegated_leagues))

c.execute(f"SELECT id FROM players WHERE league IN ({placeholders})", relegated_leagues)
relegated_ids = [row[0] for row in c.fetchall()]

if relegated_ids:
    print(f"Purging {len(relegated_ids)} players from secondary divisions...")
    id_placeholders = ','.join(['?'] * len(relegated_ids))
    c.execute(f"DELETE FROM player_competition_stats WHERE player_id IN ({id_placeholders})", relegated_ids)
    c.execute(f"DELETE FROM players WHERE id IN ({id_placeholders})", relegated_ids)

# 2. Fix the 16 cross-assigned elite players
corrections = [
    ('Kevin De Bruyne', 'Manchester City', 'Premier League'),
    ('Rodri', 'Manchester City', 'Premier League'),
    ('Rodrigo Bentancur', 'Tottenham Hotspur', 'Premier League'),
    ('Rodrigo Muniz', 'Fulham', 'Premier League'),
    ('Rodrigo Gomes', 'Wolverhampton Wanderers', 'Premier League'),
    ('Harry Winks', 'Leicester City', 'Premier League'),
    ('Piero Hincapié', 'Bayer Leverkusen', 'Bundesliga'),
    ('Florian Wirtz', 'Bayer Leverkusen', 'Bundesliga'),
    ('Gianluigi Donnarumma', 'Paris Saint-Germain', 'Ligue 1'),
    ('Bradley Barcola', 'Paris Saint-Germain', 'Ligue 1'),
    ('Khvicha Kvaratskhelia', 'Napoli', 'Serie A'),
    ('Ayyoub Bouaddi', 'Lille OSC', 'Ligue 1'),
    ('Maxence Lacroix', 'Crystal Palace', 'Premier League'),
    ('Kristjan Asllani', 'Inter Milan', 'Serie A'),
    ('Sebastiano Esposito', 'Empoli', 'Serie A'),
    ('Javi Muñoz', 'UD Las Palmas', 'La Liga')
]

for name, team, league in corrections:
    # Match using LIKE or exact name to handle encoding variants
    c.execute("UPDATE players SET team = ?, league = ? WHERE name LIKE ?", (team, league, f"%{name.split()[-1]}%"))
    print(f"Restored {name} -> {team} ({league})")

# 3. Clean up any remaining rogue teams not in the top 5 leagues
c.execute("DELETE FROM player_competition_stats WHERE player_id IN (SELECT id FROM players WHERE team IN ('Al-Jazira', 'Almeria', 'Sampdoria', 'Sassuolo') AND league NOT IN ('Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'))")
c.execute("DELETE FROM players WHERE team IN ('Al-Jazira', 'Almeria')")

# Standardize club names to canonical top-5 names
club_normalizations = {
    'Atltico Madrid': 'Atlético Madrid',
    'CD Legans': 'CD Leganés',
    'Deportivo Alavs': 'Deportivo Alavés',
    'Borussia Mnchengladbach': 'Borussia Mönchengladbach',
    'Saint-Etienne': 'AS Saint-Étienne',
    'Strasbourg': 'RC Strasbourg'
}
for old_name, new_name in club_normalizations.items():
    c.execute("UPDATE players SET team = ? WHERE team = ?", (new_name, old_name))

conn.commit()

# 4. Check results
total = c.execute("SELECT count(*) FROM players").fetchone()[0]
leagues = c.execute("SELECT league, count(DISTINCT team), count(*) FROM players GROUP BY league").fetchall()

print(f"\nRemediation Complete! Total Players: {total}")
print("Leagues breakdown:")
for l, t_cnt, p_cnt in leagues:
    print(f"  {l}: {t_cnt} clubs, {p_cnt} players")

# Check squad sizes
team_sizes = c.execute("SELECT team, league, count(*) as cnt FROM players GROUP BY team, league ORDER BY cnt ASC").fetchall()
print(f"Total unique clubs across all leagues: {len(team_sizes)}")
out_of_range = [t for t in team_sizes if t[2] < 20 or t[2] > 34]
print(f"Clubs with squad size out of range (20-34): {len(out_of_range)}")
if out_of_range:
    for t in out_of_range:
        print(f"  Out of range club: {t}")

conn.close()

# 5. Export JSON to frontend
print("\nExporting fresh data to frontend/src/data/...")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

players = [dict(row) for row in c.execute('SELECT * FROM players ORDER BY predicted_market_value_eur DESC').fetchall()]
stats = [dict(row) for row in c.execute('SELECT * FROM player_competition_stats').fetchall()]

stats_by_player = {}
for s in stats:
    pid = s['player_id']
    stats_by_player.setdefault(pid, []).append(dict(s))

for p in players:
    p['competition_stats'] = stats_by_player.get(p['id'], [])

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'data'))
os.makedirs(data_dir, exist_ok=True)

with open(os.path.join(data_dir, 'players.json'), 'w', encoding='utf-8') as f:
    json.dump(players, f)

top_player = players[0] if players else None
clause_count = sum(1 for p in players if p.get('release_clause_eur'))
summary = {
    'total_players': len(players),
    'players_with_release_clause': clause_count,
    'total_competition_records': len(stats),
    'most_valuable_player': {
        'name': top_player['name'] if top_player else None,
        'team': top_player['team'] if top_player else None,
        'value_eur': top_player['predicted_market_value_eur'] if top_player else 0,
        'release_clause_eur': top_player.get('release_clause_eur')
    }
}
with open(os.path.join(data_dir, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print(f"Successfully exported {len(players)} players and summary to frontend!")
conn.close()
