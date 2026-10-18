import sqlite3
import pandas as pd
from fuzzywuzzy import fuzz
import re

conn = sqlite3.connect('sql_app.db')
c = conn.cursor()

leagues_files = {
    'Premier League': 'raw_data_pl.txt',
    'La Liga': 'raw_data_laliga.txt',
    'Serie A': 'raw_data_seriea.txt',
    'Ligue 1': 'raw_data_ligue1.txt',
    'Bundesliga': 'raw_data_bundesliga.txt'
}

# 1. Parse truth data
truth_squads = {} # team -> list of names

def normalize(name):
    # Remove accents/special chars for comparison
    return re.sub(r'[^a-z]', '', name.lower())

for league, filename in leagues_files.items():
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_club = None
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('###'):
            current_club = line.replace('###', '').strip()
            current_club = re.sub(r'^\d+\.\s*', '', current_club)
            
            # Map truth club names to DB standard club names
            team_map = {
                'Auxerre': 'AJ Auxerre', 'Brest': 'Stade Brestois 29', 'Le Havre': 'Le Havre AC',
                'Lens': 'RC Lens', 'Lille': 'Lille OSC', 'Lyon': 'Olympique Lyonnais',
                'Marseille': 'Olympique de Marseille', 'Monaco': 'AS Monaco', 'Montpellier': 'Montpellier HSC',
                'Nantes': 'FC Nantes', 'Nice': 'OGC Nice', 'PSG': 'Paris Saint-Germain',
                'RC Strasbourg': 'Strasbourg', 'Reims': 'Stade de Reims', 'Rennes': 'Stade Rennais',
                'Saint-tienne': 'AS Saint-tienne', 'Toulouse': 'Toulouse FC', 'Athletic Club (Bilbao)': 'Athletic Club',
                'Sevilla FC': 'Sevilla', 'Valencia CF': 'Valencia', 'Villarreal CF': 'Villarreal',
                'FC Barcelona': 'FC Barcelona', 'Real Madrid': 'Real Madrid'
            }
            if current_club in team_map:
                current_club = team_map[current_club]
                
            truth_squads[current_club] = []
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 5 and current_club:
            truth_squads[current_club].append(parts[0])

# Fix any mapping issues for keys in truth_squads
db_teams = [r[0] for r in c.execute("SELECT DISTINCT team FROM players WHERE league IN ('Premier League', 'La Liga', 'Serie A', 'Ligue 1', 'Bundesliga')").fetchall()]

valid_truth_teams = {}
for t, names in truth_squads.items():
    # find best match in db_teams
    best_match = None
    best_score = 0
    for dt in db_teams:
        score = fuzz.ratio(t.lower(), dt.lower())
        if score > best_score:
            best_score = score
            best_match = dt
    if best_score > 80:
        valid_truth_teams[best_match] = names
    else:
        valid_truth_teams[t] = names

# 2. Iterate DB and delete invalid players
c.execute("SELECT id, name, team FROM players WHERE league IN ('Premier League', 'La Liga', 'Serie A', 'Ligue 1', 'Bundesliga')")
db_players = c.fetchall()

to_delete = []

for pid, name, team in db_players:
    if team not in valid_truth_teams:
        # If the team isn't in our truth data (e.g. relegated teams still assigned to top 5 league?), skip or delete?
        # Relegated teams were moved to other leagues, so they shouldn't be here.
        continue
        
    truth_names = valid_truth_teams[team]
    
    # Check if this DB player matches any truth name
    matched = False
    for t_name in truth_names:
        if fuzz.token_set_ratio(name, t_name) > 80 or (normalize(name) in normalize(t_name)) or (normalize(t_name) in normalize(name)):
            matched = True
            break
            
    if not matched:
        # Protect player ID 1 just in case
        if pid != 1:
            to_delete.append((pid, name, team))

print(f"Identified {len(to_delete)} players who are NOT in the 2024/25 scraped truth data.")
for p in to_delete:
    c.execute("DELETE FROM players WHERE id = ?", (p[0],))

conn.commit()
conn.close()
print("Perfect truth pruning complete.")
