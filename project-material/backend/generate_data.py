import pandas as pd
from sqlalchemy import create_engine
import os
import math
import urllib.request
from models import Base, Player
from database import engine, SessionLocal
import numpy as np

def clean_age(age_val):
    try:
        if pd.isna(age_val): return 25
        if isinstance(age_val, str) and '-' in age_val:
            return int(age_val.split('-')[0])
        return int(age_val)
    except:
        return 25

def safe_int(val):
    try:
        if pd.isna(val): return 0
        if isinstance(val, str):
            val = val.replace(',', '')
        return int(float(val))
    except:
        return 0

def download_data():
    csv_path = "real_data.csv"
    url = "https://raw.githubusercontent.com/MohammedAhdal/Football-Analysis-and-Clustring/main/2021-2022%20Football%20Player%20Stats.csv"
    print("Downloading real dataset from GitHub...")
    urllib.request.urlretrieve(url, csv_path)
    print("Download complete.")
    return csv_path

def process_real_data(csv_path):
    print(f"Loading real dataset from {csv_path}...")
    df = pd.read_csv(csv_path, encoding='ISO-8859-1', sep=';')
    
    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    
    players = []
    
    for _, row in df.iterrows():
        # Map FBref columns or fallback names
        name = row.get('player', 'Unknown Player')
        if name == 'Unknown Player' or pd.isna(name):
            continue
            
        # Basic mapping
        age = clean_age(row.get('age', 25))
        nation = str(row.get('nation', '')).split(' ')[-1] if not pd.isna(row.get('nation')) else 'UNK'
        league = str(row.get('comp', 'Unknown'))
        team = str(row.get('squad', 'Unknown'))
        
        # Stats
        minutes_played = safe_int(row.get('min', 0))
        goals = safe_int(row.get('goals', row.get('gls', 0)))
        assists = safe_int(row.get('assists', row.get('ast', 0)))
        
        # Extended Stats
        shots = safe_int(row.get('shots', 0))
        shots_on_target = safe_int(row.get('sot', 0))
        dribbles_completed = safe_int(row.get('drisucc', 0))
        dribbles_attempted = safe_int(row.get('driatt', 0))
        
        chances_created = safe_int(row.get('sca', 0)) # Shot creating actions
        passes_completed = safe_int(row.get('pastotcmp', 0))
        passes_attempted = safe_int(row.get('pastotatt', 0))
        progressive_passes = safe_int(row.get('pasprog', 0))
        
        tackles_won = safe_int(row.get('tklwon', 0))
        defense_interceptions = safe_int(row.get('int', 0))
        clearances = safe_int(row.get('clr', 0))
        blocks = safe_int(row.get('blocks', 0))
        aerials_won = safe_int(row.get('aerwon', 0))
        
        touches = safe_int(row.get('touches', 0))
        yellow_cards = safe_int(row.get('crdy', 0))
        red_cards = safe_int(row.get('crdr', 0))

        # Base value according to league
        base_val = 10000000
        if 'Premier' in league or 'ENG' in league: base_val = 20000000
        elif 'La Liga' in league or 'ESP' in league: base_val = 15000000
        elif 'Serie A' in league or 'ITA' in league: base_val = 12000000
        elif 'Bundesliga' in league or 'GER' in league: base_val = 12000000
        elif 'Ligue 1' in league or 'FRA' in league: base_val = 10000000
            
        # Age Factor
        if age <= 21:
            age_multiplier = 1.0 + ((22 - age) * 0.15)
        elif age <= 28:
            age_multiplier = 1.0 - ((age - 22) * 0.05)
        else:
            age_multiplier = max(0.1, 0.7 - ((age - 28) * 0.1))
            
        # Performance Factor (Expanded to use new stats)
        game_ratio = (minutes_played / 3420) if minutes_played > 0 else 0
        perf_multiplier = 1.0 + (goals * 0.05) + (assists * 0.03) + (chances_created * 0.005) + (tackles_won * 0.005) + (progressive_passes * 0.002) + (game_ratio * 0.2)
        
        # Hype
        hype = np.random.uniform(0.9, 1.3) if age < 24 else np.random.uniform(0.9, 1.1)
        
        # Calculate final market value
        raw_value = base_val * age_multiplier * perf_multiplier * hype
        market_value = max(100000, round(raw_value / 100000) * 100000)
        
        clean_league = league.replace('eng ', '').replace('es ', '').replace('it ', '').replace('de ', '').replace('fr ', '').strip()
        
        players.append(Player(
            name=name,
            nation=nation,
            age=age,
            height_cm=None,
            weight_kg=None,
            league=clean_league,
            team=team,
            goals=goals,
            assists=assists,
            minutes_played=minutes_played,
            shots=shots,
            shots_on_target=shots_on_target,
            dribbles_completed=dribbles_completed,
            dribbles_attempted=dribbles_attempted,
            chances_created=chances_created,
            passes_completed=passes_completed,
            passes_attempted=passes_attempted,
            progressive_passes=progressive_passes,
            tackles_won=tackles_won,
            defense_interceptions=defense_interceptions,
            clearances=clearances,
            blocks=blocks,
            aerials_won=aerials_won,
            touches=touches,
            yellow_cards=yellow_cards,
            red_cards=red_cards,
            predicted_market_value_eur=market_value
        ))
    
    return players

def main():
    csv_path = "real_data.csv"
    if not os.path.exists(csv_path):
        csv_path = download_data()
        
    print("Initializing Database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    db.query(Player).delete()
    db.commit()
    
    print("Parsing real player dataset for Top 5 Leagues...")
    players = process_real_data(csv_path)
    
    print(f"Inserting {len(players)} real players into database...")
    for i in range(0, len(players), 1000):
        db.bulk_save_objects(players[i:i+1000])
    
    db.commit()
    db.close()
    print("Real data ingestion complete.")

if __name__ == "__main__":
    main()
