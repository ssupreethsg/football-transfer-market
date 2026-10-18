import sqlite3
import random

conn = sqlite3.connect("sql_app.db")
c = conn.cursor()

c.execute("SELECT max(id) FROM players")
curr_p_id = c.fetchone()[0] or 3500

c.execute("SELECT max(id) FROM player_competition_stats")
curr_c_id = c.fetchone()[0] or 7000

c.execute("SELECT lower(name) FROM players")
existing_names = set(row[0] for row in c.fetchall())

TOP_UP_PLAYERS = [
    # Werder Bremen (+7)
    ("Amos Pieper", "Germany", 28, "DEF", "Bundesliga", "Werder Bremen", 1890, 1, 0, 10, 3, 4, 48, 38, 92, 18, 4, 0, 2027, None, 30000),
    ("Derrick Köhn", "Germany", 27, "DEF", "Bundesliga", "Werder Bremen", 1980, 2, 3, 20, 6, 28, 54, 32, 42, 11, 3, 0, 2028, None, 32000),
    ("Felix Agu", "Germany", 26, "DEF", "Bundesliga", "Werder Bremen", 2160, 2, 2, 16, 5, 26, 62, 36, 44, 12, 4, 0, 2027, None, 28000),
    ("Keke Topp", "Germany", 22, "FWD", "Bundesliga", "Werder Bremen", 1620, 5, 2, 38, 16, 18, 22, 10, 12, 3, 2, 0, 2028, None, 25000),
    ("Julian Malatini", "Argentina", 25, "DEF", "Bundesliga", "Werder Bremen", 1710, 1, 0, 8, 2, 4, 44, 34, 86, 16, 3, 0, 2028, None, 24000),
    ("Skelly Alvero", "France", 24, "MID", "Bundesliga", "Werder Bremen", 1800, 2, 1, 18, 5, 20, 58, 36, 42, 14, 4, 0, 2028, None, 25000),
    ("Mio Backhaus", "Germany", 22, "GK", "Bundesliga", "Werder Bremen", 630, 0, 0, 0, 0, 0, 1, 0, 14, 0, 0, 0, 2028, None, 18000),

    # Lecce (+10)
    ("Balthazar Pierret", "France", 26, "MID", "Serie A", "Lecce", 1980, 2, 1, 20, 6, 24, 68, 42, 38, 14, 5, 0, 2027, None, 25000),
    ("Lassana Coulibaly", "Mali", 30, "MID", "Serie A", "Lecce", 2160, 2, 2, 22, 7, 28, 76, 46, 42, 16, 6, 0, 2027, None, 28000),
    ("Santiago Pierotti", "Argentina", 25, "FWD", "Serie A", "Lecce", 1890, 4, 2, 36, 14, 26, 28, 12, 14, 4, 3, 0, 2028, None, 25000),
    ("Medon Berisha", "Albania", 22, "MID", "Serie A", "Lecce", 1710, 2, 3, 24, 8, 32, 54, 30, 24, 10, 3, 0, 2028, None, 20000),
    ("Andy Pelmard", "France", 26, "DEF", "Serie A", "Lecce", 1800, 1, 1, 10, 3, 16, 52, 34, 46, 11, 4, 0, 2027, None, 24000),
    ("Christian Früchtl", "Germany", 26, "GK", "Serie A", "Lecce", 630, 0, 0, 0, 0, 0, 1, 0, 16, 0, 0, 0, 2027, None, 20000),
    ("Gaby Jean", "France", 26, "DEF", "Serie A", "Lecce", 1620, 1, 0, 8, 2, 4, 46, 36, 88, 18, 3, 0, 2027, None, 20000),
    ("Thorir Johann Helgason", "Iceland", 25, "MID", "Serie A", "Lecce", 1530, 2, 2, 18, 6, 22, 48, 28, 22, 8, 3, 0, 2027, None, 20000),
    ("Tete Morente", "Spain", 29, "FWD", "Serie A", "Lecce", 2070, 5, 3, 44, 16, 36, 32, 14, 14, 4, 4, 0, 2027, None, 28000),
    ("Filip Marchwiński", "Poland", 24, "MID", "Serie A", "Lecce", 1890, 4, 3, 38, 14, 38, 44, 22, 16, 6, 3, 0, 2028, None, 25000),

    # Parma (+8)
    ("Woyo Coulibaly", "France", 27, "DEF", "Serie A", "Parma", 2070, 1, 2, 12, 3, 22, 62, 36, 44, 12, 4, 0, 2027, None, 25000),
    ("Nahuel Estévez", "Argentina", 30, "MID", "Serie A", "Parma", 2250, 2, 2, 24, 7, 28, 78, 48, 38, 16, 7, 0, 2026, None, 30000),
    ("Drissa Camara", "Ivory Coast", 24, "MID", "Serie A", "Parma", 1800, 3, 2, 28, 10, 32, 58, 34, 26, 11, 4, 0, 2027, None, 22000),
    ("Antoine Hainaut", "France", 24, "MID", "Serie A", "Parma", 1620, 1, 2, 16, 5, 24, 52, 28, 24, 9, 3, 0, 2027, None, 20000),
    ("Gabriel Charpentier", "Congo", 27, "FWD", "Serie A", "Parma", 1530, 5, 2, 36, 15, 18, 20, 8, 12, 3, 2, 0, 2026, None, 25000),
    ("Botond Balogh", "Hungary", 24, "DEF", "Serie A", "Parma", 1980, 1, 0, 10, 3, 4, 52, 40, 94, 20, 3, 0, 2027, None, 22000),
    ("Gianluca Di Chiara", "Italy", 32, "DEF", "Serie A", "Parma", 1890, 1, 3, 14, 4, 30, 58, 32, 42, 10, 4, 0, 2026, None, 25000),
    ("Edoardo Corvi", "Italy", 25, "GK", "Serie A", "Parma", 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, 0, 0, 2027, None, 18000),

    # AJ Auxerre (+10)
    ("Paul Joly", "France", 26, "DEF", "Ligue 1", "AJ Auxerre", 2250, 1, 4, 18, 5, 34, 68, 38, 46, 12, 4, 0, 2027, None, 25000),
    ("Kévin Danois", "France", 22, "MID", "Ligue 1", "AJ Auxerre", 1800, 2, 3, 24, 8, 32, 54, 32, 24, 10, 3, 0, 2028, None, 20000),
    ("Rayan Raveloson", "Madagascar", 29, "MID", "Ligue 1", "AJ Auxerre", 2340, 4, 3, 36, 12, 38, 74, 46, 38, 16, 6, 0, 2026, None, 28000),
    ("Florian Ayé", "France", 29, "FWD", "Ligue 1", "AJ Auxerre", 1980, 7, 3, 52, 21, 24, 24, 10, 14, 4, 3, 0, 2026, None, 28000),
    ("Theo Bair", "Canada", 27, "FWD", "Ligue 1", "AJ Auxerre", 1890, 6, 2, 44, 18, 22, 22, 8, 16, 4, 3, 0, 2028, None, 26000),
    ("Ki-Jana Hoever", "Netherlands", 24, "DEF", "Ligue 1", "AJ Auxerre", 1980, 2, 2, 16, 5, 26, 58, 34, 38, 10, 4, 0, 2027, None, 25000),
    ("Gabriel Osho", "Nigeria", 28, "DEF", "Ligue 1", "AJ Auxerre", 2070, 2, 0, 14, 4, 6, 56, 44, 112, 24, 5, 0, 2027, None, 26000),
    ("Clément Akpa", "France", 24, "DEF", "Ligue 1", "AJ Auxerre", 1710, 1, 1, 10, 3, 18, 52, 30, 42, 9, 3, 0, 2027, None, 20000),
    ("Théo De Percin", "France", 25, "GK", "Ligue 1", "AJ Auxerre", 630, 0, 0, 0, 0, 0, 1, 0, 15, 0, 0, 0, 2027, None, 18000),
    ("Aristide Zossou", "Ivory Coast", 21, "MID", "Ligue 1", "AJ Auxerre", 1440, 1, 2, 14, 4, 22, 46, 26, 20, 8, 2, 0, 2028, None, 18000),

    # CD Leganés (+5)
    ("Naim García", "Spain", 24, "FWD", "La Liga", "CD Leganés", 1620, 3, 3, 30, 11, 28, 26, 12, 10, 3, 2, 0, 2027, 20000000, 22000),
    ("Diego García", "Spain", 26, "FWD", "La Liga", "CD Leganés", 1710, 5, 2, 36, 14, 20, 22, 8, 12, 3, 3, 0, 2027, 20000000, 24000),
    ("Lalo Aguilar", "Spain", 24, "DEF", "La Liga", "CD Leganés", 1530, 1, 0, 8, 2, 4, 42, 32, 82, 16, 3, 0, 2027, 15000000, 18000),
    ("Julián Chicco", "Argentina", 28, "MID", "La Liga", "CD Leganés", 1800, 1, 1, 16, 5, 22, 62, 38, 32, 12, 4, 0, 2026, 15000000, 22000),
    ("Alvin Abajas", "Spain", 23, "GK", "La Liga", "CD Leganés", 450, 0, 0, 0, 0, 0, 1, 0, 12, 0, 0, 0, 2027, 10000000, 15000),

    # UD Las Palmas (+5)
    ("Marc Cardona", "Spain", 31, "FWD", "La Liga", "UD Las Palmas", 1620, 4, 2, 34, 13, 22, 22, 8, 12, 3, 3, 0, 2026, 15000000, 28000),
    ("Pejiño", "Spain", 30, "FWD", "La Liga", "UD Las Palmas", 1530, 3, 3, 28, 10, 26, 24, 10, 10, 3, 2, 0, 2026, 15000000, 25000),
    ("Daley Sinkgraven", "Netherlands", 31, "DEF", "La Liga", "UD Las Palmas", 1710, 1, 2, 12, 3, 22, 54, 32, 38, 9, 3, 0, 2026, 15000000, 30000),
    ("Fabio González", "Spain", 29, "MID", "La Liga", "UD Las Palmas", 1620, 1, 1, 14, 4, 20, 56, 34, 28, 10, 4, 0, 2026, 15000000, 24000),
    ("Álvaro Killane", "Argentina", 22, "GK", "La Liga", "UD Las Palmas", 450, 0, 0, 0, 0, 0, 1, 0, 10, 0, 0, 0, 2027, 10000000, 15000),

    # Como (+5)
    ("Alessio Iovine", "Italy", 35, "DEF", "Serie A", "Como", 1710, 1, 2, 12, 3, 22, 52, 30, 36, 8, 4, 0, 2026, None, 25000),
    ("Luca Mazzitelli", "Italy", 30, "MID", "Serie A", "Como", 2070, 3, 3, 32, 10, 34, 68, 42, 34, 14, 6, 0, 2027, None, 35000),
    ("Matthias Braunöder", "Austria", 24, "MID", "Serie A", "Como", 1890, 2, 2, 22, 7, 28, 58, 36, 28, 11, 4, 0, 2028, None, 25000),
    ("Ali Jasim", "Iraq", 22, "FWD", "Serie A", "Como", 1620, 4, 3, 34, 13, 32, 26, 12, 10, 3, 2, 0, 2028, None, 22000),
    ("Oliver Abildgaard", "Denmark", 30, "MID", "Serie A", "Como", 1800, 1, 1, 16, 5, 20, 64, 40, 34, 14, 5, 0, 2026, None, 30000),

    # Girona (+5)
    ("Ladislav Krejčí", "Czech Republic", 27, "DEF", "La Liga", "Girona", 2430, 3, 1, 22, 8, 10, 72, 54, 132, 28, 6, 1, 2029, 45000000, 55000),
    ("Bojan Miovski", "North Macedonia", 27, "FWD", "La Liga", "Girona", 2160, 10, 3, 62, 26, 28, 24, 10, 14, 4, 3, 0, 2028, 35000000, 45000),
    ("Jhon Solís", "Colombia", 21, "MID", "La Liga", "Girona", 1890, 2, 2, 20, 6, 28, 58, 36, 28, 12, 4, 0, 2029, 30000000, 30000),
    ("Pau López", "Spain", 31, "GK", "La Liga", "Girona", 900, 0, 0, 0, 0, 0, 1, 0, 22, 0, 1, 0, 2026, 20000000, 40000),
    ("Gabriel Misehouy", "Netherlands", 21, "MID", "La Liga", "Girona", 1440, 3, 2, 24, 9, 28, 32, 16, 10, 3, 2, 0, 2028, 25000000, 25000),

    # FC St. Pauli (+4)
    ("Scott Banks", "Scotland", 24, "FWD", "Bundesliga", "FC St. Pauli", 1620, 3, 3, 28, 11, 26, 24, 10, 8, 2, 2, 0, 2027, None, 20000),
    ("Adam Dźwigała", "Poland", 30, "DEF", "Bundesliga", "FC St. Pauli", 1710, 1, 0, 10, 3, 4, 46, 36, 88, 18, 3, 0, 2026, None, 22000),
    ("Simon Zoller", "Germany", 35, "FWD", "Bundesliga", "FC St. Pauli", 1260, 3, 1, 24, 9, 14, 16, 6, 10, 2, 1, 0, 2026, None, 20000),
    ("Ben Voll", "Germany", 25, "GK", "Bundesliga", "FC St. Pauli", 450, 0, 0, 0, 0, 0, 1, 0, 12, 0, 0, 0, 2027, None, 15000),

    # Le Havre AC (+5)
    ("Aloïs Confais", "France", 29, "MID", "Ligue 1", "Le Havre AC", 1620, 1, 1, 14, 4, 20, 52, 32, 26, 10, 3, 0, 2026, None, 20000),
    ("Damián Pizarro", "Chile", 21, "FWD", "Ligue 1", "Le Havre AC", 1530, 4, 2, 32, 13, 18, 18, 8, 10, 2, 2, 0, 2028, None, 22000),
    ("Ruben Londja", "Switzerland", 20, "FWD", "Ligue 1", "Le Havre AC", 1350, 3, 2, 26, 10, 20, 16, 6, 8, 2, 1, 0, 2028, None, 18000),
    ("Kandet Diawara", "Guinea", 26, "FWD", "Ligue 1", "Le Havre AC", 1440, 2, 2, 22, 8, 22, 20, 8, 8, 2, 2, 0, 2027, None, 18000),
    ("Paul Argney", "France", 20, "GK", "Ligue 1", "Le Havre AC", 450, 0, 0, 0, 0, 0, 1, 0, 10, 0, 0, 0, 2028, None, 15000),

    # Toulouse FC (+5)
    ("Edhy Zuliani", "Algeria", 22, "FWD", "Ligue 1", "Toulouse FC", 1530, 3, 2, 28, 11, 22, 20, 8, 8, 2, 2, 0, 2028, None, 18000),
    ("Noah Lahmadi", "France", 21, "MID", "Ligue 1", "Toulouse FC", 1440, 1, 2, 16, 5, 24, 46, 26, 20, 8, 2, 0, 2028, None, 18000),
    ("Kévin Keben", "Cameroon", 22, "DEF", "Ligue 1", "Toulouse FC", 1620, 1, 0, 8, 2, 4, 44, 32, 78, 16, 3, 0, 2027, None, 18000),
    ("Ylies Aradj", "France", 21, "DEF", "Ligue 1", "Toulouse FC", 1350, 1, 1, 10, 3, 14, 40, 26, 32, 7, 2, 0, 2028, None, 16000),
    ("Justin Lacombe", "France", 23, "GK", "Ligue 1", "Toulouse FC", 450, 0, 0, 0, 0, 0, 1, 0, 10, 0, 0, 0, 2027, None, 15000),

    # Fulham (+4)
    ("Steven Benda", "Germany", 27, "GK", "Premier League", "Fulham", 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, 0, 0, 2027, None, 25000),
    ("Jorge Cuenca", "Spain", 26, "DEF", "Premier League", "Fulham", 1800, 1, 0, 12, 3, 6, 48, 38, 92, 18, 3, 0, 2028, None, 45000),
    ("Reiss Nelson", "England", 26, "FWD", "Premier League", "Fulham", 1890, 4, 4, 38, 15, 38, 32, 14, 10, 3, 2, 0, 2027, None, 65000),
    ("Josh King", "England", 19, "MID", "Premier League", "Fulham", 990, 1, 2, 14, 5, 20, 34, 18, 14, 5, 1, 0, 2029, None, 20000),

    # Bournemouth (+3)
    ("James Hill", "England", 24, "DEF", "Premier League", "Bournemouth", 1710, 1, 1, 10, 3, 8, 48, 36, 82, 16, 3, 0, 2027, None, 25000),
    ("Max Aarons", "England", 26, "DEF", "Premier League", "Bournemouth", 1980, 1, 3, 16, 5, 28, 62, 34, 42, 11, 4, 0, 2028, None, 40000),
    ("Will Dennis", "England", 26, "GK", "Premier League", "Bournemouth", 450, 0, 0, 0, 0, 0, 1, 0, 12, 0, 0, 0, 2027, None, 18000),

    # Nottingham Forest (+3)
    ("Carlos Miguel", "Brazil", 27, "GK", "Premier League", "Nottingham Forest", 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, 0, 0, 2028, None, 35000),
    ("Jota Silva", "Portugal", 27, "FWD", "Premier League", "Nottingham Forest", 1890, 5, 3, 44, 17, 36, 34, 16, 12, 4, 3, 0, 2028, None, 40000),
    ("Ramón Sosa", "Paraguay", 27, "FWD", "Premier League", "Nottingham Forest", 1800, 4, 3, 40, 15, 32, 30, 14, 10, 3, 2, 0, 2029, None, 45000),

    # 1. FC Heidenheim (+2)
    ("Stefan Schimmer", "Germany", 32, "FWD", "Bundesliga", "1. FC Heidenheim", 1440, 4, 1, 28, 10, 14, 18, 6, 12, 2, 2, 0, 2026, None, 20000),
    ("Paul Tschernuth", "Austria", 24, "GK", "Bundesliga", "1. FC Heidenheim", 450, 0, 0, 0, 0, 0, 1, 0, 10, 0, 0, 0, 2027, None, 15000),

    # Ipswich Town (+2)
    ("Ali Al-Hamadi", "Iraq", 24, "FWD", "Premier League", "Ipswich Town", 1530, 4, 2, 34, 13, 20, 20, 8, 10, 2, 2, 0, 2028, None, 25000),
    ("Cieran Slicker", "Scotland", 23, "GK", "Premier League", "Ipswich Town", 450, 0, 0, 0, 0, 0, 1, 0, 10, 0, 0, 0, 2028, None, 15000),

    # RB Leipzig (+3)
    ("Arthur Vermeeren", "Belgium", 21, "MID", "Bundesliga", "RB Leipzig", 2250, 2, 4, 26, 8, 44, 68, 42, 32, 12, 4, 0, 2029, None, 50000),
    ("Antonio Nusa", "Norway", 21, "FWD", "Bundesliga", "RB Leipzig", 2430, 7, 6, 58, 24, 52, 38, 18, 12, 4, 3, 0, 2029, None, 55000),
    ("Lutsharel Geertruida", "Netherlands", 26, "DEF", "Bundesliga", "RB Leipzig", 2700, 3, 3, 26, 9, 24, 78, 56, 118, 26, 5, 0, 2029, None, 80000)
]

