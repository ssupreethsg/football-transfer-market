"""
Adversarial Verification and Stress-Testing Suite for sql_app.db
Author: challenger_1 (EMPIRICAL CHALLENGER)
"""

import sqlite3
import sys
import os
import unicodedata
import json

DB_PATH = os.path.abspath(r"c:\Users\Supreeth\OneDrive\Desktop\antigravityfiles\football_transfer_analytics\backend\sql_app.db")

def normalize_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text.lower().strip()

def run_adversarial_tests():
    print("=" * 80)
    print("EMPIRICAL CHALLENGER: ADVERSARIAL STRESS-TEST SUITE")
    print(f"Target DB: {DB_PATH}")
    print("=" * 80)

    if not os.path.exists(DB_PATH):
        print(f"FATAL: Database file does not exist at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    failures = []
    warnings = []
    passed_checks = []

    # -------------------------------------------------------------------------
    # TEST 1: Top 5 Leagues & 96 Clubs Count and Distribution
    # -------------------------------------------------------------------------
    print("\n[TEST 1] League & Club Distribution Stress Test...")
    cursor.execute("""
        SELECT league, COUNT(DISTINCT team) as team_count
        FROM players
        GROUP BY league
        ORDER BY league
    """)
    league_counts = {row["league"]: row["team_count"] for row in cursor.fetchall()}
    
    expected_leagues = {
        "Premier League": 20,
        "La Liga": 20,
        "Serie A": 20,
        "Bundesliga": 18,
        "Ligue 1": 18
    }

    total_clubs = sum(league_counts.get(lg, 0) for lg in expected_leagues)
    print(f"Discovered League Distribution: {league_counts}")
    print(f"Total Top 5 Clubs: {total_clubs} (Expected: 96)")

    if total_clubs != 96:
        failures.append(f"Expected exactly 96 Top 5 clubs, but found {total_clubs}")
    else:
        passed_checks.append("Total Top 5 clubs == 96")

    for lg, exp_cnt in expected_leagues.items():
        actual = league_counts.get(lg, 0)
        if actual != exp_cnt:
            failures.append(f"League '{lg}' has {actual} clubs, expected {exp_cnt}")
        else:
            passed_checks.append(f"League '{lg}' has exactly {exp_cnt} clubs")

    # Check for any unexpected leagues
    unexpected_leagues = [lg for lg in league_counts if lg not in expected_leagues]
    if unexpected_leagues:
        failures.append(f"Unexpected leagues present in database: {unexpected_leagues}")

    # -------------------------------------------------------------------------
    # TEST 2: Strict Squad Boundary Test [20, 33] on all 96 Clubs
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Squad Size Boundary Stress Test [20, 33] for ALL 96 Clubs...")
    cursor.execute("""
        SELECT league, team, COUNT(*) as squad_size
        FROM players
        WHERE league IN ('Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1')
        GROUP BY league, team
        ORDER BY squad_size ASC, team ASC
    """)
    squads = cursor.fetchall()
    
    squad_sizes = [r["squad_size"] for r in squads]
    min_size = min(squad_sizes) if squad_sizes else 0
    max_size = max(squad_sizes) if squad_sizes else 0
    avg_size = sum(squad_sizes) / len(squad_sizes) if squad_sizes else 0

    print(f"Total Clubs Evaluated: {len(squads)}")
    print(f"Min Squad Size: {min_size} (Required: >= 20)")
    print(f"Max Squad Size: {max_size} (Required: <= 33)")
    print(f"Average Squad Size: {avg_size:.2f}")

    underpopulated = [r for r in squads if r["squad_size"] < 20]
    overpopulated = [r for r in squads if r["squad_size"] > 33]

    if underpopulated:
        failures.append(f"Found {len(underpopulated)} underpopulated clubs (< 20): {[(r['team'], r['squad_size']) for r in underpopulated]}")
    else:
        passed_checks.append("All clubs have at least 20 players (min_size >= 20)")

    if overpopulated:
        failures.append(f"Found {len(overpopulated)} overpopulated clubs (> 33): {[(r['team'], r['squad_size']) for r in overpopulated]}")
    else:
        passed_checks.append("All clubs have at most 33 players (max_size <= 33)")

    # Boundary hits
    min_boundary_clubs = [r["team"] for r in squads if r["squad_size"] == 20]
    max_boundary_clubs = [r["team"] for r in squads if r["squad_size"] == 33]
    print(f"Clubs at lower boundary (size == 20): {len(min_boundary_clubs)} -> {min_boundary_clubs}")
    print(f"Clubs at upper boundary (size == 33): {len(max_boundary_clubs)} -> {max_boundary_clubs}")

    # -------------------------------------------------------------------------
    # TEST 3: Duplicate Player Integrity Checks
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Duplicate Player Integrity Stress Test...")
    # Check 3.1: Duplicate IDs
    cursor.execute("""
        SELECT id, COUNT(*) as cnt
        FROM players
        GROUP BY id
        HAVING cnt > 1
    """)
    dup_ids = cursor.fetchall()
    if dup_ids:
        failures.append(f"Found {len(dup_ids)} duplicate player IDs in database: {[r['id'] for r in dup_ids]}")
    else:
        passed_checks.append("Zero duplicate player IDs")

    # Check 3.2: Duplicate (Name, Team) exact
    cursor.execute("""
        SELECT team, name, COUNT(*) as cnt
        FROM players
        GROUP BY team, name
        HAVING cnt > 1
    """)
    dup_name_team = cursor.fetchall()
    if dup_name_team:
        failures.append(f"Found {len(dup_name_team)} duplicate (name, team) records: {[(r['team'], r['name'], r['cnt']) for r in dup_name_team]}")
    else:
        passed_checks.append("Zero duplicate (name, team) records")

    # Check 3.3: Case-insensitive / normalized (Name, Team) duplicates
    cursor.execute("SELECT id, name, team FROM players")
    all_players = cursor.fetchall()
    normalized_team_map = {}
    normalized_duplicates = []
    for p in all_players:
        norm_key = (normalize_text(p["name"]), p["team"])
        if norm_key in normalized_team_map:
            normalized_duplicates.append((p["name"], normalized_team_map[norm_key]["name"], p["team"]))
        else:
            normalized_team_map[norm_key] = p

    if normalized_duplicates:
        failures.append(f"Found {len(normalized_duplicates)} normalized name duplicates in same team: {normalized_duplicates}")
    else:
        passed_checks.append("Zero normalized name duplicates within any single team")

    # Check 3.4: Cross-team duplicate players check
    cursor.execute("""
        SELECT name, COUNT(DISTINCT team) as club_count, GROUP_CONCAT(team, ' | ') as clubs
        FROM players
        GROUP BY name
        HAVING club_count > 1
    """)
    cross_team_dups = cursor.fetchall()
    print(f"Identical player names across multiple teams: {len(cross_team_dups)}")
    for r in cross_team_dups:
        print(f"  - '{r['name']}' in {r['club_count']} clubs: {r['clubs']}")

    # -------------------------------------------------------------------------
    # TEST 4: Null / Sanity / Data Anomaly Checks
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Null / Sanity / Data Anomaly Stress Test...")
    
    # 4.1: Null or empty names
    cursor.execute("SELECT id, team FROM players WHERE name IS NULL OR TRIM(name) = ''")
    null_names = cursor.fetchall()
    if null_names:
        failures.append(f"Found {len(null_names)} players with NULL or empty name")
    else:
        passed_checks.append("Zero NULL or empty player names")

    # 4.2: Null or empty team / league
    cursor.execute("SELECT id, name FROM players WHERE team IS NULL OR TRIM(team) = '' OR league IS NULL OR TRIM(league) = ''")
    null_team_league = cursor.fetchall()
    if null_team_league:
        failures.append(f"Found {len(null_team_league)} players with NULL team or league")
    else:
        passed_checks.append("Zero NULL team or league fields")

    # 4.3: Invalid positions
    cursor.execute("SELECT DISTINCT position FROM players")
    positions = [r["position"] for r in cursor.fetchall()]
    print(f"Distinct positions in DB: {positions}")
    valid_positions = {"GK", "DEF", "MID", "FWD", "CB", "LB", "RB", "LWB", "RWB", "CM", "CDM", "CAM", "LM", "RM", "LW", "RW", "CF", "ST"}
    invalid_positions = [p for p in positions if p not in valid_positions and p is not None]
    if invalid_positions:
        failures.append(f"Found invalid positions in database: {invalid_positions}")
    else:
        passed_checks.append("All positions match standard football categorizations")

    # 4.4: Market value sanity (< 0 or NULL or NaN)
    cursor.execute("SELECT id, name, team, predicted_market_value_eur FROM players WHERE predicted_market_value_eur IS NULL OR predicted_market_value_eur < 0")
    bad_valuations = cursor.fetchall()
    if bad_valuations:
        failures.append(f"Found {len(bad_valuations)} players with negative or NULL market valuation: {[(r['name'], r['predicted_market_value_eur']) for r in bad_valuations]}")
    else:
        passed_checks.append("Zero negative or NULL predicted market valuations")

    # 4.5: Wage and clause sanity
    cursor.execute("SELECT id, name, team, wage_eur_weekly FROM players WHERE wage_eur_weekly IS NULL OR wage_eur_weekly < 0")
    bad_wages = cursor.fetchall()
    if bad_wages:
        failures.append(f"Found {len(bad_wages)} players with negative or NULL weekly wage")
    else:
        passed_checks.append("Zero negative or NULL weekly wages")

    # 4.6: Age sanity (< 15 or > 45)
    cursor.execute("SELECT id, name, team, age FROM players WHERE age IS NULL OR age < 15 OR age > 45")
    bad_ages = cursor.fetchall()
    if bad_ages:
        failures.append(f"Found {len(bad_ages)} players with out-of-range ages (15-45): {[(r['name'], r['age']) for r in bad_ages]}")
    else:
        passed_checks.append("Zero out-of-range player ages (15 <= age <= 45)")

    # 4.7: Contract expiry year sanity (< 2024 or > 2036)
    cursor.execute("SELECT id, name, team, contract_expires_year FROM players WHERE contract_expires_year IS NOT NULL AND (contract_expires_year < 2024 OR contract_expires_year > 2036)")
    bad_contracts = cursor.fetchall()
    if bad_contracts:
        failures.append(f"Found {len(bad_contracts)} players with anomalous contract expiry year: {[(r['name'], r['contract_expires_year']) for r in bad_contracts]}")
    else:
        passed_checks.append("Zero anomalous contract expiration years")

    # 4.8: Negative core stats
    cursor.execute("""
        SELECT id, name, team, appearances, minutes_played, goals, assists, yellow_cards, red_cards
        FROM players
        WHERE appearances < 0 OR minutes_played < 0 OR goals < 0 OR assists < 0 OR yellow_cards < 0 OR red_cards < 0
    """)
    bad_stats = cursor.fetchall()
    if bad_stats:
        failures.append(f"Found {len(bad_stats)} players with negative match statistics")
    else:
        passed_checks.append("Zero negative match statistics")

    # 4.9: Foreign Key / Referential Integrity
    cursor.execute("""
        SELECT COUNT(*) as orphan_count
        FROM player_competition_stats
        WHERE player_id NOT IN (SELECT id FROM players)
    """)
    orphan_row = cursor.fetchone()
    orphan_count = orphan_row["orphan_count"] if orphan_row else 0
    if orphan_count > 0:
        failures.append(f"Found {orphan_count} orphaned records in player_competition_stats referencing non-existent player_id")
    else:
        passed_checks.append("Zero orphaned records in player_competition_stats")

    # -------------------------------------------------------------------------
    # TEST 5: Lower Division & Relegated Club Leakage Test
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Lower Division & Relegated Club Leakage Stress Test...")
    
    relegated_clubs = [
        # Premier League relegated
        "Burnley", "Burnley FC", "Luton Town", "Luton", "Sheffield United", "Sheffield Utd",
        # La Liga relegated
        "Cádiz", "Cadiz", "Cádiz CF", "Cadiz CF", "Almería", "Almeria", "UD Almería", "Granada", "Granada CF",
        # Serie A relegated
        "Salernitana", "US Salernitana 1919", "Sassuolo", "US Sassuolo", "Frosinone", "Frosinone Calcio",
        # Bundesliga relegated
        "1. FC Köln", "FC Köln", "Köln", "Koln", "1. FC Koln", "SV Darmstadt 98", "Darmstadt 98", "Darmstadt",
        # Ligue 1 relegated
        "FC Metz", "Metz", "FC Lorient", "Lorient", "Clermont Foot", "Clermont Foot 63", "Clermont"
    ]

    cursor.execute("""
        SELECT DISTINCT team, league
        FROM players
        WHERE league IN ('Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1')
    """)
    top5_clubs = cursor.fetchall()
    top5_team_names = [r["team"] for r in top5_clubs]

    leaked_relegated = []
    for rel in relegated_clubs:
        for t in top5_team_names:
            if normalize_text(rel) == normalize_text(t):
                leaked_relegated.append((t, rel))

    if leaked_relegated:
        failures.append(f"Found {len(leaked_relegated)} relegated clubs misclassified in Top 5 leagues: {leaked_relegated}")
    else:
        passed_checks.append("Zero relegated/lower division clubs leaked into Top 5 leagues")

    # Print full list of 96 clubs grouped by league
    print("\nComplete Top 5 League Roster Breakdown (96 Clubs):")
    for lg in expected_leagues:
        cursor.execute("SELECT team, COUNT(*) as cnt FROM players WHERE league = ? GROUP BY team ORDER BY team", (lg,))
        teams_in_lg = cursor.fetchall()
        print(f"\n--- {lg} ({len(teams_in_lg)} clubs) ---")
        for t in teams_in_lg:
            print(f"  - {t['team']}: {t['cnt']} players")

    # -------------------------------------------------------------------------
    # TEST 6: 2025/2026 Mega-Transfers & Departures Stress Test (50+ Transfers, 40+ Departures)
    # -------------------------------------------------------------------------
    print("\n[TEST 6] 2025/2026 Mega-Transfers & Departures Adversarial Oracle (50+ Transfers, 40+ Departures)...")

    mega_transfers = [
        # Premier League Transfers
        ("Kylian Mbappé", "Real Madrid", ["Paris Saint-Germain", "PSG"]),
        ("Julián Álvarez", "Atlético Madrid", ["Manchester City", "Man City"]),
        ("Dani Olmo", "FC Barcelona", ["RB Leipzig"]),
        ("Riccardo Calafiori", "Arsenal", ["Bologna"]),
        ("Mikel Merino", "Arsenal", ["Real Sociedad"]),
        ("Raheem Sterling", "Arsenal", ["Chelsea"]),
        ("Pedro Neto", "Chelsea", ["Wolverhampton Wanderers", "Wolves"]),
        ("Jadon Sancho", "Chelsea", ["Manchester United", "Man Utd", "Borussia Dortmund"]),
        ("João Félix", "Chelsea", ["Atlético Madrid", "FC Barcelona", "Barcelona"]),
        ("Kieran Dewsbury-Hall", "Chelsea", ["Leicester City"]),
        ("Matthijs de Ligt", "Manchester United", ["Bayern Munich", "FC Bayern München"]),
        ("Noussair Mazraoui", "Manchester United", ["Bayern Munich", "FC Bayern München"]),
        ("Leny Yoro", "Manchester United", ["Lille", "LOSC Lille"]),
        ("Manuel Ugarte", "Manchester United", ["Paris Saint-Germain", "PSG"]),
        ("Joshua Zirkzee", "Manchester United", ["Bologna"]),
        ("Federico Chiesa", "Liverpool", ["Juventus"]),
        ("Dominic Solanke", "Tottenham Hotspur", ["Bournemouth"]),
        ("Wilson Odobert", "Tottenham Hotspur", ["Burnley"]),
        ("Archie Gray", "Tottenham Hotspur", ["Leeds United"]),
        ("Lucas Bergvall", "Tottenham Hotspur", ["Djurgårdens"]),
        ("Amadou Onana", "Aston Villa", ["Everton"]),
        ("Ian Maatsen", "Aston Villa", ["Chelsea", "Borussia Dortmund"]),
        ("Ross Barkley", "Aston Villa", ["Luton Town"]),
        ("Jaden Philogene", "Aston Villa", ["Hull City"]),
        ("Lewis Hall", "Newcastle United", ["Chelsea"]),
        ("William Osula", "Newcastle United", ["Sheffield United"]),
        ("Lloyd Kelly", "Newcastle United", ["Bournemouth"]),
        ("Georginio Rutter", "Brighton & Hove Albion", ["Leeds United"]),
        ("Yankuba Minteh", "Brighton & Hove Albion", ["Newcastle United", "Feyenoord"]),
        ("Ferdi Kadıoğlu", "Brighton & Hove Albion", ["Fenerbahçe", "Fenerbahce"]),
        ("Mats Wieffer", "Brighton & Hove Albion", ["Feyenoord"]),
        ("Matt O'Riley", "Brighton & Hove Albion", ["Celtic"]),
        ("Brajan Gruda", "Brighton & Hove Albion", ["FSV Mainz 05", "Mainz"]),
        ("Crysencio Summerville", "West Ham United", ["Leeds United"]),
        ("Max Kilman", "West Ham United", ["Wolverhampton Wanderers"]),
        ("Niclas Füllkrug", "West Ham United", ["Borussia Dortmund"]),
        ("Jean-Clair Todibo", "West Ham United", ["OGC Nice", "Nice"]),
        ("Aaron Wan-Bissaka", "West Ham United", ["Manchester United"]),
        ("Guido Rodríguez", "West Ham United", ["Real Betis"]),
        ("Eddie Nketiah", "Crystal Palace", ["Arsenal"]),
        ("Daichi Kamada", "Crystal Palace", ["Lazio"]),
        ("Ismaïla Sarr", "Crystal Palace", ["Marseille", "Olympique de Marseille"]),
        ("Chadi Riad", "Crystal Palace", ["Real Betis", "Barcelona"]),

        # Bundesliga Transfers
        ("Michael Olise", "Bayern Munich", ["Crystal Palace"]),
        ("João Palhinha", "Bayern Munich", ["Fulham"]),
        ("Hiroki Ito", "Bayern Munich", ["VfB Stuttgart"]),
        ("Serhou Guirassy", "Borussia Dortmund", ["VfB Stuttgart"]),
        ("Waldemar Anton", "Borussia Dortmund", ["VfB Stuttgart"]),
        ("Pascal Groß", "Borussia Dortmund", ["Brighton & Hove Albion", "Brighton"]),
        ("Maximilian Beier", "Borussia Dortmund", ["TSG Hoffenheim", "Hoffenheim"]),
        ("Yan Couto", "Borussia Dortmund", ["Girona", "Manchester City"]),
        ("Martin Terrier", "Bayer Leverkusen", ["Rennes", "Stade Rennais"]),
        ("Aleix García", "Bayer Leverkusen", ["Girona"]),
        ("Jeanuël Belocian", "Bayer Leverkusen", ["Rennes", "Stade Rennais"]),
        ("Nordi Mukiele", "Bayer Leverkusen", ["Paris Saint-Germain", "PSG"]),
        ("Benjamin Šeško", "RB Leipzig", ["Red Bull Salzburg"]),
        ("Antonio Nusa", "RB Leipzig", ["Club Brugge"]),
        ("Lutsharel Geertruida", "RB Leipzig", ["Feyenoord"]),
        ("Arthur Vermeeren", "RB Leipzig", ["Atlético Madrid", "Royal Antwerp"]),
        ("Deniz Undav", "VfB Stuttgart", ["Brighton & Hove Albion"]),
        ("Ermedin Demirović", "VfB Stuttgart", ["FC Augsburg", "Augsburg"]),
        ("Jeff Chabot", "VfB Stuttgart", ["1. FC Köln", "Köln"]),

        # Serie A Transfers
        ("Teun Koopmeiners", "Juventus", ["Atalanta"]),
        ("Douglas Luiz", "Juventus", ["Aston Villa"]),
        ("Khéphren Thuram", "Juventus", ["OGC Nice", "Nice"]),
        ("Nicolás González", "Juventus", ["Fiorentina"]),
        ("Pierre Kalulu", "Juventus", ["AC Milan"]),
        ("Francisco Conceição", "Juventus", ["FC Porto", "Porto"]),
        ("Michele Di Gregorio", "Juventus", ["Monza"]),
        ("Juan Cabal", "Juventus", ["Hellas Verona"]),
        ("Romelu Lukaku", "Napoli", ["Chelsea", "AS Roma", "Roma", "Inter Milan"]),
        ("Scott McTominay", "Napoli", ["Manchester United", "Man Utd"]),
        ("Billy Gilmour", "Napoli", ["Brighton & Hove Albion"]),
        ("David Neres", "Napoli", ["Benfica"]),
        ("Alessandro Buongiorno", "Napoli", ["Torino"]),
        ("Leonardo Spinazzola", "Napoli", ["AS Roma"]),
        ("Rafa Marín", "Napoli", ["Real Madrid", "Deportivo Alavés"]),
        ("Álvaro Morata", "AC Milan", ["Atlético Madrid"]),
        ("Youssouf Fofana", "AC Milan", ["AS Monaco", "Monaco"]),
        ("Strahinja Pavlović", "AC Milan", ["Red Bull Salzburg"]),
        ("Emerson Royal", "AC Milan", ["Tottenham Hotspur"]),
        ("Tammy Abraham", "AC Milan", ["AS Roma"]),
        ("Piotr Zieliński", "Inter Milan", ["Napoli"]),
        ("Mehdi Taremi", "Inter Milan", ["FC Porto"]),
        ("Josep Martínez", "Inter Milan", ["Genoa"]),
        ("Artem Dovbyk", "AS Roma", ["Girona"]),
        ("Matías Soulé", "AS Roma", ["Juventus", "Frosinone"]),
        ("Enzo Le Fée", "AS Roma", ["Rennes", "Stade Rennais"]),
        ("Manu Koné", "AS Roma", ["Borussia Mönchengladbach"]),
        ("Alexis Saelemaekers", "AS Roma", ["AC Milan", "Bologna"]),
        ("Mats Hummels", "AS Roma", ["Borussia Dortmund"]),
        ("Mario Hermoso", "AS Roma", ["Atlético Madrid"]),
        ("Mateo Retegui", "Atalanta", ["Genoa"]),
        ("Charles De Ketelaere", "Atalanta", ["AC Milan"]),
        ("Raoul Bellanova", "Atalanta", ["Torino"]),
        ("Odilon Kossounou", "Atalanta", ["Bayer Leverkusen"]),
        ("Lazar Samardžić", "Atalanta", ["Udinese"]),
        ("Nicolò Zaniolo", "Atalanta", ["Galatasaray", "Aston Villa"]),
        ("Ben Godfrey", "Atalanta", ["Everton"]),
        ("Juan Cuadrado", "Atalanta", ["Inter Milan"]),
        ("Rui Patrício", "Atalanta", ["AS Roma"]),
        ("Moise Kean", "Fiorentina", ["Juventus"]),
        ("Albert Guðmundsson", "Fiorentina", ["Genoa"]),
        ("David De Gea", "Fiorentina", ["Manchester United"]),
        ("Robin Gosens", "Fiorentina", ["Union Berlin", "Inter Milan"]),
        ("Andrea Colpani", "Fiorentina", ["Monza"]),
        ("Amir Richardson", "Fiorentina", ["Stade de Reims"]),
        ("Marin Pongračić", "Fiorentina", ["Lecce"]),
        ("Edoardo Bove", "Fiorentina", ["AS Roma"]),
        ("Danilo Cataldi", "Fiorentina", ["Lazio"]),
        ("Yacine Adli", "Fiorentina", ["AC Milan"]),
        ("Sergi Roberto", "Como", ["FC Barcelona", "Barcelona"]),
        ("Nico Paz", "Como", ["Real Madrid"]),
        ("Gabriel Strefezza", "Como", ["Lecce"]),
        ("Alberto Moreno", "Como", ["Villarreal"]),
        ("Pepe Reina", "Como", ["Villarreal"]),

        # La Liga Transfers
        ("Conor Gallagher", "Atlético Madrid", ["Chelsea"]),
        ("Alexander Sørloth", "Atlético Madrid", ["Villarreal"]),
        ("Robin Le Normand", "Atlético Madrid", ["Real Sociedad"]),
        ("Clément Lenglet", "Atlético Madrid", ["Barcelona", "Aston Villa"]),
        ("Juan Musso", "Atlético Madrid", ["Atalanta"]),
        ("Endrick", "Real Madrid", ["Palmeiras"]),
        ("Pau Víctor", "FC Barcelona", ["Girona"]),
        ("Wojciech Szczęsny", "FC Barcelona", ["Juventus"]),
        ("James Rodríguez", "Rayo Vallecano", ["São Paulo"]),

        # Ligue 1 Transfers
        ("João Neves", "Paris Saint-Germain", ["Benfica"]),
        ("Willian Pacho", "Paris Saint-Germain", ["Eintracht Frankfurt"]),
        ("Désiré Doué", "Paris Saint-Germain", ["Stade Rennais", "Rennes"]),
        ("Matvey Safonov", "Paris Saint-Germain", ["Krasnodar"]),
        ("Lucas Beraldo", "Paris Saint-Germain", ["São Paulo"]),
        ("Mason Greenwood", "Olympique de Marseille", ["Manchester United", "Getafe"]),
        ("Pierre-Emile Højbjerg", "Olympique de Marseille", ["Tottenham Hotspur"]),
        ("Adrien Rabiot", "Olympique de Marseille", ["Juventus"]),
        ("Gerónimo Rulli", "Olympique de Marseille", ["Ajax"]),
        ("Elye Wahi", "Olympique de Marseille", ["RC Lens", "Lens"]),
        ("Jonathan Rowe", "Olympique de Marseille", ["Norwich City"]),
        ("Neal Maupay", "Olympique de Marseille", ["Everton", "Brentford"]),
        ("Lilian Brassier", "Olympique de Marseille", ["Stade Brestois 29"]),
        ("Ismaël Koné", "Olympique de Marseille", ["Watford"]),
        ("Derek Cornelius", "Olympique de Marseille", ["Malmö FF"]),
        ("Valentin Carboni", "Olympique de Marseille", ["Inter Milan", "Monza"]),
        ("Georges Mikautadze", "Olympique Lyonnais", ["FC Metz", "Ajax"]),
        ("Moussa Niakhaté", "Olympique Lyonnais", ["Nottingham Forest"]),
        ("Ernest Nuamah", "Olympique Lyonnais", ["RWD Molenbeek"]),
        ("Saïd Benrahma", "Olympique Lyonnais", ["West Ham United"]),
        ("Abner Vinícius", "Olympique Lyonnais", ["Real Betis"]),
        ("Wilfried Zaha", "Olympique Lyonnais", ["Galatasaray", "Crystal Palace"]),
        ("Tanner Tessmann", "Olympique Lyonnais", ["Venezia"]),
        ("Jordan Veretout", "Olympique Lyonnais", ["Olympique de Marseille"]),
        ("Warmed Omari", "Olympique Lyonnais", ["Stade Rennais"]),
        ("George Ilenikhena", "AS Monaco", ["Royal Antwerp"]),
        ("Lamine Camara", "AS Monaco", ["FC Metz"]),
        ("Christian Mawissa", "AS Monaco", ["Toulouse FC"]),
        ("Jordan Teze", "AS Monaco", ["PSV Eindhoven"]),
        ("Thilo Kehrer", "AS Monaco", ["West Ham United"]),
        ("Tanguy Ndombele", "OGC Nice", ["Tottenham Hotspur", "Galatasaray"]),
        ("Jonathan Clauss", "OGC Nice", ["Olympique de Marseille"]),
        ("Youssoufa Moukoko", "OGC Nice", ["Borussia Dortmund"]),
        ("Moïse Bombito", "OGC Nice", ["Colorado Rapids"]),
        ("Mohamed Abdelmonem", "OGC Nice", ["Al Ahly"]),
        ("Thomas Meunier", "Lille OSC", ["Trabzonspor", "Borussia Dortmund"]),
        ("Osame Sahraoui", "Lille OSC", ["Heerenveen"]),
        ("Aïssa Mandi", "Lille OSC", ["Villarreal"])
    ]

    print(f"Total Transfers Tested in Oracle: {len(mega_transfers)}")
    for name, expected_team, forbidden_teams in mega_transfers:
        norm_name = normalize_text(name)
        cursor.execute("SELECT id, name, team, league FROM players")
        all_p = cursor.fetchall()
        matches = [p for p in all_p if normalize_text(p["name"]) == norm_name]
        
        if not matches:
            # Try last name matching
            last_token = norm_name.split()[-1]
            matches = [p for p in all_p if last_token in normalize_text(p["name"]) and len(last_token) > 4]

        if not matches:
            failures.append(f"Transfer player '{name}' not found anywhere in database")
        else:
            curr_teams = [p["team"] for p in matches]
            norm_exp = normalize_text(expected_team)
            if not any(norm_exp in normalize_text(t) or normalize_text(t) in norm_exp for t in curr_teams):
                failures.append(f"Transfer player '{name}' expected at '{expected_team}', but found at {curr_teams}")
            else:
                passed_checks.append(f"Transfer confirmed: '{name}' -> '{expected_team}'")

            for f_team in forbidden_teams:
                norm_f = normalize_text(f_team)
                if any(norm_f in normalize_text(t) for t in curr_teams):
                    failures.append(f"Transfer player '{name}' still lingers at legacy club '{f_team}'")

    # -------------------------------------------------------------------------
    # TEST 7: Experimental Test Artifacts Zero-Check
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Experimental Test Artifacts Sanitization Audit...")
    ARTIFACT_ASSERTIONS = [
        ("Kevin De Bruyne", "Manchester City", ["Napoli"]),
        ("Rodri", "Manchester City", ["FC Barcelona", "Barcelona"]),
        ("Bradley Barcola", "Paris Saint-Germain", ["Liverpool"]),
        ("Savinho", "Manchester City", ["Tottenham Hotspur", "Tottenham"]),
        ("Emiliano Martínez", "Aston Villa", ["Chelsea"]),
        ("Carlos Baleba", "Brighton & Hove Albion", ["Manchester United", "Man Utd"]),
        ("Ezri Konsa", "Aston Villa", ["Arsenal"]),
        ("Bruno Guimarães", "Newcastle United", ["Arsenal"]),
        ("Maxence Lacroix", "Crystal Palace", ["Chelsea"]),
        ("Morgan Rogers", "Aston Villa", ["Chelsea"]),
        ("Nicolás González", "Juventus", ["Newcastle United"])
    ]

    for art_name, correct_club, forbidden_clubs in ARTIFACT_ASSERTIONS:
        norm_art = normalize_text(art_name)
        cursor.execute("SELECT id, name, team, league FROM players")
        all_p = cursor.fetchall()
        matches = [p for p in all_p if normalize_text(p["name"]) == norm_art]
        
        if not matches:
            last_tok = norm_art.split()[-1]
            matches = [p for p in all_p if last_tok in normalize_text(p["name"]) and len(last_tok) > 4]

        if not matches:
            failures.append(f"Artifact audit player '{art_name}' not found in database")
        else:
            curr_teams = [p["team"] for p in matches]
            norm_corr = normalize_text(correct_club)
            if not any(norm_corr in normalize_text(t) or normalize_text(t) in norm_corr for t in curr_teams):
                failures.append(f"Experimental Artifact Violation: '{art_name}' assigned to {curr_teams}, expected '{correct_club}'")
            else:
                passed_checks.append(f"Artifact clean: '{art_name}' properly positioned at '{correct_club}'")

            for f_club in forbidden_clubs:
                norm_fc = normalize_text(f_club)
                if any(norm_fc in normalize_text(t) for t in curr_teams):
                    failures.append(f"Experimental Artifact Leaked: '{art_name}' still assigned to hallucinated club '{f_club}'")

    # Henderson check: must not be in Top 5 (Chelsea / Liverpool)
    cursor.execute("SELECT id, name, team, league FROM players WHERE name LIKE '%Henderson%' AND league IN ('Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1')")
    hendersons = cursor.fetchall()
    for h in hendersons:
        if "jordan" in normalize_text(h["name"]):
            failures.append(f"Experimental Artifact Leaked: Jordan Henderson found in Top 5 at '{h['team']}' ({h['league']})")
    if not any("jordan" in normalize_text(h["name"]) for h in hendersons):
        passed_checks.append("Artifact clean: Jordan Henderson 0 records in Top 5 leagues")

    # -------------------------------------------------------------------------
    # TEST 8: Global Departures & Contract Expirations Zero-Check (50+ Players)
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Global Departures & Retired Zero-Check (50+ Players across 8 non-Top-5 regions)...")
    departures = [
        # Saudi Pro League
        ("Cristiano Ronaldo", "Al Nassr / Saudi Pro League"),
        ("Karim Benzema", "Al Ittihad / Saudi Pro League"),
        ("Neymar Jr", "Al Hilal / Saudi Pro League"),
        ("Sadio Mané", "Al Nassr / Saudi Pro League"),
        ("Riyad Mahrez", "Al Ahli / Saudi Pro League"),
        ("Roberto Firmino", "Al Ahli / Saudi Pro League"),
        ("Ivan Toney", "Al Ahli / Saudi Pro League"),
        ("Moussa Diaby", "Al Ittihad / Saudi Pro League"),
        ("João Cancelo", "Al Hilal / Saudi Pro League"),
        ("N'Golo Kanté", "Al Ittihad / Saudi Pro League"),
        ("Fabinho", "Al Ittihad / Saudi Pro League"),
        ("Rúben Neves", "Al Hilal / Saudi Pro League"),
        ("Sergej Milinković-Savić", "Al Hilal / Saudi Pro League"),
        ("Kalidou Koulibaly", "Al Hilal / Saudi Pro League"),
        ("Aymeric Laporte", "Al Nassr / Saudi Pro League"),
        ("Marcelo Brozović", "Al Nassr / Saudi Pro League"),
        ("Yannick Carrasco", "Al Shabab / Saudi Pro League"),
        ("Franck Kessié", "Al Ahli / Saudi Pro League"),
        ("Édouard Mendy", "Al Ahli / Saudi Pro League"),
        ("Gabri Veiga", "Al Ahli / Saudi Pro League"),
        ("Merih Demiral", "Al Ahli / Saudi Pro League"),
        ("Otávio", "Al Nassr / Saudi Pro League"),
        ("Malcom", "Al Hilal / Saudi Pro League"),
        ("Renan Lodi", "Al Hilal / Saudi Pro League"),
        ("Houssem Aouar", "Al Ittihad / Saudi Pro League"),
        ("Danilo Pereira", "Al Ittihad / Saudi Pro League"),
        ("Steven Bergwijn", "Al Ittihad / Saudi Pro League"),
        ("Mohamed Simakan", "Al Nassr / Saudi Pro League"),
        ("Marcos Leonardo", "Al Hilal / Saudi Pro League"),
        ("Daniel Podence", "Al Shabab / Saudi Pro League"),
        ("Giacomo Bonaventura", "Al Shabab / Saudi Pro League"),
        ("Kurt Zouma", "Al Orobah / Saudi Pro League"),
        ("Chris Smalling", "Al Fayha / Saudi Pro League"),
        ("Cameron Puertas", "Al Qadsiah / Saudi Pro League"),
        ("Ezequiel Fernández", "Al Qadsiah / Saudi Pro League"),
        ("Koen Casteels", "Al Qadsiah / Saudi Pro League"),
        ("Nacho", "Al Qadsiah / Saudi Pro League"),
        ("Nacho Fernández", "Al Qadsiah / Saudi Pro League"),
        ("Julián Quiñones", "Al Qadsiah / Saudi Pro League"),
        ("Pierre-Emerick Aubameyang", "Al Qadsiah / Saudi Pro League"),

        # Qatar
        ("Joselu", "Al Gharafa / Qatar"),
        ("Marco Verratti", "Al Arabi / Qatar"),
        ("Julian Draxler", "Al Ahli SC / Qatar"),
        ("Rafinha", "Al Arabi / Qatar"),

        # MLS
        ("Olivier Giroud", "LAFC / MLS"),
        ("Marco Reus", "LA Galaxy / MLS"),
        ("Hugo Lloris", "LAFC / MLS"),
        ("Emil Forsberg", "New York Red Bulls / MLS"),
        ("Lionel Messi", "Inter Miami / MLS"),
        ("Sergio Busquets", "Inter Miami / MLS"),
        ("Jordi Alba", "Inter Miami / MLS"),
        ("Luis Suárez", "Inter Miami / MLS"),
        ("Luis Muriel", "Orlando City / MLS"),
        ("Christian Benteke", "D.C. United / MLS"),
        ("Lorenzo Insigne", "Toronto FC / MLS"),
        ("Federico Bernardeschi", "Toronto FC / MLS"),

        # Brazil
        ("Memphis Depay", "Corinthians / Brazil"),
        ("Thiago Silva", "Fluminense / Brazil"),
        ("Felipe Anderson", "Palmeiras / Brazil"),
        ("Philippe Coutinho", "Vasco da Gama / Brazil"),
        ("Alex Sandro", "Flamengo / Brazil"),
        ("Carlos Alcaraz", "Flamengo / Brazil"),
        ("Vitinho", "Botafogo / Brazil"),
        ("Matheus Martins", "Botafogo / Brazil"),
        ("Luiz Henrique", "Botafogo / Brazil"),
        ("Thiago Almada", "Botafogo / Brazil"),

        # Turkey
        ("Victor Osimhen", "Galatasaray / Turkey"),
        ("Ciro Immobile", "Beşiktaş / Turkey"),
        ("Sofyan Amrabat", "Fenerbahçe / Turkey"),
        ("Allan Saint-Maximin", "Fenerbahçe / Turkey"),
        ("Fred", "Fenerbahçe / Turkey"),
        ("Dušan Tadić", "Fenerbahçe / Turkey"),
        ("Edin Džeko", "Fenerbahçe / Turkey"),
        ("Youssef En-Nesyri", "Fenerbahçe / Turkey"),
        ("Sebastian Szymański", "Fenerbahçe / Turkey"),
        ("Dominik Livaković", "Fenerbahçe / Turkey"),
        ("Mauro Icardi", "Galatasaray / Turkey"),
        ("Dries Mertens", "Galatasaray / Turkey"),
        ("Lucas Torreira", "Galatasaray / Turkey"),
        ("Davinson Sánchez", "Galatasaray / Turkey"),
        ("Hakim Ziyech", "Galatasaray / Turkey"),
        ("Michy Batshuayi", "Galatasaray / Turkey"),
        ("Gabriel Sara", "Galatasaray / Turkey"),
        ("Rafa Silva", "Beşiktaş / Turkey"),
        ("João Mário", "Beşiktaş / Turkey"),
        ("Cher Ndour", "Beşiktaş / Turkey"),
        ("Arthur Masuaku", "Beşiktaş / Turkey"),
        ("Simon Banza", "Trabzonspor / Turkey"),
        ("Stefan Savić", "Trabzonspor / Turkey"),

        # Greece
        ("Anthony Martial", "AEK Athens / Greece"),
        ("Erik Lamela", "AEK Athens / Greece"),
        ("Roberto Pereyra", "AEK Athens / Greece"),
        ("Willian", "Olympiacos / Greece"),
        ("Sérgio Oliveira", "Olympiacos / Greece"),
        ("Dani García", "Olympiacos / Greece"),
        ("David Carmo", "Olympiacos / Greece"),
        ("Facundo Pellistri", "Panathinaikos / Greece"),
        ("Azzedine Ounahi", "Panathinaikos / Greece"),
        ("Tetê", "Panathinaikos / Greece"),
        ("Dejan Lovren", "PAOK / Greece"),
        ("Tiémoué Bakayoko", "PAOK / Greece"),
        ("Shola Shoretire", "PAOK / Greece"),
        ("Jonny Otto", "PAOK / Greece"),

        # Retired / Free Agents / Eredivisie
        ("Jordan Henderson", "Ajax / Departed"),
        ("Toni Kroos", "Retired"),
        ("Raphaël Varane", "Retired"),
        ("Thiago Alcântara", "Retired"),
        ("Pepe", "Retired"),
        ("Eden Hazard", "Retired"),
        ("Zlatan Ibrahimović", "Retired"),
        ("Giorgio Chiellini", "Retired"),
        ("Leonardo Bonucci", "Retired"),
        ("Claudio Bravo", "Retired"),
        ("Sergio Ramos", "Free Agent / Departed"),
        ("Joel Matip", "Free Agent / Retired"),
        ("Keylor Navas", "Free Agent / Departed"),
        ("Wissam Ben Yedder", "Free Agent / Departed")
    ]

    print(f"Total Global Departures Tested: {len(departures)}")
    cursor.execute("SELECT id, name, team, league FROM players WHERE league IN ('Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1')")
    top5_all = cursor.fetchall()

    for dep_name, dest in departures:
        norm_dep = normalize_text(dep_name)
        violations = []
        for p in top5_all:
            p_norm = normalize_text(p["name"])
            if norm_dep == p_norm or (" " in dep_name and norm_dep in p_norm and len(norm_dep) > 6):
                violations.append(p)
            elif dep_name in ["Nacho", "Joselu"] and p_norm in [norm_dep, f"{norm_dep} fernandez", f"{norm_dep} mato"]:
                violations.append(p)

        if violations:
            failures.append(f"Global departure '{dep_name}' [{dest}] still lingering in Top 5: {[(v['name'], v['team'], v['league']) for v in violations]}")
        else:
            passed_checks.append(f"Confirmed departure purged: '{dep_name}' [{dest}]")

    # -------------------------------------------------------------------------
    # FINAL VERDICT
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("EMPIRICAL CHALLENGER VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Total Passed Assertions: {len(passed_checks)}")
    print(f"Total Warnings: {len(warnings)}")
    print(f"Total Failures: {len(failures)}")

    if failures:
        print("\n[!!!] FAILURES DETECTED:")
        for f in failures:
            print(f"  - FAIL: {f}")
        print("\nFINAL VERDICT: REQUEST_CHANGES")
    else:
        print("\n[***] ALL ADVERSARIAL STRESS-TESTS PASSED (0 FAILURES) [***]")
        print("FINAL VERDICT: APPROVE")

    conn.close()
    return len(failures) == 0

if __name__ == "__main__":
    success = run_adversarial_tests()
    sys.exit(0 if success else 1)

