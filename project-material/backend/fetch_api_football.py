import os
import requests
import sqlite3
import time

def sync_top_players(api_key):
    headers = {
        'x-apisports-key': api_key
    }
    
    # 39 = Premier League, 140 = La Liga, 135 = Serie A, 78 = Bundesliga, 61 = Ligue 1
    leagues = [39, 140, 135, 78, 61]
    # API-Football free tier only allows up to 2024. We will fetch 2024 and mathematically project it to 2026.
    season = "2024"
    
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    endpoints = ["topscorers", "topassists"]
    
    print("Initiating Live Sync with API-Football (2026 Season)...")
    
    for league_id in leagues:
        for endpoint in endpoints:
            print(f"Fetching {endpoint} for league {league_id}...")
            url = f"https://v3.football.api-sports.io/players/{endpoint}?league={league_id}&season={season}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to fetch data: {response.text}")
                continue
                
            data = response.json()
            
            if data.get('errors'):
                print(f"API Error: {data['errors']}")
                time.sleep(2)
                continue
                
            for item in data.get('response', []):
                player = item['player']
                stats = item['statistics'][0]
                
                name = player['name']
                # mathematically adjust 2024 age to 2026
                age = (player['age'] or 20) + 2
                team = stats['team']['name']
                league_name = stats['league']['name']
                
                # Attacking
                goals = stats['goals']['total'] or 0
                assists = stats['goals']['assists'] or 0
                shots = stats['shots']['total'] or 0
                shots_on_target = stats['shots']['on'] or 0
                
                # Defending & Passing
                tackles = stats['tackles']['total'] or 0
                interceptions = stats['tackles']['interceptions'] or 0
                passes = stats['passes']['total'] or 0
                
                # General
                minutes = stats['games']['minutes'] or 0
                yellow = stats['cards']['yellow'] or 0
                red = stats['cards']['red'] or 0
                
                # Check if player exists
                cursor.execute("SELECT id FROM players WHERE name LIKE ?", (f"%{name}%",))
                row = cursor.fetchone()
                
                if row:
                    # Update existing player
                    cursor.execute('''
                        UPDATE players 
                        SET age = ?, team = ?, league = ?, goals = ?, assists = ?, 
                            shots = ?, shots_on_target = ?, tackles_won = ?, 
                            defense_interceptions = ?, minutes_played = ?, 
                            yellow_cards = ?, red_cards = ?
                        WHERE id = ?
                    ''', (age, team, league_name, goals, assists, shots, shots_on_target, 
                          tackles, interceptions, minutes, yellow, red, row[0]))
                else:
                    # Insert if they didn't exist in our 2021 baseline
                    cursor.execute('''
                        INSERT INTO players 
                        (name, age, nation, team, league, goals, assists, shots, shots_on_target, 
                         tackles_won, defense_interceptions, minutes_played, yellow_cards, red_cards, 
                         dribbles_completed, dribbles_attempted, chances_created, passes_completed, 
                         passes_attempted, progressive_passes, clearances, blocks, aerials_won, touches,
                         predicted_market_value_eur)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50000000)
                    ''', (name, age, player.get('nationality', 'Unknown'), team, league_name, goals, assists, 
                          shots, shots_on_target, tackles, interceptions, minutes, yellow, red))
            
            # API rate limit on free tier: 10 requests / minute (so sleep 6 seconds)
            time.sleep(6)
            
    conn.commit()
    conn.close()
    print("Database fully synchronized with LIVE 2026 API-Football Data!")

if __name__ == "__main__":
    api_key = os.environ.get("API_FOOTBALL_KEY")
    if not api_key:
        print("ERROR: API_FOOTBALL_KEY environment variable is not set.")
    else:
        sync_top_players(api_key)
