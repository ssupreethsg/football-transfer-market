import sqlite3
import unicodedata
import re
import math

def clean_text(s: str) -> str:
    if not s: return ""
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s).lower().strip()
    return re.sub(r'\s+', ' ', s)

MARQUEE_STARS = {
    "haaland": {
        "name": "Erling Haaland",
        "age": 26,
        "team": "Manchester City",
        "league": "Premier League",
        "position": "FWD",
        "goals": 27,
        "assists": 5,
        "minutes": 2741,
        "expires": 2034,
        "clause": None,
        "wage": 475000.0
    },
    "yamal": {
        "name": "Lamine Yamal",
        "age": 19,
        "team": "Barcelona",
        "league": "La Liga",
        "position": "FWD",
        "goals": 9,
        "assists": 13,
        "minutes": 2771,
        "expires": 2031,
        "clause": 1000000000.0,
        "wage": 150000.0
    },
    "mbappe": {
        "name": "Kylian Mbappé",
        "age": 27,
        "team": "Real Madrid",
        "league": "La Liga",
        "position": "FWD",
        "goals": 31,
        "assists": 7,
        "minutes": 3023,
        "expires": 2029,
        "clause": 1000000000.0,
        "wage": 600000.0
    },
    "bellingham": {
        "name": "Jude Bellingham",
        "age": 23,
        "team": "Real Madrid",
        "league": "La Liga",
        "position": "MID",
        "goals": 19,
        "assists": 8,
        "minutes": 2790,
        "expires": 2029,
        "clause": 1000000000.0,
        "wage": 400000.0
    },
    "palmer": {
        "name": "Cole Palmer",
        "age": 24,
        "team": "Chelsea",
        "league": "Premier League",
        "position": "FWD",
        "goals": 22,
        "assists": 11,
        "minutes": 3199,
        "expires": 2033,
        "clause": None,
        "wage": 150000.0
    },
    "saka": {
        "name": "Bukayo Saka",
        "age": 24,
        "team": "Arsenal",
        "league": "Premier League",
        "position": "FWD",
        "goals": 16,
        "assists": 13,
        "minutes": 2978,
        "expires": 2030,
        "clause": None,
        "wage": 350000.0
    },
    "vinicius": {
        "name": "Vinícius Júnior",
        "age": 26,
        "team": "Real Madrid",
        "league": "La Liga",
        "position": "FWD",
        "goals": 18,
        "assists": 11,
        "minutes": 2600,
        "expires": 2027,
        "clause": 1000000000.0,
        "wage": 600000.0
    },
    "nico_williams": {
        "name": "Nico Williams",
        "age": 24,
        "team": "Athletic Club",
        "league": "La Liga",
        "position": "FWD",
        "goals": 8,
        "assists": 16,
        "minutes": 2650,
        "expires": 2035,
        "clause": 90000000.0,
        "wage": 200000.0
    },
    "pedri": {
        "name": "Pedri",
        "age": 23,
        "team": "Barcelona",
        "league": "La Liga",
        "position": "MID",
        "goals": 7,
        "assists": 8,
        "minutes": 2500,
        "expires": 2026,
        "clause": 1000000000.0,
        "wage": 240000.0
    },
    "cubarsi": {
        "name": "Pau Cubarsí",
        "age": 19,
        "team": "Barcelona",
        "league": "La Liga",
        "position": "DEF",
        "goals": 1,
        "assists": 2,
        "minutes": 2400,
        "expires": 2027,
        "clause": 500000000.0,
        "wage": 80000.0
    },
    "musiala": {
        "name": "Jamal Musiala",
        "age": 23,
        "team": "Bayern Munich",
        "league": "Bundesliga",
        "position": "MID",
        "goals": 14,
        "assists": 9,
        "minutes": 2600,
        "expires": 2030,
        "clause": 175000000.0,
        "wage": 480000.0
    },
    "wirtz": {
        "name": "Florian Wirtz",
        "age": 23,
        "team": "Bayer Leverkusen",
        "league": "Bundesliga",
        "position": "MID",
        "goals": 16,
        "assists": 14,
        "minutes": 2700,
        "expires": 2031,
        "clause": None,
        "wage": 240000.0
    },
    "saliba": {
        "name": "William Saliba",
        "age": 25,
        "team": "Arsenal",
        "league": "Premier League",
        "position": "DEF",
        "goals": 2,
        "assists": 1,
        "minutes": 3300,
        "expires": 2030,
        "clause": None,
        "wage": 280000.0
    },
    "rodri": {
        "name": "Rodri",
        "age": 30,
        "team": "Manchester City",
        "league": "Premier League",
        "position": "MID",
        "goals": 8,
        "assists": 9,
        "minutes": 3100,
        "expires": 2027,
        "clause": None,
        "wage": 320000.0
    },
    "rice": {
        "name": "Declan Rice",
        "age": 27,
        "team": "Arsenal",
        "league": "Premier League",
        "position": "MID",
        "goals": 7,
        "assists": 8,
        "minutes": 3150,
        "expires": 2029,
        "clause": None,
        "wage": 290000.0
    },
    "gvardiol": {
        "name": "Joško Gvardiol",
        "age": 24,
        "team": "Manchester City",
        "league": "Premier League",
        "position": "DEF",
        "goals": 4,
        "assists": 2,
        "minutes": 2800,
        "expires": 2028,
        "clause": None,
        "wage": 220000.0
    }
}

