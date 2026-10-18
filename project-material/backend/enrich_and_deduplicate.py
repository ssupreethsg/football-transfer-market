import sqlite3
import unicodedata
import re
import pandas as pd
import os

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Normalize unicode characters and remove accents
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # Lowercase and strip punctuation
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text).lower().strip()
    return re.sub(r'\s+', ' ', text)

def get_position_map_from_csv():
    pos_map = {}
    csv_path = 'real_data.csv'
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, encoding='ISO-8859-1', sep=';')
            for _, row in df.iterrows():
                p_name = normalize_text(str(row.get('Player', '')))
                pos_raw = str(row.get('Pos', '')).upper()
                
                # Map to FWD, MID, DEF, GK
                if 'GK' in pos_raw:
                    pos = 'GK'
                elif 'DF' in pos_raw and 'FW' not in pos_raw and 'MF' not in pos_raw:
                    pos = 'DEF'
                elif 'FW' in pos_raw:
                    pos = 'FWD'
                elif 'MF' in pos_raw or 'DFMF' in pos_raw or 'MFDF' in pos_raw:
                    pos = 'MID'
                else:
                    pos = 'MID'
                if p_name:
                    pos_map[p_name] = pos
        except Exception as e:
            print(f"Error reading CSV for positions: {e}")
    return pos_map

KNOWN_POSITIONS = {
    "erling haaland": "FWD",
    "lamine yamal": "FWD",
    "kylian mbappe": "FWD",
    "jude bellingham": "MID",
    "vinicius junior": "FWD",
    "pedri": "MID",
    "cole palmer": "FWD",
    "bukayo saka": "FWD",
    "william saliba": "DEF",
    "pau cubarsi": "DEF",
    "rodri": "MID",
    "neco williams": "DEF",
    "arda guler": "MID",
    "endrick": "FWD",
    "kobbie mainoo": "MID",
    "warren zaireemery": "MID",
    "alejandro garnacho": "FWD",
    "savinho": "FWD",
    "bradley barcola": "FWD",
    "leny yoro": "DEF",
    "joao neves": "MID",
    "riccardo calafiori": "DEF",
    "michael olise": "FWD",
    "xavi simons": "MID",
    "florian wirtz": "MID",
    "jamal musiala": "MID",
    "declan rice": "MID",
    "martin odegaard": "MID",
    "gabriel magalhaes": "DEF",
    "trent alexanderarnold": "DEF",
    "virgil van dijk": "DEF",
    "alisson": "GK",
    "thibaut courtois": "GK",
    "gianluigi donnarumma": "GK",
    "david raya": "GK",
    "ederson": "GK",
    "marcandre ter stegen": "GK",
    "mohamed salah": "FWD",
    "harry kane": "FWD",
    "robert lewandowski": "FWD",
    "lautaro martinez": "FWD",
    "rafael leao": "FWD",
    "khvicha kvaratskhelia": "FWD",
    "victor osimhen": "FWD",
    "alessandro bastoni": "DEF",
    "federico dimarco": "DEF",
    "theo hernandez": "DEF",
    "achraf hakimi": "DEF",
    "alphonso davies": "DEF",
    "josko gvardiol": "DEF",
    "ruben dias": "DEF"
}

