import sqlite3
import random

conn = sqlite3.connect("sql_app.db")
c = conn.cursor()

c.execute("SELECT max(id) FROM players")
curr_p_id = c.fetchone()[0] or 3200

c.execute("SELECT max(id) FROM player_competition_stats")
curr_c_id = c.fetchone()[0] or 6500

c.execute("SELECT lower(name) FROM players")
existing_names = set(row[0] for row in c.fetchall())

# Format: (name, nation, age, position, league, team, mins, goals, assists, shots, sot, chances, tackles, interc, clearances, blocks, yellow, red, contract_year, release_clause, wage_weekly, [competitions])
ALL_NEW_SQUAD_PLAYERS = [
    # ==========================================
    # IPSWICH TOWN (Premier League)
    # ==========================================
    ("Arijanet Muric", "Kosovo", 27, "GK", "Premier League", "Ipswich Town", 2880, 0, 0, 0, 0, 1, 2, 1, 74, 1, 2, 0, 2028, None, 40000, [
        ("Premier League", "league", 32, 2880, 0, 0, 0, 0, 1, 2, 1, 74, 1, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 0, 0, 0, 0, 0, 4, 0, "Fourth Round")
    ]),
    ("Leif Davis", "England", 26, "DEF", "Premier League", "Ipswich Town", 2970, 2, 8, 28, 9, 64, 76, 44, 52, 14, 5, 0, 2028, None, 45000, [
        ("Premier League", "league", 33, 2970, 2, 8, 28, 9, 64, 76, 44, 52, 14, "Regular Season")
    ]),
    ("Jacob Greaves", "England", 25, "DEF", "Premier League", "Ipswich Town", 2700, 2, 1, 20, 7, 8, 68, 56, 144, 32, 6, 0, 2029, None, 45000, [
        ("Premier League", "league", 30, 2700, 2, 1, 20, 7, 8, 68, 56, 144, 32, "Regular Season")
    ]),
    ("Luke Woolfenden", "England", 27, "DEF", "Premier League", "Ipswich Town", 2520, 1, 0, 14, 4, 6, 58, 48, 128, 26, 4, 0, 2027, None, 35000, [
        ("Premier League", "league", 28, 2520, 1, 0, 14, 4, 6, 58, 48, 128, 26, "Regular Season")
    ]),
    ("Axel Tuanzebe", "DR Congo", 28, "DEF", "Premier League", "Ipswich Town", 2340, 1, 1, 12, 3, 10, 62, 44, 96, 20, 5, 0, 2027, None, 40000, [
        ("Premier League", "league", 26, 2340, 1, 1, 12, 3, 10, 62, 44, 96, 20, "Regular Season")
    ]),
    ("Sam Morsy", "Egypt", 34, "MID", "Premier League", "Ipswich Town", 2880, 2, 3, 34, 10, 36, 96, 58, 44, 22, 11, 1, 2026, None, 40000, [
        ("Premier League", "league", 32, 2880, 2, 3, 34, 10, 36, 96, 58, 44, 22, "Regular Season")
    ]),
    ("Kalvin Phillips", "England", 30, "MID", "Premier League", "Ipswich Town", 2070, 1, 2, 22, 6, 28, 72, 42, 38, 14, 6, 0, 2026, None, 90000, [
        ("Premier League", "league", 23, 2070, 1, 2, 22, 6, 28, 72, 42, 38, 14, "Regular Season")
    ]),
    ("Sammie Szmodics", "Republic of Ireland", 30, "MID", "Premier League", "Ipswich Town", 2700, 10, 4, 72, 28, 48, 44, 22, 16, 6, 3, 0, 2028, None, 50000, [
        ("Premier League", "league", 30, 2700, 10, 4, 72, 28, 48, 44, 22, 16, 6, "Regular Season")
    ]),
    ("Liam Delap", "England", 23, "FWD", "Premier League", "Ipswich Town", 2790, 14, 3, 76, 34, 32, 34, 14, 18, 5, 7, 0, 2029, None, 55000, [
        ("Premier League", "league", 31, 2790, 14, 3, 76, 34, 32, 34, 14, 18, 5, "Regular Season")
    ]),
    ("Omari Hutchinson", "Jamaica", 22, "FWD", "Premier League", "Ipswich Town", 2610, 7, 6, 64, 24, 56, 42, 20, 12, 4, 3, 0, 2029, None, 45000, [
        ("Premier League", "league", 29, 2610, 7, 6, 64, 24, 56, 42, 20, 12, 4, "Regular Season")
    ]),
    ("Jack Clarke", "England", 25, "FWD", "Premier League", "Ipswich Town", 2430, 8, 5, 58, 22, 54, 36, 18, 10, 3, 2, 0, 2029, None, 50000, [
        ("Premier League", "league", 27, 2430, 8, 5, 58, 22, 54, 36, 18, 10, 3, "Regular Season")
    ]),
    ("Jens Cajuste", "Sweden", 27, "MID", "Premier League", "Ipswich Town", 2250, 2, 2, 24, 7, 32, 74, 44, 36, 16, 5, 0, 2027, None, 45000, [
        ("Premier League", "league", 25, 2250, 2, 2, 24, 7, 32, 74, 44, 36, 16, "Regular Season")
    ]),
    ("Dara O'Shea", "Republic of Ireland", 27, "DEF", "Premier League", "Ipswich Town", 2610, 2, 1, 20, 6, 8, 68, 52, 134, 28, 5, 0, 2029, None, 45000, [
        ("Premier League", "league", 29, 2610, 2, 1, 20, 6, 8, 68, 52, 134, 28, "Regular Season")
    ]),
    ("Ben Johnson", "England", 26, "DEF", "Premier League", "Ipswich Town", 2160, 1, 2, 14, 4, 22, 64, 38, 48, 12, 4, 0, 2028, None, 40000, [
        ("Premier League", "league", 24, 2160, 1, 2, 14, 4, 22, 64, 38, 48, 12, "Regular Season")
    ]),
    ("Conor Chaplin", "England", 29, "FWD", "Premier League", "Ipswich Town", 2070, 6, 4, 48, 18, 38, 32, 14, 12, 4, 3, 0, 2027, None, 35000, [
        ("Premier League", "league", 23, 2070, 6, 4, 48, 18, 38, 32, 14, 12, 4, "Regular Season")
    ]),
    ("Wes Burns", "Wales", 31, "FWD", "Premier League", "Ipswich Town", 1980, 4, 4, 38, 14, 36, 38, 18, 14, 3, 2, 0, 2026, None, 35000, [
        ("Premier League", "league", 22, 1980, 4, 4, 38, 14, 36, 38, 18, 14, 3, "Regular Season")
    ]),
    ("George Hirst", "England", 27, "FWD", "Premier League", "Ipswich Town", 1620, 5, 2, 42, 17, 20, 18, 8, 16, 4, 2, 0, 2027, None, 30000, [
        ("Premier League", "league", 18, 1620, 5, 2, 42, 17, 20, 18, 8, 16, 4, "Regular Season")
    ]),
    ("Massimo Luongo", "Australia", 33, "MID", "Premier League", "Ipswich Town", 1800, 1, 2, 18, 5, 24, 62, 36, 30, 12, 4, 0, 2026, None, 30000, [
        ("Premier League", "league", 20, 1800, 1, 2, 18, 5, 24, 62, 36, 30, 12, "Regular Season")
    ]),
    ("Christian Walton", "England", 30, "GK", "Premier League", "Ipswich Town", 900, 0, 0, 0, 0, 0, 1, 0, 24, 0, 0, 0, 2026, None, 25000, [
        ("Premier League", "league", 10, 900, 0, 0, 0, 0, 0, 1, 0, 24, 0, "Regular Season")
    ]),
    ("Cameron Burgess", "Australia", 30, "DEF", "Premier League", "Ipswich Town", 1890, 1, 0, 12, 3, 4, 52, 42, 102, 22, 3, 0, 2027, None, 30000, [
        ("Premier League", "league", 21, 1890, 1, 0, 12, 3, 4, 52, 42, 102, 22, "Regular Season")
    ]),

    # ==========================================
    # CD LEGANÉS (La Liga)
    # ==========================================
    ("Juan Soriano", "Spain", 28, "GK", "La Liga", "CD Leganés", 2970, 0, 0, 0, 0, 1, 2, 1, 72, 1, 2, 0, 2027, 20000000, 30000, [
        ("La Liga", "league", 33, 2970, 0, 0, 0, 0, 1, 2, 1, 72, 1, "Regular Season"),
        ("Copa del Rey", "domestic_cup", 2, 180, 0, 0, 0, 0, 0, 0, 0, 4, 0, "Round of 32")
    ]),
    ("Javi Hernández", "Spain", 28, "DEF", "La Liga", "CD Leganés", 2700, 2, 3, 18, 6, 32, 68, 42, 54, 14, 6, 0, 2028, 25000000, 35000, [
        ("La Liga", "league", 30, 2700, 2, 3, 18, 6, 32, 68, 42, 54, 14, "Regular Season")
    ]),
    ("Matija Nastasić", "Serbia", 33, "DEF", "La Liga", "CD Leganés", 2610, 2, 0, 16, 5, 6, 62, 48, 134, 28, 5, 0, 2026, 15000000, 45000, [
        ("La Liga", "league", 29, 2610, 2, 0, 16, 5, 6, 62, 48, 134, 28, "Regular Season")
    ]),
    ("Sergio González", "Spain", 34, "DEF", "La Liga", "CD Leganés", 2520, 1, 1, 12, 4, 8, 58, 44, 122, 24, 5, 0, 2026, 15000000, 35000, [
        ("La Liga", "league", 28, 2520, 1, 1, 12, 4, 8, 58, 44, 122, 24, "Regular Season")
    ]),
    ("Valentin Rosier", "France", 30, "DEF", "La Liga", "CD Leganés", 2430, 1, 2, 14, 4, 24, 74, 42, 48, 12, 4, 0, 2027, 20000000, 40000, [
        ("La Liga", "league", 27, 2430, 1, 2, 14, 4, 24, 74, 42, 48, 12, "Regular Season")
    ]),
    ("Yvan Neyou", "Cameroon", 29, "MID", "La Liga", "CD Leganés", 2700, 2, 2, 26, 7, 34, 86, 56, 42, 18, 8, 1, 2027, 25000000, 35000, [
        ("La Liga", "league", 30, 2700, 2, 2, 26, 7, 34, 86, 56, 42, 18, "Regular Season")
    ]),
    ("Renato Tapia", "Peru", 31, "MID", "La Liga", "CD Leganés", 2610, 1, 2, 22, 6, 28, 92, 62, 58, 22, 7, 0, 2026, 20000000, 50000, [
        ("La Liga", "league", 29, 2610, 1, 2, 22, 6, 28, 92, 62, 58, 22, "Regular Season"),
        ("Copa América 2024", "international", 3, 270, 0, 0, 2, 0, 1, 11, 7, 6, 2, "Group Stage")
    ]),
    ("Seydouba Cissé", "Guinea", 25, "MID", "La Liga", "CD Leganés", 2340, 4, 3, 42, 14, 44, 64, 34, 26, 10, 5, 0, 2028, 30000000, 35000, [
        ("La Liga", "league", 26, 2340, 4, 3, 42, 14, 44, 64, 34, 26, 10, "Regular Season")
    ]),
    ("Juan Cruz", "Spain", 26, "FWD", "La Liga", "CD Leganés", 2700, 8, 6, 68, 26, 58, 44, 22, 14, 5, 3, 0, 2028, 35000000, 40000, [
        ("La Liga", "league", 30, 2700, 8, 6, 68, 26, 58, 44, 22, 14, 5, "Regular Season")
    ]),
    ("Dani Raba", "Spain", 30, "FWD", "La Liga", "CD Leganés", 2250, 7, 5, 54, 20, 46, 36, 16, 12, 4, 4, 0, 2027, 25000000, 35000, [
        ("La Liga", "league", 25, 2250, 7, 5, 54, 20, 46, 36, 16, 12, 4, "Regular Season")
    ]),
    ("Sébastien Haller", "Ivory Coast", 32, "FWD", "La Liga", "CD Leganés", 2070, 9, 3, 58, 24, 28, 22, 10, 24, 6, 3, 0, 2026, 30000000, 75000, [
        ("La Liga", "league", 23, 2070, 9, 3, 58, 24, 28, 22, 10, 24, 6, "Regular Season"),
        ("AFCON 2024", "international", 5, 360, 2, 0, 10, 4, 4, 4, 2, 6, 1, "🏆 African Champion (Final Goalscorer)")
    ]),
    ("Miguel de la Fuente", "Spain", 27, "FWD", "La Liga", "CD Leganés", 2160, 8, 3, 52, 21, 26, 26, 12, 14, 4, 4, 0, 2027, 25000000, 35000, [
        ("La Liga", "league", 24, 2160, 8, 3, 52, 21, 26, 26, 12, 14, 4, "Regular Season")
    ]),
    ("Munir El Haddadi", "Morocco", 30, "FWD", "La Liga", "CD Leganés", 1980, 6, 4, 44, 18, 36, 32, 14, 10, 3, 2, 0, 2026, 20000000, 45000, [
        ("La Liga", "league", 22, 1980, 6, 4, 44, 18, 36, 32, 14, 10, 3, "Regular Season")
    ]),
    ("Óscar Rodríguez", "Spain", 28, "MID", "La Liga", "CD Leganés", 2250, 5, 5, 52, 19, 52, 48, 24, 16, 6, 4, 0, 2028, 30000000, 40000, [
        ("La Liga", "league", 25, 2250, 5, 5, 52, 19, 52, 48, 24, 16, 6, "Regular Season")
    ]),
    ("Roberto López", "Spain", 26, "MID", "La Liga", "CD Leganés", 1890, 4, 4, 38, 14, 42, 38, 18, 12, 4, 3, 0, 2027, 25000000, 30000, [
        ("La Liga", "league", 21, 1890, 4, 4, 38, 14, 42, 38, 18, 12, 4, "Regular Season")
    ]),
    ("Darko Brašanac", "Serbia", 34, "MID", "La Liga", "CD Leganés", 1800, 2, 1, 20, 6, 24, 62, 36, 28, 11, 5, 0, 2026, 15000000, 30000, [
        ("La Liga", "league", 20, 1800, 2, 1, 20, 6, 24, 62, 36, 28, 11, "Regular Season")
    ]),
    ("Enric Franquesa", "Spain", 29, "DEF", "La Liga", "CD Leganés", 1980, 1, 2, 12, 3, 22, 54, 32, 38, 9, 3, 0, 2027, 20000000, 30000, [
        ("La Liga", "league", 22, 1980, 1, 2, 12, 3, 22, 54, 32, 38, 9, "Regular Season")
    ]),
    ("Jorge Sáenz", "Spain", 29, "DEF", "La Liga", "CD Leganés", 2160, 1, 0, 14, 4, 6, 52, 40, 108, 22, 4, 0, 2027, 20000000, 30000, [
        ("La Liga", "league", 24, 2160, 1, 0, 14, 4, 6, 52, 40, 108, 22, "Regular Season")
    ]),
    ("Marko Dmitrović", "Serbia", 34, "GK", "La Liga", "CD Leganés", 900, 0, 0, 0, 0, 0, 1, 0, 22, 0, 1, 0, 2026, 15000000, 35000, [
        ("La Liga", "league", 10, 900, 0, 0, 0, 0, 0, 1, 0, 22, 0, "Regular Season")
    ]),

    # ==========================================
    # UD LAS PALMAS (La Liga)
    # ==========================================
    ("Jasper Cillessen", "Netherlands", 37, "GK", "La Liga", "UD Las Palmas", 2880, 0, 0, 0, 0, 1, 2, 1, 68, 1, 1, 0, 2026, 15000000, 45000, [
        ("La Liga", "league", 32, 2880, 0, 0, 0, 0, 1, 2, 1, 68, 1, "Regular Season")
    ]),
    ("Álex Muñoz", "Spain", 32, "DEF", "La Liga", "UD Las Palmas", 2610, 2, 2, 18, 6, 26, 68, 42, 62, 16, 5, 0, 2026, 20000000, 35000, [
        ("La Liga", "league", 29, 2610, 2, 2, 18, 6, 26, 68, 42, 62, 16, "Regular Season")
    ]),
    ("Mika Mármol", "Spain", 25, "DEF", "La Liga", "UD Las Palmas", 2880, 1, 1, 16, 5, 12, 74, 56, 128, 26, 4, 0, 2028, 35000000, 40000, [
        ("La Liga", "league", 32, 2880, 1, 1, 16, 5, 12, 74, 56, 128, 26, "Regular Season")
    ]),
    ("Scott McKenna", "Scotland", 29, "DEF", "La Liga", "UD Las Palmas", 2430, 1, 0, 14, 4, 4, 58, 46, 134, 28, 6, 0, 2027, 20000000, 40000, [
        ("La Liga", "league", 27, 2430, 1, 0, 14, 4, 4, 58, 46, 134, 28, "Regular Season"),
        ("UEFA Euro 2024", "international", 3, 230, 0, 0, 1, 0, 1, 6, 5, 11, 3, "Group Stage")
    ]),
    ("Viti Rozada", "Spain", 28, "DEF", "La Liga", "UD Las Palmas", 2340, 1, 3, 16, 5, 32, 64, 38, 44, 11, 4, 0, 2027, 20000000, 30000, [
        ("La Liga", "league", 26, 2340, 1, 3, 16, 5, 32, 64, 38, 44, 11, "Regular Season")
    ]),
    ("José Campaña", "Spain", 33, "MID", "La Liga", "UD Las Palmas", 2250, 2, 4, 28, 9, 44, 58, 32, 24, 10, 5, 0, 2026, 15000000, 40000, [
        ("La Liga", "league", 25, 2250, 2, 4, 28, 9, 44, 58, 32, 24, 10, "Regular Season")
    ]),
    ("Kirian Rodríguez", "Spain", 30, "MID", "La Liga", "UD Las Palmas", 2970, 6, 5, 54, 20, 68, 76, 44, 36, 14, 6, 0, 2028, 40000000, 50000, [
        ("La Liga", "league", 33, 2970, 6, 5, 54, 20, 68, 76, 44, 36, 14, "Club Captain")
    ]),
    ("Javi Muñoz", "Spain", 31, "MID", "La Liga", "UD Las Palmas", 2700, 3, 3, 34, 11, 42, 84, 52, 42, 18, 7, 0, 2027, 25000000, 35000, [
        ("La Liga", "league", 30, 2700, 3, 3, 34, 11, 42, 84, 52, 42, 18, "Regular Season")
    ]),
    ("Alberto Moleiro", "Spain", 22, "MID", "La Liga", "UD Las Palmas", 2880, 8, 7, 72, 28, 76, 52, 26, 18, 6, 3, 0, 2028, 60000000, 45000, [
        ("La Liga", "league", 32, 2880, 8, 7, 72, 28, 76, 52, 26, 18, 6, "Regular Season")
    ]),
    ("Sandro Ramírez", "Spain", 31, "FWD", "La Liga", "UD Las Palmas", 2430, 10, 4, 68, 27, 38, 34, 16, 14, 5, 4, 0, 2026, 25000000, 45000, [
        ("La Liga", "league", 27, 2430, 10, 4, 68, 27, 38, 34, 16, 14, 5, "Regular Season")
    ]),
    ("Fábio Silva", "Portugal", 24, "FWD", "La Liga", "UD Las Palmas", 2340, 9, 3, 62, 25, 34, 28, 12, 12, 4, 3, 0, 2028, 40000000, 50000, [
        ("La Liga", "league", 26, 2340, 9, 3, 62, 25, 34, 28, 12, 12, 4, "Regular Season")
    ]),
    ("Oli McBurnie", "Scotland", 30, "FWD", "La Liga", "UD Las Palmas", 1980, 6, 2, 48, 19, 22, 26, 10, 22, 5, 5, 0, 2027, 25000000, 45000, [
        ("La Liga", "league", 22, 1980, 6, 2, 48, 19, 22, 26, 10, 22, 5, "Regular Season")
    ]),
    ("Jaime Mata", "Spain", 37, "FWD", "La Liga", "UD Las Palmas", 1440, 4, 1, 32, 12, 18, 18, 8, 14, 3, 3, 0, 2026, 10000000, 30000, [
        ("La Liga", "league", 16, 1440, 4, 1, 32, 12, 18, 18, 8, 14, 3, "Regular Season")
    ]),
    ("Adnan Januzaj", "Belgium", 31, "FWD", "La Liga", "UD Las Palmas", 1800, 4, 5, 42, 16, 44, 28, 12, 10, 3, 2, 0, 2026, 20000000, 50000, [
        ("La Liga", "league", 20, 1800, 4, 5, 42, 16, 44, 28, 12, 10, 3, "Regular Season")
    ]),
    ("Benito Ramírez", "Spain", 31, "MID", "La Liga", "UD Las Palmas", 1710, 2, 3, 24, 8, 28, 44, 22, 16, 6, 3, 0, 2026, 15000000, 25000, [
        ("La Liga", "league", 19, 1710, 2, 3, 24, 8, 28, 44, 22, 16, 6, "Regular Season")
    ]),
    ("Enzo Loiodice", "France", 25, "MID", "La Liga", "UD Las Palmas", 2250, 3, 3, 32, 10, 36, 68, 38, 28, 12, 5, 0, 2028, 30000000, 35000, [
        ("La Liga", "league", 25, 2250, 3, 3, 32, 10, 36, 68, 38, 28, 12, "Regular Season")
    ]),
    ("Marvin Park", "Spain", 26, "DEF", "La Liga", "UD Las Palmas", 2160, 1, 3, 18, 6, 30, 62, 34, 36, 10, 4, 0, 2028, 25000000, 30000, [
        ("La Liga", "league", 24, 2160, 1, 3, 18, 6, 30, 62, 34, 36, 10, "Regular Season")
    ]),
    ("Álex Suárez", "Spain", 33, "DEF", "La Liga", "UD Las Palmas", 2340, 1, 0, 12, 3, 6, 58, 44, 116, 24, 6, 0, 2026, 15000000, 30000, [
        ("La Liga", "league", 26, 2340, 1, 0, 12, 3, 6, 58, 44, 116, 24, "Regular Season")
    ]),
    ("Dinko Horkaš", "Croatia", 27, "GK", "La Liga", "UD Las Palmas", 810, 0, 0, 0, 0, 0, 1, 0, 18, 0, 0, 0, 2027, 15000000, 25000, [
        ("La Liga", "league", 9, 810, 0, 0, 0, 0, 0, 1, 0, 18, 0, "Regular Season")
    ]),

    # ==========================================
    # FC ST. PAULI (Bundesliga)
    # ==========================================
    ("Nikola Vasilj", "Bosnia and Herzegovina", 30, "GK", "Bundesliga", "FC St. Pauli", 2880, 0, 0, 0, 0, 1, 2, 1, 72, 1, 1, 0, 2027, None, 25000, [
        ("Bundesliga", "league", 32, 2880, 0, 0, 0, 0, 1, 2, 1, 72, 1, "Regular Season")
    ]),
    ("Philipp Treu", "Germany", 25, "DEF", "Bundesliga", "FC St. Pauli", 2610, 1, 4, 18, 5, 34, 72, 44, 52, 14, 5, 0, 2027, None, 25000, [
        ("Bundesliga", "league", 29, 2610, 1, 4, 18, 5, 34, 72, 44, 52, 14, "Regular Season")
    ]),
    ("Karol Mets", "Estonia", 33, "DEF", "Bundesliga", "FC St. Pauli", 2700, 1, 0, 14, 4, 6, 62, 52, 138, 28, 4, 0, 2026, None, 25000, [
        ("Bundesliga", "league", 30, 2700, 1, 0, 14, 4, 6, 62, 52, 138, 28, "Regular Season")
    ]),
    ("Eric Smith", "Sweden", 29, "DEF", "Bundesliga", "FC St. Pauli", 2790, 3, 3, 24, 8, 22, 78, 58, 126, 32, 6, 0, 2027, None, 30000, [
        ("Bundesliga", "league", 31, 2790, 3, 3, 24, 8, 22, 78, 58, 126, 32, "Regular Season")
    ]),
    ("Hauke Wahl", "Germany", 32, "DEF", "Bundesliga", "FC St. Pauli", 2880, 1, 1, 16, 5, 8, 66, 54, 144, 30, 5, 0, 2026, None, 28000, [
        ("Bundesliga", "league", 32, 2880, 1, 1, 16, 5, 8, 66, 54, 144, 30, "Regular Season")
    ]),
    ("Manolis Saliakas", "Greece", 29, "DEF", "Bundesliga", "FC St. Pauli", 2520, 2, 3, 22, 7, 36, 76, 42, 48, 12, 6, 0, 2026, None, 25000, [
        ("Bundesliga", "league", 28, 2520, 2, 3, 22, 7, 36, 76, 42, 48, 12, "Regular Season")
    ]),
    ("Jackson Irvine", "Australia", 33, "MID", "Bundesliga", "FC St. Pauli", 2970, 6, 5, 54, 20, 52, 88, 56, 48, 22, 8, 0, 2026, None, 35000, [
        ("Bundesliga", "league", 33, 2970, 6, 5, 54, 20, 52, 88, 56, 48, 22, "Club Captain")
    ]),
    ("Robert Wagner", "Germany", 23, "MID", "Bundesliga", "FC St. Pauli", 2340, 2, 3, 24, 7, 32, 74, 46, 36, 16, 5, 0, 2028, None, 22000, [
        ("Bundesliga", "league", 26, 2340, 2, 3, 24, 7, 32, 74, 46, 36, 16, "Regular Season")
    ]),
    ("Carlo Boukhalfa", "Germany", 27, "MID", "Bundesliga", "FC St. Pauli", 2160, 3, 2, 32, 10, 28, 62, 38, 30, 14, 4, 0, 2027, None, 20000, [
        ("Bundesliga", "league", 24, 2160, 3, 2, 32, 10, 28, 62, 38, 30, 14, "Regular Season")
    ]),
    ("Johannes Eggestein", "Germany", 28, "FWD", "Bundesliga", "FC St. Pauli", 2520, 9, 5, 68, 28, 38, 28, 12, 16, 5, 3, 0, 2027, None, 30000, [
        ("Bundesliga", "league", 28, 2520, 9, 5, 68, 28, 38, 28, 12, 16, 5, "Regular Season")
    ]),
    ("Morgan Guilavogui", "Guinea", 28, "FWD", "Bundesliga", "FC St. Pauli", 2430, 8, 4, 62, 25, 34, 32, 14, 14, 4, 4, 0, 2027, None, 25000, [
        ("Bundesliga", "league", 27, 2430, 8, 4, 62, 25, 34, 32, 14, 14, 4, "Regular Season")
    ]),
    ("Oladapo Afolayan", "England", 28, "FWD", "Bundesliga", "FC St. Pauli", 2340, 7, 5, 58, 22, 46, 36, 16, 12, 4, 3, 0, 2027, None, 25000, [
        ("Bundesliga", "league", 26, 2340, 7, 5, 58, 22, 46, 36, 16, 12, 4, "Regular Season")
    ]),
    ("Danel Sinani", "Luxembourg", 29, "MID", "Bundesliga", "FC St. Pauli", 1890, 4, 4, 36, 14, 38, 42, 20, 14, 5, 3, 0, 2026, None, 22000, [
        ("Bundesliga", "league", 21, 1890, 4, 4, 36, 14, 38, 42, 20, 14, 5, "Regular Season")
    ]),
    ("Connor Metcalfe", "Australia", 26, "MID", "Bundesliga", "FC St. Pauli", 2070, 3, 3, 30, 10, 32, 58, 34, 24, 11, 4, 0, 2027, None, 22000, [
        ("Bundesliga", "league", 23, 2070, 3, 3, 30, 10, 32, 58, 34, 24, 11, "Regular Season")
    ]),
    ("Elias Saad", "Tunisia", 26, "FWD", "Bundesliga", "FC St. Pauli", 2160, 6, 4, 48, 19, 42, 34, 16, 10, 3, 3, 0, 2027, None, 22000, [
        ("Bundesliga", "league", 24, 2160, 6, 4, 48, 19, 42, 34, 16, 10, 3, "Regular Season")
    ]),
    ("David Nemeth", "Austria", 25, "DEF", "Bundesliga", "FC St. Pauli", 1980, 1, 0, 12, 3, 4, 48, 38, 92, 18, 3, 0, 2027, None, 20000, [
        ("Bundesliga", "league", 22, 1980, 1, 0, 12, 3, 4, 48, 38, 92, 18, "Regular Season")
    ]),
    ("Lars Ritzka", "Germany", 28, "DEF", "Bundesliga", "FC St. Pauli", 1800, 1, 2, 10, 3, 18, 52, 28, 34, 8, 3, 0, 2026, None, 18000, [
        ("Bundesliga", "league", 20, 1800, 1, 2, 10, 3, 18, 52, 28, 34, 8, "Regular Season")
    ]),
    ("Sascha Burchert", "Germany", 36, "GK", "Bundesliga", "FC St. Pauli", 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, 0, 0, 2026, None, 15000, [
        ("Bundesliga", "league", 6, 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, "Regular Season")
    ]),

    # ==========================================
    # 1. FC HEIDENHEIM (Bundesliga & UEFA Conference League)
    # ==========================================
    ("Kevin Müller", "Germany", 35, "GK", "Bundesliga", "1. FC Heidenheim", 3060, 0, 0, 0, 0, 1, 2, 1, 84, 1, 2, 0, 2026, None, 30000, [
        ("Bundesliga", "league", 34, 3060, 0, 0, 0, 0, 1, 2, 1, 84, 1, "Regular Season"),
        ("UEFA Conference League", "continental", 8, 720, 0, 0, 0, 0, 0, 1, 0, 22, 0, "Knockout Phase")
    ]),
    ("Jonas Föhrenbach", "Germany", 30, "DEF", "Bundesliga", "1. FC Heidenheim", 2700, 1, 3, 18, 5, 32, 68, 44, 58, 16, 5, 0, 2027, None, 28000, [
        ("Bundesliga", "league", 30, 2700, 1, 3, 18, 5, 32, 68, 44, 58, 16, "Regular Season"),
        ("UEFA Conference League", "continental", 7, 610, 0, 1, 3, 1, 5, 12, 7, 9, 2, "Knockout Phase")
    ]),
    ("Patrick Mainka", "Germany", 31, "DEF", "Bundesliga", "1. FC Heidenheim", 3060, 3, 1, 22, 8, 8, 72, 64, 168, 38, 4, 0, 2027, None, 35000, [
        ("Bundesliga", "league", 34, 3060, 3, 1, 22, 8, 8, 72, 64, 168, 38, "Club Captain"),
        ("UEFA Conference League", "continental", 8, 720, 1, 0, 5, 2, 1, 14, 11, 32, 6, "Knockout Phase")
    ]),
    ("Benedikt Gimber", "Germany", 29, "DEF", "Bundesliga", "1. FC Heidenheim", 2880, 2, 1, 18, 6, 8, 78, 58, 154, 34, 7, 1, 2027, None, 30000, [
        ("Bundesliga", "league", 32, 2880, 2, 1, 18, 6, 8, 78, 58, 154, 34, "Regular Season")
    ]),
    ("Marnon Busch", "Germany", 31, "DEF", "Bundesliga", "1. FC Heidenheim", 2430, 1, 2, 14, 4, 24, 64, 38, 46, 12, 4, 0, 2026, None, 25000, [
        ("Bundesliga", "league", 27, 2430, 1, 2, 14, 4, 24, 64, 38, 46, 12, "Regular Season")
    ]),
    ("Lennard Maloney", "United States", 26, "MID", "Bundesliga", "1. FC Heidenheim", 2790, 2, 2, 24, 7, 26, 94, 62, 54, 24, 8, 0, 2027, None, 30000, [
        ("Bundesliga", "league", 31, 2790, 2, 2, 24, 7, 26, 94, 62, 54, 24, "Regular Season")
    ]),
    ("Jan Schöppner", "Germany", 27, "MID", "Bundesliga", "1. FC Heidenheim", 2700, 5, 3, 44, 16, 36, 82, 48, 42, 18, 6, 0, 2028, None, 30000, [
        ("Bundesliga", "league", 30, 2700, 5, 3, 44, 16, 36, 82, 48, 42, 18, "Regular Season"),
        ("UEFA Conference League", "continental", 7, 600, 2, 1, 8, 3, 7, 14, 8, 6, 2, "Knockout Phase")
    ]),
    ("Paul Wanner", "Germany", 20, "MID", "Bundesliga", "1. FC Heidenheim", 2520, 8, 6, 62, 25, 68, 46, 24, 16, 6, 3, 0, 2028, None, 40000, [
        ("Bundesliga", "league", 28, 2520, 8, 6, 62, 25, 68, 46, 24, 16, 6, "Regular Season"),
        ("UEFA Conference League", "continental", 7, 580, 3, 2, 14, 6, 12, 8, 4, 3, 1, "Knockout Phase Hero")
    ]),
    ("Léo Scienza", "Brazil", 27, "FWD", "Bundesliga", "1. FC Heidenheim", 2430, 7, 6, 58, 24, 52, 42, 20, 14, 4, 4, 0, 2027, None, 28000, [
        ("Bundesliga", "league", 27, 2430, 7, 6, 58, 24, 52, 42, 20, 14, 4, "Regular Season"),
        ("UEFA Conference League", "continental", 6, 480, 2, 2, 10, 4, 8, 6, 3, 2, 1, "Knockout Phase")
    ]),
    ("Marvin Pieringer", "Germany", 26, "FWD", "Bundesliga", "1. FC Heidenheim", 2610, 11, 5, 74, 32, 38, 34, 16, 18, 5, 5, 0, 2028, None, 32000, [
        ("Bundesliga", "league", 29, 2610, 11, 5, 74, 32, 38, 34, 16, 18, 5, "Regular Season"),
        ("UEFA Conference League", "continental", 7, 590, 3, 1, 16, 7, 6, 5, 2, 3, 1, "Knockout Phase")
    ]),
    ("Mikkel Kaufmann", "Denmark", 25, "FWD", "Bundesliga", "1. FC Heidenheim", 1980, 6, 3, 44, 18, 24, 24, 10, 14, 3, 2, 0, 2027, None, 25000, [
        ("Bundesliga", "league", 22, 1980, 6, 3, 44, 18, 24, 24, 10, 14, 3, "Regular Season")
    ]),
    ("Mathias Honsak", "Austria", 29, "MID", "Bundesliga", "1. FC Heidenheim", 2070, 5, 4, 42, 16, 38, 38, 18, 12, 4, 3, 0, 2027, None, 25000, [
        ("Bundesliga", "league", 23, 2070, 5, 4, 42, 16, 38, 38, 18, 12, 4, "Regular Season")
    ]),
    ("Adrian Beck", "Germany", 29, "MID", "Bundesliga", "1. FC Heidenheim", 2160, 4, 3, 34, 12, 34, 52, 28, 22, 8, 4, 0, 2027, None, 24000, [
        ("Bundesliga", "league", 24, 2160, 4, 3, 34, 12, 34, 52, 28, 22, 8, "Regular Season")
    ]),
    ("Sirlord Conteh", "Germany", 30, "FWD", "Bundesliga", "1. FC Heidenheim", 1890, 5, 3, 38, 15, 28, 28, 12, 10, 3, 3, 0, 2027, None, 24000, [
        ("Bundesliga", "league", 21, 1890, 5, 3, 38, 15, 28, 28, 12, 10, 3, "Regular Season")
    ]),
    ("Omar Traoré", "Germany", 28, "DEF", "Bundesliga", "1. FC Heidenheim", 2250, 1, 2, 14, 4, 26, 68, 36, 42, 11, 4, 0, 2027, None, 24000, [
        ("Bundesliga", "league", 25, 2250, 1, 2, 14, 4, 26, 68, 36, 42, 11, "Regular Season")
    ]),
    ("Tim Siersleben", "Germany", 26, "DEF", "Bundesliga", "1. FC Heidenheim", 2070, 1, 0, 12, 3, 6, 54, 42, 98, 22, 3, 0, 2027, None, 22000, [
        ("Bundesliga", "league", 23, 2070, 1, 0, 12, 3, 6, 54, 42, 98, 22, "Regular Season")
    ]),
    ("Norman Theuerkauf", "Germany", 39, "MID", "Bundesliga", "1. FC Heidenheim", 1260, 1, 1, 10, 3, 16, 42, 24, 22, 8, 2, 0, 2026, None, 20000, [
        ("Bundesliga", "league", 14, 1260, 1, 1, 10, 3, 16, 42, 24, 22, 8, "Veteran Leader")
    ]),
    ("Frank Feller", "Germany", 22, "GK", "Bundesliga", "1. FC Heidenheim", 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, 0, 0, 2028, None, 15000, [
        ("Bundesliga", "league", 6, 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, "Regular Season")
    ]),

    # ==========================================
    # TOULOUSE FC (Ligue 1)
    # ==========================================
    ("Guillaume Restes", "France", 21, "GK", "Ligue 1", "Toulouse FC", 3060, 0, 0, 0, 0, 1, 2, 1, 78, 1, 1, 0, 2028, None, 45000, [
        ("Ligue 1", "league", 34, 3060, 0, 0, 0, 0, 1, 2, 1, 78, 1, "Regular Season"),
        ("Olympics 2024", "international", 6, 540, 0, 0, 0, 0, 0, 1, 0, 16, 0, "🥈 Olympic Silver Medalist")
    ]),
    ("Gabriel Suazo", "Chile", 29, "DEF", "Ligue 1", "Toulouse FC", 2790, 2, 4, 22, 7, 44, 82, 46, 54, 16, 6, 0, 2027, None, 40000, [
        ("Ligue 1", "league", 31, 2790, 2, 4, 22, 7, 44, 82, 46, 54, 16, "Regular Season"),
        ("Copa América 2024", "international", 3, 270, 0, 0, 2, 0, 3, 9, 6, 5, 2, "Group Stage")
    ]),
    ("Rasmus Nicolaisen", "Denmark", 29, "DEF", "Ligue 1", "Toulouse FC", 2970, 3, 1, 24, 8, 8, 74, 62, 162, 34, 5, 0, 2027, None, 45000, [
        ("Ligue 1", "league", 33, 2970, 3, 1, 24, 8, 8, 74, 62, 162, 34, "Regular Season")
    ]),
    ("Charlie Cresswell", "England", 24, "DEF", "Ligue 1", "Toulouse FC", 2610, 2, 0, 18, 6, 6, 68, 54, 138, 28, 6, 0, 2028, None, 35000, [
        ("Ligue 1", "league", 29, 2610, 2, 0, 18, 6, 6, 68, 54, 138, 28, "Regular Season")
    ]),
    ("Djibril Sidibé", "France", 34, "DEF", "Ligue 1", "Toulouse FC", 2340, 1, 2, 14, 4, 26, 66, 38, 48, 12, 4, 0, 2026, None, 50000, [
        ("Ligue 1", "league", 26, 2340, 1, 2, 14, 4, 26, 66, 38, 48, 12, "World Cup Winner")
    ]),
    ("Cristian Cásseres Jr.", "Venezuela", 26, "MID", "Ligue 1", "Toulouse FC", 2700, 3, 4, 38, 12, 48, 88, 52, 42, 18, 7, 0, 2027, None, 40000, [
        ("Ligue 1", "league", 30, 2700, 3, 4, 38, 12, 48, 88, 52, 42, 18, "Regular Season"),
        ("Copa América 2024", "international", 4, 310, 0, 1, 4, 1, 4, 10, 6, 4, 1, "Quarter-Finalist")
    ]),
    ("Vincent Sierro", "Switzerland", 30, "MID", "Ligue 1", "Toulouse FC", 2880, 7, 5, 56, 22, 62, 82, 46, 38, 16, 6, 0, 2026, None, 45000, [
        ("Ligue 1", "league", 32, 2880, 7, 5, 56, 22, 62, 82, 46, 38, 16, "Club Captain"),
        ("UEFA Euro 2024", "international", 4, 210, 0, 0, 3, 1, 3, 7, 4, 3, 1, "Quarter-Finalist")
    ]),
    ("Zakaria Aboukhlal", "Morocco", 26, "FWD", "Ligue 1", "Toulouse FC", 2520, 12, 4, 78, 34, 44, 36, 16, 14, 5, 4, 0, 2027, None, 50000, [
        ("Ligue 1", "league", 28, 2520, 12, 4, 78, 34, 44, 36, 16, 14, 5, "Regular Season")
    ]),
    ("Yann Gboho", "France", 25, "MID", "Ligue 1", "Toulouse FC", 2610, 6, 6, 58, 22, 58, 44, 22, 16, 6, 3, 0, 2028, None, 35000, [
        ("Ligue 1", "league", 29, 2610, 6, 6, 58, 22, 58, 44, 22, 16, 6, "Regular Season")
    ]),
    ("Aron Dønnum", "Norway", 28, "FWD", "Ligue 1", "Toulouse FC", 2430, 4, 5, 46, 16, 42, 48, 26, 18, 6, 5, 0, 2027, None, 35000, [
        ("Ligue 1", "league", 27, 2430, 4, 5, 46, 16, 42, 48, 26, 18, 6, "Regular Season")
    ]),
    ("Frank Magri", "Cameroon", 26, "FWD", "Ligue 1", "Toulouse FC", 2250, 8, 3, 54, 22, 26, 26, 12, 14, 4, 3, 0, 2027, None, 32000, [
        ("Ligue 1", "league", 25, 2250, 8, 3, 54, 22, 26, 26, 12, 14, 4, "Regular Season"),
        ("AFCON 2024", "international", 4, 290, 1, 0, 6, 3, 2, 3, 1, 2, 0, "Round of 16")
    ]),
    ("Shavy Babicka", "Gabon", 26, "FWD", "Ligue 1", "Toulouse FC", 2160, 7, 3, 48, 20, 32, 30, 14, 12, 4, 3, 0, 2027, None, 30000, [
        ("Ligue 1", "league", 24, 2160, 7, 3, 48, 20, 32, 30, 14, 12, 4, "Regular Season")
    ]),
    ("Joshua King", "Norway", 34, "FWD", "Ligue 1", "Toulouse FC", 1890, 6, 2, 42, 18, 24, 20, 8, 14, 3, 2, 0, 2026, None, 45000, [
        ("Ligue 1", "league", 21, 1890, 6, 2, 42, 18, 24, 20, 8, 14, 3, "Regular Season")
    ]),
    ("Niklas Schmidt", "Germany", 28, "MID", "Ligue 1", "Toulouse FC", 2070, 3, 4, 34, 11, 38, 54, 28, 22, 8, 4, 0, 2027, None, 32000, [
        ("Ligue 1", "league", 23, 2070, 3, 4, 34, 11, 38, 54, 28, 22, 8, "Regular Season")
    ]),
    ("Warren Kamanzi", "Norway", 25, "DEF", "Ligue 1", "Toulouse FC", 1980, 1, 2, 12, 3, 24, 58, 32, 36, 10, 3, 0, 2027, None, 25000, [
        ("Ligue 1", "league", 22, 1980, 1, 2, 12, 3, 24, 58, 32, 36, 10, "Regular Season")
    ]),
    ("Ümit Akdağ", "Romania", 22, "DEF", "Ligue 1", "Toulouse FC", 1800, 1, 0, 10, 3, 4, 48, 36, 88, 18, 3, 0, 2028, None, 22000, [
        ("Ligue 1", "league", 20, 1800, 1, 0, 10, 3, 4, 48, 36, 88, 18, "Regular Season")
    ]),
    ("Denis Genreau", "Australia", 27, "MID", "Ligue 1", "Toulouse FC", 1620, 2, 2, 20, 6, 26, 52, 26, 20, 8, 3, 0, 2026, None, 25000, [
        ("Ligue 1", "league", 18, 1620, 2, 2, 20, 6, 26, 52, 26, 20, 8, "Regular Season")
    ]),
    ("Álex Domínguez", "Spain", 28, "GK", "Ligue 1", "Toulouse FC", 720, 0, 0, 0, 0, 0, 1, 0, 16, 0, 0, 0, 2026, None, 22000, [
        ("Ligue 1", "league", 8, 720, 0, 0, 0, 0, 0, 1, 0, 16, 0, "Regular Season")
    ]),

    # ==========================================
    # LE HAVRE AC (Ligue 1)
    # ==========================================
    ("Arthur Desmas", "France", 32, "GK", "Ligue 1", "Le Havre AC", 2970, 0, 0, 0, 0, 1, 2, 1, 76, 1, 2, 0, 2026, None, 28000, [
        ("Ligue 1", "league", 33, 2970, 0, 0, 0, 0, 1, 2, 1, 76, 1, "Regular Season")
    ]),
    ("Christopher Opéri", "Ivory Coast", 29, "DEF", "Ligue 1", "Le Havre AC", 2790, 3, 5, 32, 11, 48, 78, 46, 58, 16, 7, 1, 2026, None, 30000, [
        ("Ligue 1", "league", 31, 2790, 3, 5, 32, 11, 48, 78, 46, 58, 16, "Regular Season")
    ]),
    ("Gautier Lloris", "France", 31, "DEF", "Ligue 1", "Le Havre AC", 2880, 2, 1, 18, 6, 8, 68, 54, 152, 32, 4, 0, 2026, None, 32000, [
        ("Ligue 1", "league", 32, 2880, 2, 1, 18, 6, 8, 68, 54, 152, 32, "Regular Season")
    ]),
    ("Étienne Youté Kinkoué", "France", 24, "DEF", "Ligue 1", "Le Havre AC", 2700, 1, 0, 14, 4, 6, 64, 52, 142, 28, 5, 1, 2027, None, 25000, [
        ("Ligue 1", "league", 30, 2700, 1, 0, 14, 4, 6, 64, 52, 142, 28, "Regular Season")
    ]),
    ("Yoann Salmier", "France", 33, "DEF", "Ligue 1", "Le Havre AC", 2430, 1, 1, 12, 3, 6, 56, 44, 118, 22, 4, 0, 2026, None, 26000, [
        ("Ligue 1", "league", 27, 2430, 1, 1, 12, 3, 6, 56, 44, 118, 22, "Regular Season")
    ]),
    ("Loïc Négo", "Hungary", 35, "DEF", "Ligue 1", "Le Havre AC", 2520, 1, 4, 20, 6, 36, 72, 40, 48, 12, 5, 0, 2026, None, 30000, [
        ("Ligue 1", "league", 28, 2520, 1, 4, 20, 6, 36, 72, 40, 48, 12, "Regular Season"),
        ("UEFA Euro 2024", "international", 2, 90, 0, 0, 1, 0, 1, 3, 2, 2, 1, "Group Stage")
    ]),
    ("Abdoulaye Touré", "Guinea", 32, "MID", "Ligue 1", "Le Havre AC", 2880, 4, 2, 34, 11, 32, 92, 58, 48, 20, 7, 0, 2026, None, 35000, [
        ("Ligue 1", "league", 32, 2880, 4, 2, 34, 11, 32, 92, 58, 48, 20, "Regular Season"),
        ("AFCON 2024", "international", 4, 310, 1, 0, 5, 2, 2, 9, 5, 4, 1, "Quarter-Finalist")
    ]),
    ("Rassoul Ndiaye", "Senegal", 24, "MID", "Ligue 1", "Le Havre AC", 2340, 3, 3, 32, 10, 36, 68, 42, 32, 14, 4, 0, 2027, None, 25000, [
        ("Ligue 1", "league", 26, 2340, 3, 3, 32, 10, 36, 68, 42, 32, 14, "Regular Season")
    ]),
    ("Yassine Kechta", "Morocco", 24, "MID", "Ligue 1", "Le Havre AC", 2610, 4, 5, 44, 16, 54, 76, 44, 28, 12, 5, 0, 2027, None, 25000, [
        ("Ligue 1", "league", 29, 2610, 4, 5, 44, 16, 54, 76, 44, 28, 12, "Regular Season"),
        ("Olympics 2024", "international", 6, 460, 1, 2, 7, 3, 10, 14, 7, 5, 2, "🥉 Olympic Bronze Medalist")
    ]),
    ("Josué Casimir", "France", 24, "FWD", "Ligue 1", "Le Havre AC", 2430, 5, 6, 48, 19, 46, 42, 22, 14, 4, 3, 0, 2027, None, 22000, [
        ("Ligue 1", "league", 27, 2430, 5, 6, 48, 19, 46, 42, 22, 14, 4, "Regular Season")
    ]),
    ("Emmanuel Sabbi", "United States", 28, "FWD", "Ligue 1", "Le Havre AC", 2520, 8, 4, 64, 26, 40, 36, 16, 14, 4, 4, 0, 2027, None, 28000, [
        ("Ligue 1", "league", 28, 2520, 8, 4, 64, 26, 40, 36, 16, 14, 4, "Regular Season")
    ]),
    ("Issa Soumaré", "Senegal", 25, "FWD", "Ligue 1", "Le Havre AC", 2160, 6, 3, 46, 18, 30, 28, 12, 12, 3, 3, 0, 2027, None, 22000, [
        ("Ligue 1", "league", 24, 2160, 6, 3, 46, 18, 30, 28, 12, 12, 3, "Regular Season")
    ]),
    ("Daler Kuzyaev", "Russia", 33, "MID", "Ligue 1", "Le Havre AC", 2340, 4, 3, 38, 13, 42, 64, 36, 30, 12, 4, 1, 2026, None, 40000, [
        ("Ligue 1", "league", 26, 2340, 4, 3, 38, 13, 42, 64, 36, 30, 12, "Regular Season")
    ]),
    ("Oussama Targhalline", "Morocco", 24, "MID", "Ligue 1", "Le Havre AC", 2250, 2, 3, 26, 8, 38, 72, 44, 26, 11, 4, 0, 2027, None, 22000, [
        ("Ligue 1", "league", 25, 2250, 2, 3, 26, 8, 38, 72, 44, 26, 11, "Regular Season"),
        ("Olympics 2024", "international", 6, 490, 1, 1, 6, 2, 8, 12, 8, 4, 1, "🥉 Olympic Bronze Medalist")
    ]),
    ("Yanis Zouaoui", "France", 27, "DEF", "Ligue 1", "Le Havre AC", 1980, 1, 2, 14, 4, 22, 58, 32, 38, 10, 3, 0, 2027, None, 20000, [
        ("Ligue 1", "league", 22, 1980, 1, 2, 14, 4, 22, 58, 32, 38, 10, "Regular Season")
    ]),
    ("Timothée Pembélé", "France", 23, "DEF", "Ligue 1", "Le Havre AC", 1890, 1, 1, 12, 3, 20, 54, 30, 34, 8, 2, 0, 2027, None, 25000, [
        ("Ligue 1", "league", 21, 1890, 1, 1, 12, 3, 20, 54, 30, 34, 8, "Regular Season")
    ]),
    ("Mathieu Gorgelin", "France", 36, "GK", "Ligue 1", "Le Havre AC", 630, 0, 0, 0, 0, 0, 1, 0, 16, 0, 0, 0, 2026, None, 18000, [
        ("Ligue 1", "league", 7, 630, 0, 0, 0, 0, 0, 1, 0, 16, 0, "Regular Season")
    ])
]

