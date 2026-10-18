import sqlite3
import unicodedata
import re

TEAM_CANONICAL_MAP = {
    # Premier League
    "manchester utd": "Manchester United",
    "manchester united": "Manchester United",
    "manchester city": "Manchester City",
    "arsenal": "Arsenal",
    "liverpool": "Liverpool",
    "chelsea": "Chelsea",
    "tottenham": "Tottenham Hotspur",
    "tottenham hotspur": "Tottenham Hotspur",
    "newcastle": "Newcastle United",
    "newcastle utd": "Newcastle United",
    "newcastle united": "Newcastle United",
    "aston villa": "Aston Villa",
    "west ham": "West Ham United",
    "west ham united": "West Ham United",
    "brighton": "Brighton & Hove Albion",
    "brighton and hove albion": "Brighton & Hove Albion",
    "wolves": "Wolverhampton Wanderers",
    "wolverhampton wanderers": "Wolverhampton Wanderers",
    "everton": "Everton",
    "crystal palace": "Crystal Palace",
    "brentford": "Brentford",
    "fulham": "Fulham",
    "bournemouth": "Bournemouth",
    "afc bournemouth": "Bournemouth",
    "nottm forest": "Nottingham Forest",
    "nottingham forest": "Nottingham Forest",
    "leicester": "Leicester City",
    "leicester city": "Leicester City",
    "southampton": "Southampton",
    "ipswich": "Ipswich Town",
    "ipswich town": "Ipswich Town",
    "leeds": "Leeds United",
    "leeds united": "Leeds United",
    "norwich": "Norwich City",
    "norwich city": "Norwich City",
    "watford": "Watford",
    "burnley": "Burnley",

    # La Liga
    "real madrid": "Real Madrid",
    "barcelona": "FC Barcelona",
    "fc barcelona": "FC Barcelona",
    "atletico madrid": "Atlético Madrid",
    "atletico de madrid": "Atlético Madrid",
    "athletic club": "Athletic Club",
    "athletic bilbao": "Athletic Club",
    "real sociedad": "Real Sociedad",
    "real betis": "Real Betis",
    "betis": "Real Betis",
    "villarreal": "Villarreal",
    "sevilla": "Sevilla",
    "valencia": "Valencia",
    "girona": "Girona",
    "celta": "Celta Vigo",
    "celta vigo": "Celta Vigo",
    "osasuna": "Osasuna",
    "getafe": "Getafe",
    "rayo vallecano": "Rayo Vallecano",
    "mallorca": "RCD Mallorca",
    "rcd mallorca": "RCD Mallorca",
    "espanyol": "RCD Espanyol",
    "rcd espanyol": "RCD Espanyol",
    "las palmas": "UD Las Palmas",
    "ud las palmas": "UD Las Palmas",
    "alaves": "Deportivo Alavés",
    "deportivo alaves": "Deportivo Alavés",
    "leganes": "CD Leganés",
    "cd leganes": "CD Leganés",
    "valladolid": "Real Valladolid",
    "real valladolid": "Real Valladolid",
    "cadiz": "Cádiz",
    "granada": "Granada",
    "elche": "Elche",
    "levante": "Levante",

    # Serie A
    "inter": "Inter Milan",
    "inter milan": "Inter Milan",
    "milan": "AC Milan",
    "ac milan": "AC Milan",
    "juventus": "Juventus",
    "napoli": "Napoli",
    "atalanta": "Atalanta",
    "roma": "AS Roma",
    "as roma": "AS Roma",
    "lazio": "Lazio",
    "fiorentina": "Fiorentina",
    "bologna": "Bologna",
    "torino": "Torino",
    "monza": "Monza",
    "genoa": "Genoa",
    "udinese": "Udinese",
    "parma": "Parma",
    "como": "Como",
    "cagliari": "Cagliari",
    "empoli": "Empoli",
    "verona": "Hellas Verona",
    "hellas verona": "Hellas Verona",
    "lecce": "Lecce",
    "venezia": "Venezia",
    "sassuolo": "Sassuolo",
    "salernitana": "Salernitana",
    "sampdoria": "Sampdoria",
    "spezia": "Spezia",

    # Bundesliga
    "bayern munich": "Bayern Munich",
    "bayern munchen": "Bayern Munich",
    "dortmund": "Borussia Dortmund",
    "borussia dortmund": "Borussia Dortmund",
    "leverkusen": "Bayer Leverkusen",
    "bayer leverkusen": "Bayer Leverkusen",
    "rb leipzig": "RB Leipzig",
    "leipzig": "RB Leipzig",
    "eint frankfurt": "Eintracht Frankfurt",
    "eintracht frankfurt": "Eintracht Frankfurt",
    "stuttgart": "VfB Stuttgart",
    "vfb stuttgart": "VfB Stuttgart",
    "freiburg": "SC Freiburg",
    "sc freiburg": "SC Freiburg",
    "wolfsburg": "VfL Wolfsburg",
    "vfl wolfsburg": "VfL Wolfsburg",
    "mgladbach": "Borussia Mönchengladbach",
    "borussia monchengladbach": "Borussia Mönchengladbach",
    "hoffenheim": "TSG Hoffenheim",
    "1899 hoffenheim": "TSG Hoffenheim",
    "tsg hoffenheim": "TSG Hoffenheim",
    "werder bremen": "Werder Bremen",
    "union berlin": "Union Berlin",
    "augsburg": "FC Augsburg",
    "fc augsburg": "FC Augsburg",
    "mainz 05": "FSV Mainz 05",
    "mainz": "FSV Mainz 05",
    "bochum": "VfL Bochum",
    "vfl bochum": "VfL Bochum",
    "koln": "1. FC Köln",
    "1 fc koln": "1. FC Köln",
    "heidenheim": "FC Heidenheim",
    "st pauli": "FC St. Pauli",
    "hertha bsc": "Hertha BSC",
    "arminia": "Arminia Bielefeld",
    "greuther furth": "Greuther Fürth",

    # Ligue 1
    "paris sg": "Paris Saint-Germain",
    "paris sg": "Paris Saint-Germain",
    "paris saint germain": "Paris Saint-Germain",
    "paris saintgermain": "Paris Saint-Germain",
    "monaco": "AS Monaco",
    "as monaco": "AS Monaco",
    "marseille": "Olympique de Marseille",
    "olympique marseille": "Olympique de Marseille",
    "lyon": "Olympique Lyonnais",
    "olympique lyon": "Olympique Lyonnais",
    "lille": "Lille OSC",
    "lille osc": "Lille OSC",
    "nice": "OGC Nice",
    "ogc nice": "OGC Nice",
    "lens": "RC Lens",
    "rc lens": "RC Lens",
    "rennes": "Stade Rennais",
    "stade rennais": "Stade Rennais",
    "brest": "Stade Brestois 29",
    "stade brestois 29": "Stade Brestois 29",
    "strasbourg": "RC Strasbourg",
    "rc strasbourg": "RC Strasbourg",
    "toulouse": "Toulouse FC",
    "reims": "Stade de Reims",
    "stade de reims": "Stade de Reims",
    "montpellier": "Montpellier HSC",
    "nantes": "FC Nantes",
    "fc nantes": "FC Nantes",
    "auxerre": "AJ Auxerre",
    "aj auxerre": "AJ Auxerre",
    "le havre": "Le Havre AC",
    "angers": "Angers SCO",
    "saint etienne": "AS Saint-Étienne",
    "saintetienne": "AS Saint-Étienne",
    "lorient": "FC Lorient",
    "clermont foot": "Clermont Foot",
    "metz": "FC Metz",
    "troyes": "Troyes",
    "bordeaux": "Girondins de Bordeaux"
}

