import sqlite3

def add_missing_stars():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    missing_players = [
        ("Lamine Yamal", 19, "ESP", "Barcelona", "La Liga", 5, 7, 2100),
        ("Cole Palmer", 24, "ENG", "Chelsea", "Premier League", 22, 11, 2800),
        ("Kobbie Mainoo", 21, "ENG", "Manchester Utd", "Premier League", 3, 1, 2000),
        ("Arda Guler", 21, "TUR", "Real Madrid", "La Liga", 6, 0, 400),
        ("Endrick", 20, "BRA", "Real Madrid", "La Liga", 0, 0, 0),
        ("Warren Zaire-Emery", 20, "FRA", "Paris S-G", "Ligue 1", 2, 3, 2200),
        ("Alejandro Garnacho", 22, "ARG", "Manchester Utd", "Premier League", 7, 4, 2500),
        ("Savinho", 22, "BRA", "Manchester City", "Premier League", 9, 10, 2400),
        ("Bradley Barcola", 23, "FRA", "Paris S-G", "Ligue 1", 4, 7, 1800),
        ("Pau Cubarsi", 19, "ESP", "Barcelona", "La Liga", 0, 0, 1500),
        ("Leny Yoro", 20, "FRA", "Manchester Utd", "Premier League", 2, 0, 2500),
        ("Joao Neves", 21, "POR", "Paris S-G", "Ligue 1", 3, 2, 2700),
        ("Riccardo Calafiori", 24, "ITA", "Arsenal", "Premier League", 2, 5, 2600),
        ("Michael Olise", 24, "FRA", "Bayern Munich", "Bundesliga", 10, 6, 1500),
        ("Xavi Simons", 23, "NED", "RB Leipzig", "Bundesliga", 8, 11, 2800)
    ]
    
    for p in missing_players:
        name, age, nation, team, league, goals, assists, mins = p
        # Check if exists
        cursor.execute("SELECT id FROM players WHERE name LIKE ?", (f"%{name}%",))
        if cursor.fetchone():
            continue
            
        cursor.execute('''
            INSERT INTO players 
            (name, age, nation, team, league, goals, assists, minutes_played, 
             shots, shots_on_target, tackles_won, defense_interceptions, 
             yellow_cards, red_cards, dribbles_completed, dribbles_attempted, 
             chances_created, passes_completed, passes_attempted, progressive_passes, 
             clearances, blocks, aerials_won, touches, predicted_market_value_eur)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50000000)
        ''', (name, age, nation, team, league, goals, assists, mins))
        
    conn.commit()
    conn.close()
    print("Missing 2024-2026 stars added!")

if __name__ == "__main__":
    add_missing_stars()
