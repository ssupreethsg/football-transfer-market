from sqlalchemy.orm import Session
from database import SessionLocal
from models import Player

def update_db():
    db = SessionLocal()
    players = db.query(Player).all()
    
    # 1. Increment ages to match 2024/25 (dataset was 21/22 -> +3 years)
    for p in players:
        p.age += 3
        
    # 2. Hardcode notable transfers for 24/25 accuracy
    transfers = {
        "Erling Haaland": {"team": "Manchester City", "league": "Premier League", "goals": 27, "assists": 5},
        "Jude Bellingham": {"team": "Real Madrid", "league": "La Liga", "goals": 19, "assists": 6},
        "Kylian Mbapp": {"team": "Real Madrid", "league": "La Liga", "goals": 27, "assists": 7},
        "Harry Kane": {"team": "Bayern Munich", "league": "Bundesliga", "goals": 36, "assists": 8},
        "Declan Rice": {"team": "Arsenal", "league": "Premier League"},
        "Alexis Mac Allister": {"team": "Liverpool", "league": "Premier League"},
        "Sandro Tonali": {"team": "Newcastle Utd", "league": "Premier League"},
        "Moiss Caicedo": {"team": "Chelsea", "league": "Premier League"},
        "Enzo Fernndez": {"team": "Chelsea", "league": "Premier League"},
        "Josko Gvardiol": {"team": "Manchester City", "league": "Premier League"},
        "Dominik Szoboszlai": {"team": "Liverpool", "league": "Premier League"},
        "Kai Havertz": {"team": "Arsenal", "league": "Premier League"},
        "Mason Mount": {"team": "Manchester Utd", "league": "Premier League"},
        "Rasmus Hjlund": {"team": "Manchester Utd", "league": "Premier League"},
        "Jrmy Doku": {"team": "Manchester City", "league": "Premier League"},
        "Randal Kolo Muani": {"team": "Paris S-G", "league": "Ligue 1"},
        "Ousmane Dembl": {"team": "Paris S-G", "league": "Ligue 1"},
        "Lucas Hernndez": {"team": "Paris S-G", "league": "Ligue 1"},
        "Milan Skriniar": {"team": "Paris S-G", "league": "Ligue 1"},
        "Manuel Ugarte": {"team": "Paris S-G", "league": "Ligue 1"},
        "Ilkay Gndogan": {"team": "Barcelona", "league": "La Liga"},
        "Joao Cancelo": {"team": "Barcelona", "league": "La Liga"},
        "Joao Felix": {"team": "Barcelona", "league": "La Liga"},
        "Xavi Simons": {"team": "RB Leipzig", "league": "Bundesliga"},
        "Lois Openda": {"team": "RB Leipzig", "league": "Bundesliga"},
        "Kim Min-jae": {"team": "Bayern Munich", "league": "Bundesliga"},
        "Victor Boniface": {"team": "Bayer Leverkusen", "league": "Bundesliga"},
        "Granit Xhaka": {"team": "Bayer Leverkusen", "league": "Bundesliga"},
        "Alejandro Grimaldo": {"team": "Bayer Leverkusen", "league": "Bundesliga"},
        "Marcus Thuram": {"team": "Inter", "league": "Serie A"},
        "Benjamin Pavard": {"team": "Inter", "league": "Serie A"},
        "Christian Pulisic": {"team": "Milan", "league": "Serie A"},
        "Ruben Loftus-Cheek": {"team": "Milan", "league": "Serie A"},
        "Romelu Lukaku": {"team": "Roma", "league": "Serie A"},
    }
    
    # Also fix some name encodings if possible
    for p in players:
        # Fix encoding issues in names (e.g. Mbapp)
        if "Mbapp" in p.name:
            p.name = "Kylian Mbappe"
            
        name = p.name
        
        # Apply transfer updates
        for t_name, t_data in transfers.items():
            if t_name.split(' ')[-1] in name or t_name == name:
                p.team = t_data.get("team", p.team)
                p.league = t_data.get("league", p.league)
                p.goals = t_data.get("goals", p.goals)
                p.assists = t_data.get("assists", p.assists)
                break
                
        # Re-calculate predicted market value based on current age/team
        base_val = 10000000
        if 'Premier' in p.league or 'ENG' in p.league: base_val = 20000000
        elif 'La Liga' in p.league or 'ESP' in p.league: base_val = 15000000
        elif 'Serie A' in p.league or 'ITA' in p.league: base_val = 12000000
        elif 'Bundesliga' in p.league or 'GER' in p.league: base_val = 12000000
        elif 'Ligue 1' in p.league or 'FRA' in p.league: base_val = 10000000
            
        if p.age <= 21: age_multiplier = 1.0 + ((22 - p.age) * 0.15)
        elif p.age <= 28: age_multiplier = 1.0 - ((p.age - 22) * 0.05)
        else: age_multiplier = max(0.1, 0.7 - ((p.age - 28) * 0.1))
            
        game_ratio = (p.minutes_played / 3420) if p.minutes_played > 0 else 0
        perf_multiplier = 1.0 + (p.goals * 0.05) + (p.assists * 0.03) + (p.chances_created * 0.005) + (p.tackles_won * 0.005) + (p.progressive_passes * 0.002) + (game_ratio * 0.2)
        
        raw_value = base_val * age_multiplier * perf_multiplier * 1.1
        p.predicted_market_value_eur = max(100000, round(raw_value / 100000) * 100000)

    db.commit()
    db.close()
    print("Database successfully updated to 2024/2025 season attributes.")

if __name__ == "__main__":
    update_db()