def enrich_and_deduplicate():
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    pos_from_csv = get_position_map_from_csv()
    print(f"Loaded {len(pos_from_csv)} player positions from CSV.")
    
    cursor.execute("""
        SELECT id, name, age, nation, league, team, minutes_played, goals, assists,
               shots, shots_on_target, tackles_won, defense_interceptions, clearances,
               blocks, aerials_won, chances_created, passes_completed, progressive_passes,
               clean_sheets, saves, goals_conceded, position
        FROM players
    """)
    rows = cursor.fetchall()
    print(f"Initial total rows in database: {len(rows)}")
    
    # 1. Group records by canonical identity
    # Canonical key: normalized last name + first 2 chars of first name (to match "E. Haaland" with "Erling Haaland")
    def get_canonical_key(name_str):
        clean = normalize_text(name_str)
        parts = clean.split()
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        # Check if first part is a single letter abbreviation like "e" in "e haaland"
        if len(parts[0]) == 1:
            return f"{parts[-1]}_{parts[0]}"
        return f"{parts[-1]}_{parts[0][:3]}"

    canonical_groups = {}
    for r in rows:
        p_id, name, age, nation, league, team, mins, goals, assists, shots, sot, tkl, intc, clr, blk, aer, chn, pas, prg, cs, sv, gc, pos = r
        key = get_canonical_key(name)
        if key not in canonical_groups:
            canonical_groups[key] = []
        canonical_groups[key].append(r)
        
    print(f"Grouped into {len(canonical_groups)} distinct player identities.")
    
    ids_to_keep = []
    ids_to_delete = []
    
    for key, group in canonical_groups.items():
        if len(group) == 1:
            ids_to_keep.append(group[0])
        else:
            # Sort by minutes_played desc, then by full name length desc
            group_sorted = sorted(group, key=lambda x: (x[6] or 0, len(x[1] or "")), reverse=True)
            best_record = group_sorted[0]
            ids_to_keep.append(best_record)
            for duplicate in group_sorted[1:]:
                ids_to_delete.append(duplicate[0])
                
    print(f"Identified {len(ids_to_delete)} duplicate records for deletion.")
    
    # Remove phantom players (< 20 minutes and 0 goals and 0 assists)
    cleaned_records = []
    for r in ids_to_keep:
        mins = r[6] or 0
        goals = r[7] or 0
        assists = r[8] or 0
        name = r[1]
        norm = normalize_text(name)
        
        # Never delete known stars even if low minutes
        if norm in KNOWN_POSITIONS or any(k in norm for k in ["yamal", "haaland", "mbappe", "bellingham", "endrick"]):
            cleaned_records.append(r)
        elif mins < 25 and goals == 0 and assists == 0:
            ids_to_delete.append(r[0])
        else:
            cleaned_records.append(r)
            
    # Execute deletions
    if ids_to_delete:
        cursor.executemany("DELETE FROM players WHERE id = ?", [(i,) for i in ids_to_delete])
        conn.commit()
    print(f"Deleted {len(ids_to_delete)} rows (duplicates and phantoms).")
    
    # Now assign proper positions and updated stats
    updated_count = 0
    for r in cleaned_records:
        p_id = r[0]
        name = r[1]
        norm = normalize_text(name)
        shots = r[9] or 0
        goals = r[7] or 0
        tackles = r[11] or 0
        interceptions = r[12] or 0
        clearances = r[13] or 0
        current_pos = r[22]
        
        # Determine position
        final_pos = "MID" # default
        
        # Priority 1: Known Star dictionary
        for star_norm, pos in KNOWN_POSITIONS.items():
            if star_norm in norm or norm in star_norm:
                final_pos = pos
                break
        else:
            # Priority 2: Match from CSV
            if norm in pos_from_csv:
                final_pos = pos_from_csv[norm]
            else:
                # Check fuzzy match in pos_from_csv
                matched = False
                parts = norm.split()
                if parts:
                    last_name = parts[-1]
                    for csv_name, pos in pos_from_csv.items():
                        if last_name in csv_name and len(last_name) >= 4:
                            final_pos = pos
                            matched = True
                            break
                if not matched:
                    # Priority 3: Statistical inference
                    defensive_score = tackles + interceptions + clearances
                    attacking_score = (goals * 4) + shots
                    if defensive_score > attacking_score * 2.5:
                        final_pos = "DEF"
                    elif attacking_score > defensive_score * 1.5:
                        final_pos = "FWD"
                    else:
                        final_pos = "MID"
                        
        cursor.execute("UPDATE players SET position = ? WHERE id = ?", (final_pos, p_id))
        updated_count += 1
        
    conn.commit()
    
    # Check final counts and position distribution
    cursor.execute("SELECT position, COUNT(*) FROM players GROUP BY position")
    dist = cursor.fetchall()
    print("\nFinal position distribution:")
    for pos, cnt in dist:
        print(f"  {pos}: {cnt} players")
        
    cursor.execute("SELECT COUNT(*) FROM players")
    final_total = cursor.fetchone()[0]
    print(f"\nTotal players remaining in database: {final_total}")
    
    conn.close()

if __name__ == "__main__":
    enrich_and_deduplicate()