def clean_key(s: str) -> str:
    s = unicodedata.normalize('NFKD', s or '').encode('ASCII', 'ignore').decode('utf-8')
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s).lower().strip()
    return re.sub(r'\s+', ' ', s)

def normalize_all_teams():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, team FROM players")
    rows = cursor.fetchall()
    
    updates = []
    for p_id, team_name in rows:
        key = clean_key(team_name)
        if key in TEAM_CANONICAL_MAP:
            canonical = TEAM_CANONICAL_MAP[key]
            updates.append((canonical, p_id))
        else:
            # Check partial matches
            matched = False
            for k, canonical in TEAM_CANONICAL_MAP.items():
                if k == key or (len(k) > 4 and k in key):
                    updates.append((canonical, p_id))
                    matched = True
                    break
            if not matched:
                updates.append((team_name.strip(), p_id))
                
    cursor.executemany("UPDATE players SET team = ? WHERE id = ?", updates)
    conn.commit()
    
    print(f"Normalized team names across {len(updates)} players.")
    
    # Audit team counts by league after normalization
    for lg in ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']:
        cursor.execute("SELECT COUNT(DISTINCT team) FROM players WHERE league = ?", (lg,))
        t_cnt = cursor.fetchone()[0]
        print(f"  {lg}: {t_cnt} canonical teams")
        
    conn.close()

if __name__ == "__main__":
    normalize_all_teams()
