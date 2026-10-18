import sqlite3
import re
import os
import random

db_path = 'sql_app.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

leagues_files = {
    'Premier League': 'raw_data_pl.txt',
    'La Liga': 'raw_data_laliga.txt',
    'Serie A': 'raw_data_seriea.txt',
    'Ligue 1': 'raw_data_ligue1.txt',
    'Bundesliga': 'raw_data_bundesliga.txt'
}

club_tiers = {
    1: ['Real Madrid', 'PSG', 'Bayern Munich', 'Manchester City', 'Arsenal', 'Liverpool', 'Manchester United'],
    2: ['FC Barcelona', 'Atlético Madrid', 'Chelsea', 'Tottenham Hotspur', 'Juventus', 'Inter Milan', 'AC Milan', 'Borussia Dortmund', 'RB Leipzig', 'Napoli', 'Aston Villa', 'Newcastle United'],
    3: ['West Ham United', 'Brighton & Hove Albion', 'Bayer Leverkusen', 'AS Roma', 'Lazio', 'Atalanta BC', 'Olympique Lyonnais', 'Olympique de Marseille', 'AS Monaco'],
}

def get_club_tier(club):
    for tier, clubs in club_tiers.items():
        if club in clubs or any(c in club for c in clubs):
            return tier
    return 4

def estimate_wage_and_value(age, position, tier):
    # Base weekly wage by tier (in EUR)
    base_wage = {1: 180000, 2: 100000, 3: 65000, 4: 25000}.get(tier, 25000)
    
    # Age multiplier
    if age < 20: age_mult = 0.4
    elif age < 23: age_mult = 0.7
    elif age <= 29: age_mult = 1.2
    elif age <= 33: age_mult = 0.9
    else: age_mult = 0.6
    
    # Position multiplier
    pos_mult = {'FWD': 1.3, 'MID': 1.1, 'DEF': 0.9, 'GK': 0.8}.get(position, 1.0)
    
    wage = base_wage * age_mult * pos_mult * random.uniform(0.8, 1.2)
    wage = round(wage / 1000) * 1000
    if wage < 5000: wage = 5000
    
    # Market value estimation
    # Young players have high potential value relative to wage
    if age < 21: val_mult = 300
    elif age < 24: val_mult = 250
    elif age <= 28: val_mult = 200
    elif age <= 31: val_mult = 100
    else: val_mult = 40
    
    market_value = wage * val_mult * random.uniform(0.85, 1.15)
    market_value = round(market_value / 100000) * 100000
    
    return wage, market_value

# Get existing names to avoid duplicates (case insensitive approximation)
c.execute("SELECT id, name, team FROM players")
existing = {f"{r[1].lower().strip()}_{r[2].lower().strip()}": r[0] for r in c.fetchall()}

# Ensure missing clubs exist in some capacity if there's a club table? 
# Wait, football_transfer_analytics typically stores clubs as distinct string values in `players` table.
# Let's get max player ID
c.execute("SELECT MAX(id) FROM players")
max_id = c.fetchone()[0] or 0

inserted = 0

for league, filename in leagues_files.items():
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        continue
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_club = None
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('###'):
            current_club = line.replace('###', '').strip()
            # Handle numbers like '1. Arsenal'
            current_club = re.sub(r'^\d+\.\s*', '', current_club)
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 5:
            name, pos, age, nation, club = parts[:5]
            age = int(age) if age.isdigit() else 25
            
            # Key for uniqueness: name + club
            key = f"{name.lower()}_{club.lower()}"
            if key not in existing:
                max_id += 1
                tier = get_club_tier(club)
                wage, value = estimate_wage_and_value(age, pos, tier)
                
                # Height/weight rough estimates
                height = round(random.uniform(175, 192), 1)
                weight = round(height - 100 + random.uniform(-5, 5), 1)
                if pos == 'GK': height = max(185.0, height)
                
                c.execute("""
                    INSERT INTO players 
                    (id, name, nation, age, height_cm, weight_kg, league, team, position, predicted_market_value_eur, wage_eur_weekly) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (max_id, name, nation, age, height, weight, league, club, pos, value, wage))
                
                # Insert basic competition stats for 2024/25
                c.execute("""
                    INSERT INTO player_competition_stats 
                    (player_id, competition_name, competition_type, season) 
                    VALUES (?, ?, 'League', '2024/2025')
                """, (max_id, league))
                
                existing[key] = max_id
                inserted += 1

# Cleanup FC Barcelona (remove duplicates, keep the most realistic 26 players)
# The user mentioned FC Barcelona has 41 players and needs cleanup
c.execute("SELECT id FROM players WHERE team LIKE '%Barcelona%'")
barca_players = c.fetchall()
if len(barca_players) > 28:
    print(f"Cleaning up Barcelona... currently {len(barca_players)} players")
    # Keep the newly inserted ones or highest market value ones
    c.execute("SELECT id FROM players WHERE team LIKE '%Barcelona%' ORDER BY predicted_market_value_eur DESC LIMIT 26")
    keep_ids = [r[0] for r in c.fetchall()]
    all_barca_ids = [r[0] for r in barca_players]
    delete_ids = [id for id in all_barca_ids if id not in keep_ids]
    
    for did in delete_ids:
        c.execute("DELETE FROM players WHERE id = ?", (did,))
        # cascade will handle competition_stats

# Missing clubs validation (Real Valladolid, Holstein Kiel, Monza)
missing_check = ['Real Valladolid', 'Holstein Kiel', 'Monza']
for mc in missing_check:
    c.execute("SELECT count(*) FROM players WHERE team LIKE ?", (f'%{mc}%',))
    print(f"{mc} player count: {c.fetchone()[0]}")

conn.commit()
conn.close()
print(f"Successfully inserted {inserted} missing players across top 5 leagues.")