def calculate_modern_market_value():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    # 1. Update/insert Marquee Stars to ensure high data quality & contract values
    for star_key, star_data in MARQUEE_STARS.items():
        cursor.execute("SELECT id FROM players WHERE name LIKE ? OR name LIKE ?", 
                       (f"%{star_data['name']}%", f"%{star_key.replace('_', ' ')}%"))
        found = cursor.fetchone()
        if found:
            cursor.execute("""
                UPDATE players 
                SET name = ?, age = ?, team = ?, league = ?, position = ?, 
                    goals = ?, assists = ?, minutes_played = ?,
                    contract_expires_year = ?, release_clause_eur = ?, wage_eur_weekly = ?
                WHERE id = ?
            """, (
                star_data["name"], star_data["age"], star_data["team"], star_data["league"],
                star_data["position"], star_data["goals"], star_data["assists"],
                star_data["minutes"], star_data["expires"], star_data["clause"], star_data["wage"],
                found[0]
            ))
    conn.commit()
    
    # 2. Reload players with contract fields
    cursor.execute("""
        SELECT id, name, age, position, team, league, minutes_played, goals, assists,
               shots, shots_on_target, tackles_won, defense_interceptions, clearances,
               blocks, aerials_won, chances_created, progressive_passes, dribbles_completed,
               clean_sheets, saves, goals_conceded, appearances,
               contract_expires_year, release_clause_eur, wage_eur_weekly
        FROM players
    """)
    players = cursor.fetchall()
    print(f"Applying 2026 Contract-Aware Econometric Model to {len(players)} players...")
    
    TIER_1_CLUBS = {
        'real madrid', 'manchester city', 'barcelona', 'fc barcelona',
        'bayern munich', 'bayern munchen', 'paris saint-germain', 'paris sg', 'paris s-g'
    }
    TIER_2_CLUBS = {
        'arsenal', 'liverpool', 'chelsea', 'manchester united', 'manchester utd',
        'inter', 'inter milan', 'juventus', 'borussia dortmund', 'dortmund'
    }
    TIER_3_CLUBS = {
        'atletico madrid', 'ac milan', 'milan', 'bayer leverkusen', 'leverkusen',
        'tottenham', 'tottenham hotspur', 'newcastle', 'newcastle united',
        'aston villa', 'napoli', 'roma', 'as roma', 'atalanta', 'rb leipzig', 'leipzig',
        'athletic club', 'real sociedad'
    }
    
    BASE_VALUE = 11_500_000.0  # €11.5M base median
    updates = []
    
    for p in players:
        (p_id, name, age, pos, team, league, mins, goals, assists,
         shots, sot, tkl, intc, clr, blk, aer, chn, prg, drb,
         cs, sv, gc, apps, contract_exp, release_clause, wage) = p
        
        pos = (pos or 'MID').upper()
        mins = mins or 0
        goals = goals or 0
        assists = assists or 0
        age = age or 25
        shots = shots or 0
        sot = sot or 0
        tkl = tkl or 0
        intc = intc or 0
        clr = clr or 0
        blk = blk or 0
        aer = aer or 0
        chn = chn or 0
        prg = prg or 0
        drb = drb or 0
        contract_exp = contract_exp or 2028
        
        team_clean = (team or '').lower().strip()
        league_clean = (league or '').lower().strip()
        
        # 1. League Multiplier
        if 'premier' in league_clean or 'eng' in league_clean:
            f_league = 1.35
        elif 'la liga' in league_clean or 'esp' in league_clean:
            f_league = 1.25
        elif 'bundesliga' in league_clean or 'ger' in league_clean:
            f_league = 1.10
        elif 'serie a' in league_clean or 'ita' in league_clean:
            f_league = 1.05
        elif 'ligue 1' in league_clean or 'fra' in league_clean:
            f_league = 0.95
        else:
            f_league = 0.70
            
        # 2. Club Tier Multiplier
        if any(c in team_clean for c in TIER_1_CLUBS):
            f_club = 1.52
        elif any(c in team_clean for c in TIER_2_CLUBS):
            f_club = 1.28
        elif any(c in team_clean for c in TIER_3_CLUBS):
            f_club = 1.10
        elif 'premier' in league_clean:
            f_club = 0.95
        else:
            f_club = 0.80
            
        # 3. Playing Time & Squad Role Factor
        if mins >= 2400:
            f_role = 1.25
        elif mins >= 1800:
            f_role = 1.10
        elif mins >= 1200:
            f_role = 0.95
        elif mins >= 600:
            f_role = 0.60
        elif mins >= 250:
            f_role = 0.30
        else:
            f_role = 0.12  # Benchwarmers severely limited
            
        # 4. Realistic Transfer Market Age Factor
        is_established = (mins >= 1000)
        
        if is_established:
            if age <= 19: f_age = 1.62       # Wonderkid starter (Yamal)
            elif age <= 21: f_age = 1.45     # Elite Young Talent (Bellingham, Cubarsi)
            elif age <= 23: f_age = 1.32     # Rising Star (Palmer, Saka, Musiala, Wirtz)
            elif age <= 26: f_age = 1.15     # Peak Prime (Haaland, Mbappe, Vinicius)
            elif age <= 28: f_age = 1.00     # Established Prime
            elif age <= 30: f_age = 0.78     # Late Prime (Rodri)
            elif age <= 32: f_age = 0.52     # Aging Veteran
            elif age <= 34: f_age = 0.32     # Pre-Retirement
            else: f_age = 0.16               # Twilight
        else:
            if age <= 20: f_age = 0.75
            elif age <= 23: f_age = 0.65
            elif age <= 27: f_age = 0.55
            elif age <= 30: f_age = 0.40
            else: f_age = 0.15
            
        # 5. Contract Expiration & Seller Leverage Factor
        years_left = max(0, contract_exp - 2026)
        if years_left >= 5:
            f_contract = 1.18  # Locked in long-term, extreme selling club leverage
        elif years_left >= 3:
            f_contract = 1.08  # Solid contractual protection
        elif years_left == 2:
            f_contract = 1.00  # Standard market baseline
        elif years_left == 1:
            f_contract = 0.75  # Bosman risk: selling club under pressure to renew or cash in
        else:
            f_contract = 0.45  # Final months of deal: fire-sale valuation
            
        # 6. Position-Aware Performance Scoring
        p90 = max(mins / 90.0, 0.4)
        g90 = goals / p90
        a90 = assists / p90
        
        if pos == 'FWD':
            perf_score = (goals * 0.11) + (assists * 0.08) + (g90 * 1.5) + (a90 * 1.0)
        elif pos == 'MID':
            perf_score = (goals * 0.09) + (assists * 0.12) + (g90 * 1.2) + (a90 * 1.4) + (chn / p90 * 0.3)
        elif pos == 'DEF':
            perf_score = (tkl * 0.03) + (intc * 0.03) + (clr * 0.02) + (mins / 1000.0 * 0.6)
        else: # GK
            cs_val = cs if cs > 0 else (mins / 900.0)
            perf_score = (cs_val * 0.3) + (mins / 1000.0 * 0.6)
            
        # Sigmoidal performance factor
        f_perf = 0.35 + (3.85 / (1.0 + math.exp(-1.4 * (perf_score - 1.25))))
        
        # 7. Position Scarcity
        if pos == 'FWD': f_pos = 1.15
        elif pos == 'MID': f_pos = 1.00
        elif pos == 'DEF': f_pos = 0.85
        else: f_pos = 0.65
        
        # Raw Value Calculation
        raw_val = BASE_VALUE * f_league * f_club * f_role * f_age * f_contract * f_perf * f_pos
        
        # 8. Superstar Power Law (Rosen 1981)
        if raw_val > 65_000_000:
            final_val = 65_000_000 * ((raw_val / 65_000_000) ** 1.30)
        else:
            final_val = raw_val
            
        # 9. Release Clause Pairing
        # If player has an enforceable release clause that is LOWER than calculated value,
        # the market value is capped at that buyout fee (e.g. Nico Williams €90M clause)
        if release_clause and release_clause > 0 and final_val > release_clause:
            final_val = release_clause
            
        # Global realistic bounds
        final_val = max(500_000.0, min(220_000_000.0, final_val))
        rounded_val = round(final_val / 500_000.0) * 500_000.0
        
        updates.append((rounded_val, p_id))
        
    cursor.executemany("UPDATE players SET predicted_market_value_eur = ? WHERE id = ?", updates)
    conn.commit()
    conn.close()
    print("Contract-Aware Market value calculation completed successfully!")

if __name__ == "__main__":
    calculate_modern_market_value()