inserted_total = 0
comp_total = 0

for p in ALL_NEW_SQUAD_PLAYERS:
    name = p[0]
    if name.lower() in existing_names:
        continue
    
    curr_p_id += 1
    nation, age, pos, league, team, mins, goals, assists = p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]
    shots, sot, chances, tackles, interc, clears, blocks, yellow, red = p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17]
    contract_year, release_clause, wage = p[18], p[19], p[20]
    comps = p[21]
    
    # Modern Valuation Model calculation
    base_val = 10000000.0
    if goals + assists > 15:
        base_val += (goals * 3500000.0) + (assists * 2200000.0)
    elif goals + assists > 8:
        base_val += (goals * 2500000.0) + (assists * 1600000.0)
    else:
        base_val += (goals * 1500000.0) + (assists * 1000000.0)
        
    if pos in ("DEF", "GK"):
        base_val += (tackles * 300000.0) + (interc * 250000.0) + (clears * 120000.0)
    elif pos == "MID":
        base_val += (chances * 400000.0) + (tackles * 180000.0)
        
    if age <= 21:
        base_val *= 1.35
    elif age <= 24:
        base_val *= 1.20
    elif age <= 27:
        base_val *= 1.08
    elif age <= 30:
        base_val *= 0.88
    else:
        base_val *= 0.55
        
    if contract_year >= 2029:
        base_val *= 1.15
    elif contract_year >= 2028:
        base_val *= 1.06
    elif contract_year == 2026:
        base_val *= 0.75
        
    if release_clause and release_clause < base_val:
        base_val = float(release_clause)
        
    mkt_val = round(base_val, -5)
    
    height = random.choice([178, 182, 185, 188, 191]) if pos in ("DEF", "GK") else random.choice([172, 175, 178, 180, 184])
    weight = round(height * 0.42, 1)
    drib_comp = round(chances * 0.65)
    drib_att = round(drib_comp * 1.5)
    passes_comp = round(mins * 0.52)
    passes_att = round(passes_comp * 1.23)
    prog_passes = round(passes_comp * 0.11)
    aerials = round((tackles + clears) * 0.3)
    touches = round(passes_att * 1.38)
    apps = max(18, round(mins / 85))
    cs = round(apps * 0.3) if pos in ("DEF", "GK") else 0
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
    inserted_total += 1
    existing_names.add(name.lower())
    
    # Insert competition stats
    for comp in comps:
        curr_c_id += 1
        c_name, c_type, c_apps, c_mins, c_g, c_a, c_sh, c_sot, c_ch, c_tack, c_int, c_clear, c_blk, c_stage = comp
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
            curr_c_id, curr_p_id, c_name, c_type, "2024-2026",
            c_apps, c_mins, c_g, c_a,
            c_sh, c_sot, c_ch,
            c_tack, c_int, c_clear, c_blk,
            random.choice([0, 1, 2]), 0, c_stage
        ))
        comp_total += 1

conn.commit()
print(f"COMPLETE: Inserted {inserted_total} players and {comp_total} competition stats.")

c.execute("SELECT count(*) FROM players")
p_count = c.fetchone()[0]
c.execute("SELECT count(*) FROM player_competition_stats")
c_count = c.fetchone()[0]
print(f"FINAL DATABASE TOTALS: {p_count} players | {c_count} competition breakdowns.")

conn.close()