added_players = 0
added_comps = 0

for p in TOP_UP_PLAYERS:
    name = p[0]
    if name.lower() in existing_names:
        continue
    
    curr_p_id += 1
    nation, age, pos, league, team = p[1], p[2], p[3], p[4], p[5]
    mins, goals, assists, shots, sot, chances = p[6], p[7], p[8], p[9], p[10], p[11]
    tackles, interc, clears, blocks, yellow, red = p[12], p[13], p[14], p[15], p[16], p[17]
    contract_year, release_clause, wage = p[18], p[19], p[20]
    
    # Valuation calculation
    base_val = 8000000.0
    if goals + assists > 10:
        base_val += (goals * 2500000.0) + (assists * 1800000.0)
    else:
        base_val += (goals * 1500000.0) + (assists * 1000000.0)
        
    if pos in ("DEF", "GK"):
        base_val += (tackles * 250000.0) + (interc * 200000.0) + (clears * 100000.0)
    elif pos == "MID":
        base_val += (chances * 350000.0) + (tackles * 150000.0)
        
    if age <= 21:
        base_val *= 1.35
    elif age <= 24:
        base_val *= 1.18
    elif age <= 27:
        base_val *= 1.05
    elif age <= 30:
        base_val *= 0.85
    else:
        base_val *= 0.50
        
    if contract_year >= 2029:
        base_val *= 1.15
    elif contract_year == 2026:
        base_val *= 0.75
        
    if release_clause and release_clause < base_val:
        base_val = float(release_clause)
        
    mkt_val = round(base_val, -5)
    
    height = random.choice([178, 182, 185, 188, 191]) if pos in ("DEF", "GK") else random.choice([172, 175, 178, 180, 184])
    weight = round(height * 0.42, 1)
    drib_comp = round(chances * 0.6)
    drib_att = round(drib_comp * 1.5)
    passes_comp = round(mins * 0.50)
    passes_att = round(passes_comp * 1.23)
    prog_passes = round(passes_comp * 0.10)
    aerials = round((tackles + clears) * 0.3)
    touches = round(passes_att * 1.35)
    apps = max(18, round(mins / 85))
    cs = round(apps * 0.28) if pos in ("DEF", "GK") else 0
    saves = round(mins / 25) if pos == "GK" else 0
    conceded = round(mins / 75) if pos == "GK" else 0
    
    c.execute("""
        INSERT INTO players (
            id, name, nation, age, height_cm, weight_kg, league, team,
            minutes_played, goals, assists, shots, shots_on_target,
            dribbles_completed, dribbles_attempted, chances_created,
            passes_completed, passes_attempted, progressive_passes,
            tackles_won, defense_interceptions, clearances, blocks,
            aerials_won, touches, yellow_cards, red_cards,
            predicted_market_value_eur, position, appearances,
            clean_sheets, saves, goals_conceded,
            contract_expires_year, release_clause_eur, wage_eur_weekly,
            buyback_clause_eur, sell_on_pct
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?
        )
    """, (
        curr_p_id, name, nation, age, height, weight, league, team,
        mins, goals, assists, shots, sot,
        drib_comp, drib_att, chances,
        passes_comp, passes_att, prog_passes,
        tackles, interc, clears, blocks,
        aerials, touches, yellow, red,
        mkt_val, pos, apps,
        cs, saves, conceded,
        contract_year, release_clause, wage,
        None, None
    ))
    added_players += 1
    existing_names.add(name.lower())
    
    # Insert primary league competition stat
    curr_c_id += 1
    c.execute("""
        INSERT INTO player_competition_stats (
            id, player_id, competition_name, competition_type, season,
            appearances, minutes_played, goals, assists,
            shots, shots_on_target, chances_created,
            tackles_won, interceptions, clearances, blocks,
            yellow_cards, red_cards, stage_reached
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?
        )
    """, (
        curr_c_id, curr_p_id, league, "league", "2024-2026",
        apps, mins, goals, assists,
        shots, sot, chances,
        tackles, interc, clears, blocks,
        yellow, red, "Regular Season"
    ))
    added_comps += 1

conn.commit()
print(f"COMPLETE: Added {added_players} top-up players and {added_comps} competition stats.")
conn.close()
