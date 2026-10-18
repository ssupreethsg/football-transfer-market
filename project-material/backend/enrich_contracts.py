import sqlite3
import random

KNOWN_CONTRACTS = {
    "yamal": {"expires": 2031, "clause": 1000000000.0, "wage": 150000.0, "sell_on": None, "buyback": None},
    "haaland": {"expires": 2034, "clause": None, "wage": 475000.0, "sell_on": None, "buyback": None},
    "mbappe": {"expires": 2029, "clause": 1000000000.0, "wage": 600000.0, "sell_on": None, "buyback": None},
    "bellingham": {"expires": 2029, "clause": 1000000000.0, "wage": 400000.0, "sell_on": None, "buyback": None},
    "vinicius": {"expires": 2027, "clause": 1000000000.0, "wage": 600000.0, "sell_on": None, "buyback": None},
    "nico_williams": {"expires": 2035, "clause": 90000000.0, "wage": 200000.0, "sell_on": None, "buyback": None},
    "palmer": {"expires": 2033, "clause": None, "wage": 150000.0, "sell_on": None, "buyback": None},
    "saka": {"expires": 2030, "clause": None, "wage": 350000.0, "sell_on": None, "buyback": None},
    "pedri": {"expires": 2026, "clause": 1000000000.0, "wage": 240000.0, "sell_on": None, "buyback": None},
    "cubarsi": {"expires": 2027, "clause": 500000000.0, "wage": 80000.0, "sell_on": None, "buyback": None},
    "musiala": {"expires": 2030, "clause": 175000000.0, "wage": 480000.0, "sell_on": None, "buyback": None},
    "wirtz": {"expires": 2031, "clause": None, "wage": 240000.0, "sell_on": None, "buyback": None},
    "saliba": {"expires": 2030, "clause": None, "wage": 280000.0, "sell_on": None, "buyback": None},
    "rice": {"expires": 2029, "clause": None, "wage": 290000.0, "sell_on": None, "buyback": None},
    "rodri": {"expires": 2027, "clause": None, "wage": 320000.0, "sell_on": None, "buyback": None},
    "gvardiol": {"expires": 2028, "clause": None, "wage": 220000.0, "sell_on": None, "buyback": None},
    "olise": {"expires": 2029, "clause": None, "wage": 250000.0, "sell_on": None, "buyback": None},
    "barcola": {"expires": 2028, "clause": None, "wage": 160000.0, "sell_on": None, "buyback": None},
    "kane": {"expires": 2027, "clause": None, "wage": 480000.0, "sell_on": None, "buyback": None},
    "salah": {"expires": 2026, "clause": None, "wage": 400000.0, "sell_on": None, "buyback": None},
    "de bruyne": {"expires": 2026, "clause": None, "wage": 450000.0, "sell_on": None, "buyback": None}
}

def enrich_all_contracts():
    conn = sqlite3.connect('sql_app.db')
    c = conn.cursor()
    
    c.execute("SELECT id, name, age, team, league, minutes_played, predicted_market_value_eur FROM players")
    players = c.fetchall()
    print(f"Enriching contracts for all {len(players)} players...")
    
    updates = []
    
    # Deterministic pseudo-random seed based on player ID for reproducible financial modeling
    for p in players:
        p_id, name, age, team, league, mins, mkt_val = p
        name_lower = (name or '').lower()
        team_lower = (team or '').lower()
        league_lower = (league or '').lower()
        age = age or 25
        mins = mins or 0
        mkt_val = mkt_val or 10000000.0
        
        # Check if known marquee player
        matched_marquee = False
        for k, v in KNOWN_CONTRACTS.items():
            if k in name_lower or (len(k) > 4 and k.replace('_', ' ') in name_lower):
                updates.append((v["expires"], v["clause"], v["wage"], v["buyback"], v["sell_on"], p_id))
                matched_marquee = True
                break
        if matched_marquee:
            continue
            
        rnd = random.Random(p_id * 42)
        
        # 1. Contract Expiry Year Modeling (Reference date: August 2026)
        if age >= 34:
            expires = 2026 if rnd.random() < 0.6 else 2027
        elif age >= 31:
            expires = rnd.choice([2026, 2027, 2028])
        elif age <= 22 and mins >= 1200:
            expires = rnd.choice([2029, 2030, 2031])  # Long-term young asset
        elif mins >= 1800:
            expires = rnd.choice([2028, 2029, 2030])  # Established starter
        else:
            expires = rnd.choice([2027, 2028, 2029])
            
        # 2. Release Clause Modeling (Mandatory in Spain, discretionary elsewhere)
        clause = None
        if 'la liga' in league_lower or 'esp' in league_lower:
            # Spain legally mandates release clauses
            if any(t in team_lower for t in ['real madrid', 'barcelona']):
                if mkt_val > 80000000:
                    clause = rnd.choice([500000000.0, 750000000.0, 1000000000.0])
                else:
                    clause = rnd.choice([150000000.0, 300000000.0, 400000000.0])
            elif any(t in team_lower for t in ['atletico', 'athletic', 'sociedad', 'villarreal', 'sevilla', 'valencia']):
                base_clause = max(mkt_val * 1.5, 40000000.0)
                clause = round(base_clause / 5000000.0) * 5000000.0
            else:
                base_clause = max(mkt_val * 1.3, 15000000.0)
                clause = round(base_clause / 2000000.0) * 2000000.0
        elif 'ligue 1' in league_lower or 'fra' in league_lower:
            # France LFP Charter Art 202 forbids buyout clauses
            clause = None
        else:
            # Premier League, Serie A, Bundesliga: only ~8% of contracts have clauses
            if rnd.random() < 0.08:
                base_clause = max(mkt_val * 1.4, 30000000.0)
                clause = round(base_clause / 5000000.0) * 5000000.0
                
        # 3. Weekly Wage Modeling (Capology scale grounded in club revenue & value)
        # Elite €80M+ value: €120k - €350k/wk
        # Mid-tier €20M-€80M: €45k - €120k/wk
        # Squad €5M-€20M: €20k - €50k/wk
        # Low <€5M: €5k - €20k/wk
        if mkt_val >= 100000000:
            wage = 180000.0 + (mkt_val / 1000000.0) * 1200.0
        elif mkt_val >= 50000000:
            wage = 85000.0 + (mkt_val / 1000000.0) * 900.0
        elif mkt_val >= 20000000:
            wage = 40000.0 + (mkt_val / 1000000.0) * 700.0
        elif mkt_val >= 5000000:
            wage = 18000.0 + (mkt_val / 1000000.0) * 600.0
        else:
            wage = max(5000.0, 10000.0 + (mkt_val / 1000000.0) * 500.0)
            
        # Premier League wage inflation premium (+25%)
        if 'premier' in league_lower:
            wage *= 1.25
        elif 'ligue 1' in league_lower and 'paris' not in team_lower:
            wage *= 0.85
            
        wage = round(wage / 1000.0) * 1000.0
        
        # 4. Sell-on / Buy-back for young developing players (< 23)
        buyback = None
        sell_on = None
        if age <= 23 and rnd.random() < 0.15:
            sell_on = rnd.choice([10.0, 15.0, 20.0, 25.0])
            if rnd.random() < 0.3:
                buyback = round(mkt_val * 1.6 / 1000000.0) * 1000000.0
                
        updates.append((expires, clause, wage, buyback, sell_on, p_id))
        
    c.executemany("""
        UPDATE players 
        SET contract_expires_year = ?, release_clause_eur = ?, wage_eur_weekly = ?,
            buyback_clause_eur = ?, sell_on_pct = ?
        WHERE id = ?
    """, updates)
    conn.commit()
    print(f"Successfully enriched financial and contract clause data for {len(updates)} players.")
    
    # Audit summary
    c.execute("SELECT COUNT(*) FROM players WHERE release_clause_eur IS NOT NULL")
    clauses_cnt = c.fetchone()[0]
    c.execute("SELECT AVG(wage_eur_weekly), MAX(wage_eur_weekly), MIN(wage_eur_weekly) FROM players")
    avg_w, max_w, min_w = c.fetchone()
    print(f"\nFinancial Audit Summary:")
    print(f"  Players with active Release Clauses: {clauses_cnt}")
    print(f"  Average Weekly Wage: EUR {avg_w:,.0f}/wk")
    print(f"  Top Weekly Wage: EUR {max_w:,.0f}/wk")
    print(f"  Min Weekly Wage: EUR {min_w:,.0f}/wk")
    
    conn.close()

if __name__ == "__main__":
    enrich_all_contracts()
