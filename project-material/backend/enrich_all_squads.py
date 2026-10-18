import sqlite3
import random

# Connect to database
conn = sqlite3.connect("sql_app.db")
c = conn.cursor()

# 1. Unify Barcelona naming
c.execute("UPDATE players SET team = 'FC Barcelona' WHERE team = 'Barcelona'")
conn.commit()
print("Unified 'Barcelona' -> 'FC Barcelona'.")

# Find current max IDs
c.execute("SELECT max(id) FROM players")
curr_p_id = c.fetchone()[0] or 3068

c.execute("SELECT max(id) FROM player_competition_stats")
curr_c_id = c.fetchone()[0] or 6102

# Check existing player names to prevent duplicates
c.execute("SELECT lower(name) FROM players")
existing_names = set(row[0] for row in c.fetchall())

# Comprehensive roster additions for underpopulated & promoted clubs across Top 5 Leagues
# Data format: (name, nation, age, position, league, team, mins, goals, assists, shots, sot, chances, tackles, interc, clearances, blocks, yellow, red, contract_year, release_clause, wage_weekly, [competitions])
# Competitions format: (comp_name, comp_type, apps, mins, goals, assists, shots, sot, chances, tackles, interc, clearances, blocks, stage)

NEW_PLAYERS = [
    # ==========================================
    # PREMIER LEAGUE: FULHAM
    # ==========================================
    ("Bernd Leno", "Germany", 34, "GK", "Premier League", "Fulham", 3060, 0, 0, 0, 0, 1, 3, 2, 85, 1, 2, 0, 2027, None, 130000, [
        ("Premier League", "league", 34, 3060, 0, 0, 0, 0, 1, 3, 2, 85, 1, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 0, 0, 0, 0, 0, 5, 0, "Quarter-Finalist"),
        ("Carabao Cup", "domestic_cup", 4, 360, 0, 0, 0, 0, 0, 1, 1, 12, 0, "Semi-Finalist")
    ]),
    ("Antonee Robinson", "United States", 29, "DEF", "Premier League", "Fulham", 2880, 0, 6, 18, 5, 42, 88, 72, 65, 14, 6, 0, 2028, None, 85000, [
        ("Premier League", "league", 32, 2880, 0, 6, 18, 5, 42, 88, 72, 65, 14, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 1, 0, 3, 5, 4, 4, 1, "Quarter-Finalist"),
        ("Copa América 2024", "international", 3, 270, 0, 1, 2, 1, 4, 9, 7, 6, 2, "Group Stage")
    ]),
    ("Calvin Bassey", "Nigeria", 26, "DEF", "Premier League", "Fulham", 2520, 1, 1, 12, 4, 8, 74, 48, 112, 22, 5, 1, 2028, None, 75000, [
        ("Premier League", "league", 28, 2520, 1, 1, 12, 4, 8, 74, 48, 112, 22, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 1, 0, 0, 6, 3, 9, 2, "Quarter-Finalist"),
        ("AFCON 2024", "international", 7, 630, 0, 1, 3, 1, 2, 18, 12, 28, 6, "Finalist")
    ]),
    ("Joachim Andersen", "Denmark", 30, "DEF", "Premier League", "Fulham", 2970, 2, 2, 22, 7, 14, 65, 52, 148, 28, 7, 0, 2029, None, 100000, [
        ("Premier League", "league", 33, 2970, 2, 2, 22, 7, 14, 65, 52, 148, 28, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 2, 1, 1, 4, 3, 10, 2, "Quarter-Finalist"),
        ("UEFA Euro 2024", "international", 4, 360, 1, 0, 3, 1, 1, 8, 7, 22, 5, "Round of 16")
    ]),
    ("Timothy Castagne", "Belgium", 30, "DEF", "Premier League", "Fulham", 2250, 1, 3, 14, 4, 28, 62, 38, 54, 12, 4, 0, 2027, None, 70000, [
        ("Premier League", "league", 25, 2250, 1, 3, 14, 4, 28, 62, 38, 54, 12, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 3, 270, 0, 1, 2, 1, 4, 7, 5, 8, 1, "Semi-Finalist"),
        ("UEFA Euro 2024", "international", 4, 360, 0, 0, 2, 0, 3, 9, 6, 9, 2, "Round of 16")
    ]),
    ("Andreas Pereira", "Brazil", 30, "MID", "Premier League", "Fulham", 2700, 3, 8, 56, 18, 76, 52, 24, 22, 8, 8, 0, 2026, None, 80000, [
        ("Premier League", "league", 30, 2700, 3, 8, 56, 18, 76, 52, 24, 22, 8, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 1, 1, 4, 2, 6, 3, 1, 2, 0, "Quarter-Finalist"),
        ("Copa América 2024", "international", 4, 180, 1, 0, 4, 2, 5, 4, 2, 1, 0, "Quarter-Finalist")
    ]),
    ("Saša Lukić", "Serbia", 30, "MID", "Premier League", "Fulham", 2340, 2, 2, 32, 9, 34, 72, 42, 35, 16, 6, 0, 2027, None, 65000, [
        ("Premier League", "league", 26, 2340, 2, 2, 32, 9, 34, 72, 42, 35, 16, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 2, 1, 2, 5, 3, 3, 1, "Quarter-Finalist"),
        ("UEFA Euro 2024", "international", 3, 270, 0, 0, 3, 1, 2, 8, 5, 4, 2, "Group Stage")
    ]),
    ("Emile Smith Rowe", "England", 26, "MID", "Premier League", "Fulham", 2430, 8, 6, 58, 24, 62, 38, 18, 14, 6, 2, 0, 2029, None, 95000, [
        ("Premier League", "league", 27, 2430, 8, 6, 58, 24, 62, 38, 18, 14, 6, "Regular Season"),
        ("FA Cup", "domestic_cup", 3, 240, 2, 1, 6, 3, 7, 4, 2, 1, 0, "Quarter-Finalist"),
        ("Carabao Cup", "domestic_cup", 3, 210, 1, 1, 5, 2, 5, 3, 1, 2, 1, "Semi-Finalist")
    ]),
    ("Alex Iwobi", "Nigeria", 30, "MID", "Premier League", "Fulham", 2790, 7, 5, 62, 22, 68, 56, 31, 28, 9, 3, 0, 2028, None, 90000, [
        ("Premier League", "league", 31, 2790, 7, 5, 62, 22, 68, 56, 31, 28, 9, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 1, 0, 3, 1, 4, 3, 2, 2, 0, "Quarter-Finalist"),
        ("AFCON 2024", "international", 7, 610, 0, 2, 8, 3, 14, 12, 7, 5, 1, "Finalist")
    ]),
    ("Adama Traoré", "Spain", 30, "FWD", "Premier League", "Fulham", 1620, 4, 5, 38, 14, 45, 24, 11, 8, 3, 4, 0, 2026, None, 75000, [
        ("Premier League", "league", 22, 1620, 4, 5, 38, 14, 45, 24, 11, 8, 3, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 3, 210, 1, 2, 6, 3, 6, 3, 1, 1, 0, "Semi-Finalist")
    ]),
    ("Rodrigo Muniz", "Brazil", 25, "FWD", "Premier League", "Fulham", 2250, 14, 3, 78, 34, 32, 28, 12, 18, 5, 4, 0, 2028, None, 60000, [
        ("Premier League", "league", 28, 2250, 14, 3, 78, 34, 32, 28, 12, 18, 5, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 2, 0, 6, 3, 2, 2, 1, 1, 0, "Quarter-Finalist"),
        ("Carabao Cup", "domestic_cup", 3, 240, 2, 1, 8, 4, 4, 3, 1, 2, 0, "Semi-Finalist")
    ]),
    ("Raúl Jiménez", "Mexico", 35, "FWD", "Premier League", "Fulham", 1800, 9, 3, 52, 20, 26, 22, 10, 24, 6, 4, 1, 2026, None, 100000, [
        ("Premier League", "league", 23, 1800, 9, 3, 52, 20, 26, 22, 10, 24, 6, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 160, 1, 1, 4, 2, 3, 2, 1, 3, 0, "Quarter-Finalist"),
        ("Copa América 2024", "international", 3, 190, 0, 0, 5, 2, 2, 2, 1, 2, 1, "Group Stage")
    ]),
    ("Harry Wilson", "Wales", 29, "MID", "Premier League", "Fulham", 1980, 6, 6, 48, 19, 54, 41, 19, 14, 4, 3, 0, 2027, None, 65000, [
        ("Premier League", "league", 24, 1980, 6, 6, 48, 19, 54, 41, 19, 14, 4, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 4, 310, 2, 2, 9, 4, 8, 4, 2, 2, 1, "Semi-Finalist")
    ]),
    ("Sander Berge", "Norway", 28, "MID", "Premier League", "Fulham", 2610, 2, 3, 34, 10, 38, 82, 44, 48, 18, 5, 0, 2029, None, 75000, [
        ("Premier League", "league", 29, 2610, 2, 3, 34, 10, 38, 82, 44, 48, 18, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 2, 1, 2, 6, 3, 4, 1, "Quarter-Finalist")
    ]),
    ("Kenny Tete", "Netherlands", 30, "DEF", "Premier League", "Fulham", 2070, 1, 2, 12, 3, 24, 68, 36, 46, 11, 4, 0, 2027, None, 60000, [
        ("Premier League", "league", 23, 2070, 1, 2, 12, 3, 24, 68, 36, 46, 11, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 3, 240, 0, 1, 1, 0, 3, 8, 4, 5, 1, "Semi-Finalist")
    ]),

    # ==========================================
    # PREMIER LEAGUE: BOURNEMOUTH
    # ==========================================
    ("Kepa Arrizabalaga", "Spain", 31, "GK", "Premier League", "Bournemouth", 2700, 0, 0, 0, 0, 1, 2, 1, 68, 1, 1, 0, 2027, None, 120000, [
        ("Premier League", "league", 30, 2700, 0, 0, 0, 0, 1, 2, 1, 68, 1, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 0, 0, 0, 0, 0, 4, 0, "Fifth Round")
    ]),
    ("Milos Kerkez", "Hungary", 22, "DEF", "Premier League", "Bournemouth", 2610, 1, 4, 22, 7, 36, 76, 48, 52, 16, 7, 1, 2028, None, 55000, [
        ("Premier League", "league", 29, 2610, 1, 4, 22, 7, 36, 76, 48, 52, 16, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 1, 0, 2, 5, 3, 4, 1, "Fifth Round"),
        ("UEFA Euro 2024", "international", 3, 270, 0, 0, 3, 1, 3, 7, 5, 6, 2, "Group Stage")
    ]),
    ("Illia Zabarnyi", "Ukraine", 24, "DEF", "Premier League", "Bournemouth", 3060, 1, 0, 16, 5, 6, 68, 54, 142, 32, 4, 0, 2029, None, 65000, [
        ("Premier League", "league", 34, 3060, 1, 0, 16, 5, 6, 68, 54, 142, 32, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 1, 0, 0, 4, 3, 8, 2, "Fifth Round"),
        ("UEFA Euro 2024", "international", 3, 270, 0, 0, 2, 0, 1, 6, 5, 14, 3, "Group Stage")
    ]),
    ("Marcos Senesi", "Argentina", 29, "DEF", "Premier League", "Bournemouth", 2430, 3, 3, 24, 9, 12, 78, 52, 118, 26, 8, 0, 2027, None, 75000, [
        ("Premier League", "league", 27, 2430, 3, 3, 24, 9, 12, 78, 52, 118, 26, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 1, 2, 1, 1, 5, 4, 8, 2, "Fifth Round")
    ]),
    ("Lewis Cook", "England", 29, "MID", "Premier League", "Bournemouth", 2880, 2, 4, 28, 8, 48, 92, 58, 42, 18, 6, 1, 2028, None, 70000, [
        ("Premier League", "league", 32, 2880, 2, 4, 28, 8, 48, 92, 58, 42, 18, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 1, 0, 3, 7, 4, 3, 1, "Fifth Round")
    ]),
    ("Ryan Christie", "Scotland", 31, "MID", "Premier League", "Bournemouth", 2790, 3, 5, 52, 16, 56, 84, 46, 34, 14, 7, 0, 2027, None, 65000, [
        ("Premier League", "league", 31, 2790, 3, 5, 52, 16, 56, 84, 46, 34, 14, "Regular Season"),
        ("UEFA Euro 2024", "international", 3, 210, 0, 0, 3, 1, 4, 6, 3, 2, 1, "Group Stage")
    ]),
    ("Marcus Tavernier", "England", 27, "MID", "Premier League", "Bournemouth", 2340, 6, 6, 64, 24, 58, 48, 24, 18, 8, 4, 0, 2028, None, 65000, [
        ("Premier League", "league", 26, 2340, 6, 6, 64, 24, 58, 48, 24, 18, 8, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 160, 1, 1, 4, 2, 4, 3, 2, 1, 0, "Fifth Round")
    ]),
    ("Antoine Semenyo", "Ghana", 26, "FWD", "Premier League", "Bournemouth", 2700, 12, 5, 84, 32, 44, 52, 26, 16, 6, 5, 0, 2029, None, 70000, [
        ("Premier League", "league", 30, 2700, 12, 5, 84, 32, 44, 52, 26, 16, 6, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 1, 0, 5, 2, 2, 3, 1, 1, 0, "Fifth Round"),
        ("AFCON 2024", "international", 3, 240, 0, 1, 6, 2, 3, 4, 2, 2, 0, "Group Stage")
    ]),
    ("Justin Kluivert", "Netherlands", 27, "FWD", "Premier League", "Bournemouth", 2430, 10, 4, 68, 26, 46, 36, 18, 14, 5, 6, 0, 2028, None, 75000, [
        ("Premier League", "league", 27, 2430, 10, 4, 68, 26, 46, 36, 18, 14, 5, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 170, 2, 0, 5, 3, 3, 2, 1, 1, 0, "Fifth Round")
    ]),
    ("Evanilson", "Brazil", 26, "FWD", "Premier League", "Bournemouth", 2520, 15, 4, 82, 36, 38, 28, 12, 16, 4, 4, 0, 2029, None, 85000, [
        ("Premier League", "league", 28, 2520, 15, 4, 82, 36, 38, 28, 12, 16, 4, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 2, 1, 6, 3, 3, 2, 1, 1, 0, "Fifth Round"),
        ("Copa América 2024", "international", 2, 90, 0, 0, 2, 1, 1, 1, 0, 0, 0, "Quarter-Finalist")
    ]),
    ("Dean Huijsen", "Spain", 21, "DEF", "Premier League", "Bournemouth", 1890, 2, 1, 14, 5, 8, 54, 42, 88, 18, 3, 0, 2030, None, 45000, [
        ("Premier League", "league", 21, 1890, 2, 1, 14, 5, 8, 54, 42, 88, 18, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 2, 180, 0, 0, 1, 0, 1, 4, 3, 7, 1, "Third Round")
    ]),
    ("Tyler Adams", "United States", 27, "MID", "Premier League", "Bournemouth", 1710, 1, 1, 14, 4, 22, 68, 44, 28, 12, 5, 0, 2028, None, 80000, [
        ("Premier League", "league", 19, 1710, 1, 1, 14, 4, 22, 68, 44, 28, 12, "Regular Season"),
        ("Copa América 2024", "international", 3, 270, 0, 0, 2, 0, 2, 11, 7, 4, 1, "Group Stage")
    ]),
    ("Alex Scott", "England", 23, "MID", "Premier League", "Bournemouth", 2160, 3, 4, 36, 12, 44, 58, 32, 22, 8, 4, 0, 2029, None, 50000, [
        ("Premier League", "league", 24, 2160, 3, 4, 36, 12, 44, 58, 32, 22, 8, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 160, 1, 0, 3, 1, 3, 4, 2, 2, 0, "Fifth Round")
    ]),

    # ==========================================
    # PREMIER LEAGUE: NOTTINGHAM FOREST
    # ==========================================
    ("Matz Sels", "Belgium", 34, "GK", "Premier League", "Nottingham Forest", 3060, 0, 0, 0, 0, 0, 2, 1, 74, 1, 2, 0, 2027, None, 65000, [
        ("Premier League", "league", 34, 3060, 0, 0, 0, 0, 0, 2, 1, 74, 1, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 0, 0, 0, 0, 0, 5, 0, "Fifth Round")
    ]),
    ("Ola Aina", "Nigeria", 29, "DEF", "Premier League", "Nottingham Forest", 2520, 2, 3, 18, 6, 28, 66, 42, 58, 14, 4, 0, 2027, None, 60000, [
        ("Premier League", "league", 28, 2520, 2, 3, 18, 6, 28, 66, 42, 58, 14, "Regular Season"),
        ("AFCON 2024", "international", 7, 630, 0, 1, 3, 1, 5, 16, 11, 14, 3, "Finalist")
    ]),
    ("Murillo", "Brazil", 24, "DEF", "Premier League", "Nottingham Forest", 3060, 1, 2, 22, 7, 12, 72, 64, 164, 38, 6, 0, 2029, None, 75000, [
        ("Premier League", "league", 34, 3060, 1, 2, 22, 7, 12, 72, 64, 164, 38, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 1, 0, 1, 4, 3, 11, 2, "Fifth Round")
    ]),
    ("Nikola Milenković", "Serbia", 28, "DEF", "Premier League", "Nottingham Forest", 2970, 2, 1, 24, 8, 8, 68, 52, 152, 34, 5, 0, 2029, None, 85000, [
        ("Premier League", "league", 33, 2970, 2, 1, 24, 8, 8, 68, 52, 152, 34, "Regular Season"),
        ("UEFA Euro 2024", "international", 3, 270, 0, 0, 2, 0, 1, 7, 6, 16, 4, "Group Stage")
    ]),
    ("Álex Moreno", "Spain", 33, "DEF", "Premier League", "Nottingham Forest", 2160, 1, 4, 20, 6, 32, 58, 34, 42, 11, 4, 0, 2026, None, 70000, [
        ("Premier League", "league", 24, 2160, 1, 4, 20, 6, 32, 58, 34, 42, 11, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 2, 180, 0, 1, 1, 0, 3, 4, 2, 3, 1, "Second Round")
    ]),
    ("Ryan Yates", "England", 28, "MID", "Premier League", "Nottingham Forest", 2700, 3, 2, 38, 11, 24, 88, 54, 46, 22, 9, 0, 2028, None, 55000, [
        ("Premier League", "league", 30, 2700, 3, 2, 38, 11, 24, 88, 54, 46, 22, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 0, 0, 2, 0, 1, 6, 3, 4, 1, "Fifth Round")
    ]),
    ("Elliot Anderson", "Scotland", 23, "MID", "Premier League", "Nottingham Forest", 2430, 4, 5, 46, 16, 52, 74, 38, 32, 14, 5, 0, 2029, None, 60000, [
        ("Premier League", "league", 27, 2430, 4, 5, 46, 16, 52, 74, 38, 32, 14, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 2, 180, 1, 1, 4, 2, 4, 5, 2, 2, 1, "Second Round")
    ]),
    ("Morgan Gibbs-White", "England", 26, "MID", "Premier League", "Nottingham Forest", 2970, 9, 11, 74, 28, 86, 62, 28, 18, 7, 7, 1, 2028, None, 100000, [
        ("Premier League", "league", 33, 2970, 9, 11, 74, 28, 86, 62, 28, 18, 7, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 1, 1, 5, 2, 6, 3, 1, 1, 0, "Fifth Round")
    ]),
    ("Anthony Elanga", "Sweden", 24, "FWD", "Premier League", "Nottingham Forest", 2700, 8, 9, 62, 24, 54, 42, 18, 12, 4, 3, 0, 2028, None, 65000, [
        ("Premier League", "league", 30, 2700, 8, 9, 62, 24, 54, 42, 18, 12, 4, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 170, 1, 1, 4, 2, 4, 2, 1, 1, 0, "Fifth Round")
    ]),
    ("Callum Hudson-Odoi", "England", 25, "FWD", "Premier League", "Nottingham Forest", 2520, 10, 5, 58, 22, 48, 34, 16, 10, 4, 2, 0, 2027, None, 80000, [
        ("Premier League", "league", 28, 2520, 10, 5, 58, 22, 48, 34, 16, 10, 4, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 180, 1, 0, 4, 2, 3, 2, 1, 1, 0, "Fifth Round")
    ]),
    ("Chris Wood", "New Zealand", 34, "FWD", "Premier League", "Nottingham Forest", 2340, 16, 2, 68, 32, 24, 24, 10, 36, 8, 2, 0, 2026, None, 80000, [
        ("Premier League", "league", 26, 2340, 16, 2, 68, 32, 24, 24, 10, 36, 8, "Regular Season"),
        ("FA Cup", "domestic_cup", 2, 150, 1, 0, 4, 2, 1, 1, 0, 3, 0, "Fifth Round")
    ]),
    ("Taiwo Awoniyi", "Nigeria", 29, "FWD", "Premier League", "Nottingham Forest", 1620, 8, 3, 46, 19, 22, 18, 8, 14, 3, 3, 0, 2027, None, 70000, [
        ("Premier League", "league", 18, 1620, 8, 3, 46, 19, 22, 18, 8, 14, 3, "Regular Season"),
        ("Carabao Cup", "domestic_cup", 2, 150, 1, 1, 4, 2, 2, 1, 0, 1, 0, "Second Round")
    ]),

    # ==========================================
    # LA LIGA: GIRONA (UEFA Champions League Club)
    # ==========================================
    ("Paulo Gazzaniga", "Argentina", 34, "GK", "La Liga", "Girona", 3150, 0, 0, 0, 0, 1, 2, 1, 72, 1, 2, 0, 2027, 25000000, 50000, [
        ("La Liga", "league", 35, 3150, 0, 0, 0, 0, 1, 2, 1, 72, 1, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 6, 540, 0, 0, 0, 0, 0, 1, 0, 14, 0, "League Phase"),
        ("Copa del Rey", "domestic_cup", 3, 270, 0, 0, 0, 0, 0, 0, 0, 6, 0, "Quarter-Finalist")
    ]),
    ("Miguel Gutiérrez", "Spain", 25, "DEF", "La Liga", "Girona", 2970, 3, 8, 36, 14, 64, 78, 46, 44, 12, 6, 0, 2028, 40000000, 65000, [
        ("La Liga", "league", 33, 2970, 3, 8, 36, 14, 64, 78, 46, 44, 12, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 6, 540, 1, 1, 6, 3, 11, 14, 8, 8, 2, "League Phase"),
        ("Copa del Rey", "domestic_cup", 3, 270, 0, 1, 3, 1, 5, 6, 3, 4, 1, "Quarter-Finalist")
    ]),
    ("Daley Blind", "Netherlands", 36, "DEF", "La Liga", "Girona", 2880, 2, 3, 18, 6, 32, 62, 54, 108, 22, 3, 0, 2026, 15000000, 60000, [
        ("La Liga", "league", 32, 2880, 2, 3, 18, 6, 32, 62, 54, 108, 22, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 5, 450, 0, 1, 2, 1, 4, 9, 8, 18, 4, "League Phase"),
        ("UEFA Euro 2024", "international", 1, 45, 0, 0, 0, 0, 1, 1, 1, 2, 0, "Semi-Finalist")
    ]),
    ("David López", "Spain", 36, "DEF", "La Liga", "Girona", 2430, 3, 1, 20, 8, 14, 58, 48, 112, 28, 7, 1, 2026, 20000000, 55000, [
        ("La Liga", "league", 27, 2430, 3, 1, 20, 8, 14, 58, 48, 112, 28, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 5, 450, 1, 0, 4, 2, 2, 8, 7, 20, 5, "League Phase")
    ]),
    ("Arnau Martínez", "Spain", 23, "DEF", "La Liga", "Girona", 2340, 2, 4, 22, 7, 38, 68, 38, 48, 14, 5, 0, 2028, 30000000, 45000, [
        ("La Liga", "league", 26, 2340, 2, 4, 22, 7, 38, 68, 38, 48, 14, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 6, 510, 0, 1, 3, 1, 6, 12, 7, 9, 2, "League Phase")
    ]),
    ("Yangel Herrera", "Venezuela", 28, "MID", "La Liga", "Girona", 2610, 6, 3, 44, 16, 36, 82, 46, 38, 18, 9, 0, 2027, 35000000, 60000, [
        ("La Liga", "league", 29, 2610, 6, 3, 44, 16, 36, 82, 46, 38, 18, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 5, 420, 1, 0, 5, 2, 5, 11, 6, 6, 2, "League Phase"),
        ("Copa América 2024", "international", 4, 360, 0, 1, 4, 1, 4, 12, 7, 6, 3, "Quarter-Finalist")
    ]),
    ("Iván Martín", "Spain", 27, "MID", "La Liga", "Girona", 2880, 5, 5, 46, 18, 58, 74, 42, 32, 12, 5, 0, 2028, 30000000, 50000, [
        ("La Liga", "league", 32, 2880, 5, 5, 46, 18, 58, 74, 42, 32, 12, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 6, 530, 1, 1, 7, 3, 9, 13, 8, 5, 2, "League Phase")
    ]),
    ("Viktor Tsygankov", "Ukraine", 28, "FWD", "La Liga", "Girona", 2520, 9, 8, 58, 24, 62, 36, 18, 12, 4, 2, 0, 2027, 45000000, 75000, [
        ("La Liga", "league", 28, 2520, 9, 8, 58, 24, 62, 36, 18, 12, 4, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 6, 520, 2, 2, 12, 5, 11, 6, 3, 2, 1, "League Phase"),
        ("UEFA Euro 2024", "international", 3, 240, 0, 1, 5, 2, 5, 4, 2, 1, 0, "Group Stage")
    ]),
    ("Bryan Gil", "Spain", 25, "FWD", "La Liga", "Girona", 2250, 5, 6, 48, 18, 54, 44, 22, 14, 5, 4, 0, 2028, 35000000, 60000, [
        ("La Liga", "league", 25, 2250, 5, 6, 48, 18, 54, 44, 22, 14, 5, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 6, 480, 1, 2, 8, 3, 9, 8, 4, 2, 1, "League Phase")
    ]),
    ("Yáser Asprilla", "Colombia", 22, "MID", "La Liga", "Girona", 1980, 5, 5, 44, 17, 48, 34, 18, 10, 4, 3, 0, 2030, 50000000, 45000, [
        ("La Liga", "league", 22, 1980, 5, 5, 44, 17, 48, 34, 18, 10, 4, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 5, 390, 1, 1, 7, 3, 7, 5, 3, 1, 0, "League Phase"),
        ("Copa América 2024", "international", 2, 80, 1, 0, 3, 1, 2, 2, 1, 0, 0, "Finalist")
    ]),
    ("Abel Ruiz", "Spain", 26, "FWD", "La Liga", "Girona", 2340, 11, 4, 68, 28, 32, 26, 12, 14, 4, 3, 0, 2029, 40000000, 55000, [
        ("La Liga", "league", 26, 2340, 11, 4, 68, 28, 32, 26, 12, 14, 4, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 6, 470, 2, 1, 11, 5, 5, 4, 2, 2, 0, "League Phase")
    ]),
    ("Cristhian Stuani", "Uruguay", 39, "FWD", "La Liga", "Girona", 1260, 9, 2, 42, 20, 16, 14, 6, 22, 5, 4, 0, 2026, 10000000, 45000, [
        ("La Liga", "league", 14, 1260, 9, 2, 42, 20, 16, 14, 6, 22, 5, "Club Legend & Super-Sub"),
        ("UEFA Champions League", "continental", 4, 180, 2, 0, 6, 3, 2, 2, 1, 3, 0, "League Phase")
    ]),
    ("Donny van de Beek", "Netherlands", 29, "MID", "La Liga", "Girona", 1800, 4, 3, 34, 12, 38, 48, 26, 16, 7, 3, 0, 2028, 25000000, 65000, [
        ("La Liga", "league", 20, 1800, 4, 3, 34, 12, 38, 48, 26, 16, 7, "3rd Place (UCL Qualification)"),
        ("UEFA Champions League", "continental", 5, 380, 1, 1, 5, 2, 6, 8, 4, 3, 1, "League Phase")
    ]),

    # ==========================================
    # BUNDESLIGA: WERDER BREMEN
    # ==========================================
    ("Michael Zetterer", "Germany", 31, "GK", "Bundesliga", "Werder Bremen", 2700, 0, 0, 0, 0, 1, 2, 1, 64, 1, 1, 0, 2027, None, 35000, [
        ("Bundesliga", "league", 30, 2700, 0, 0, 0, 0, 1, 2, 1, 64, 1, "Regular Season"),
        ("DFB-Pokal", "domestic_cup", 2, 180, 0, 0, 0, 0, 0, 0, 0, 5, 0, "Round of 16")
    ]),
    ("Marco Friedl", "Austria", 28, "DEF", "Bundesliga", "Werder Bremen", 2610, 2, 2, 18, 6, 14, 66, 52, 114, 24, 6, 1, 2027, None, 45000, [
        ("Bundesliga", "league", 29, 2610, 2, 2, 18, 6, 14, 66, 52, 114, 24, "Regular Season"),
        ("DFB-Pokal", "domestic_cup", 2, 180, 0, 0, 1, 0, 1, 4, 3, 8, 1, "Round of 16")
    ]),
    ("Miloš Veljković", "Serbia", 30, "DEF", "Bundesliga", "Werder Bremen", 2430, 1, 1, 14, 4, 8, 58, 44, 98, 20, 4, 0, 2026, None, 40000, [
        ("Bundesliga", "league", 27, 2430, 1, 1, 14, 4, 8, 58, 44, 98, 20, "Regular Season"),
        ("UEFA Euro 2024", "international", 3, 270, 0, 0, 2, 0, 1, 7, 5, 12, 3, "Group Stage")
    ]),
    ("Niklas Stark", "Germany", 31, "DEF", "Bundesliga", "Werder Bremen", 2250, 2, 0, 16, 5, 6, 52, 42, 88, 18, 5, 0, 2027, None, 42000, [
        ("Bundesliga", "league", 25, 2250, 2, 0, 16, 5, 6, 52, 42, 88, 18, "Regular Season")
    ]),
    ("Mitchell Weiser", "Germany", 32, "DEF", "Bundesliga", "Werder Bremen", 2790, 4, 8, 42, 14, 62, 78, 46, 52, 14, 8, 0, 2027, None, 50000, [
        ("Bundesliga", "league", 31, 2790, 4, 8, 42, 14, 62, 78, 46, 52, 14, "Regular Season"),
        ("DFB-Pokal", "domestic_cup", 2, 180, 1, 1, 3, 1, 4, 5, 3, 4, 1, "Round of 16")
    ]),
    ("Senne Lynen", "Belgium", 27, "MID", "Bundesliga", "Werder Bremen", 2700, 2, 3, 26, 8, 36, 86, 54, 44, 19, 7, 0, 2028, None, 40000, [
        ("Bundesliga", "league", 30, 2700, 2, 3, 26, 8, 36, 86, 54, 44, 19, "Regular Season")
    ]),
    ("Jens Stage", "Denmark", 29, "MID", "Bundesliga", "Werder Bremen", 2520, 8, 4, 54, 22, 42, 74, 38, 36, 16, 5, 1, 2027, None, 45000, [
        ("Bundesliga", "league", 28, 2520, 8, 4, 54, 22, 42, 74, 38, 36, 16, "Regular Season")
    ]),
    ("Romano Schmid", "Austria", 26, "MID", "Bundesliga", "Werder Bremen", 2790, 5, 7, 56, 20, 68, 62, 32, 24, 10, 4, 0, 2028, None, 45000, [
        ("Bundesliga", "league", 31, 2790, 5, 7, 56, 20, 68, 62, 32, 24, 10, "Regular Season"),
        ("UEFA Euro 2024", "international", 4, 290, 1, 1, 5, 2, 6, 8, 4, 2, 1, "Round of 16")
    ]),
    ("Marvin Ducksch", "Germany", 32, "FWD", "Bundesliga", "Werder Bremen", 2880, 14, 9, 86, 36, 72, 32, 14, 18, 6, 5, 0, 2027, None, 65000, [
        ("Bundesliga", "league", 32, 2880, 14, 9, 86, 36, 72, 32, 14, 18, 6, "Regular Season"),
        ("DFB-Pokal", "domestic_cup", 2, 180, 2, 1, 6, 3, 5, 2, 1, 1, 0, "Round of 16")
    ]),
    ("Justin Njinmah", "Germany", 25, "FWD", "Bundesliga", "Werder Bremen", 1980, 7, 4, 48, 20, 36, 28, 12, 10, 3, 3, 0, 2028, None, 35000, [
        ("Bundesliga", "league", 22, 1980, 7, 4, 48, 20, 36, 28, 12, 10, 3, "Regular Season")
    ]),
    ("Marco Grüll", "Austria", 28, "FWD", "Bundesliga", "Werder Bremen", 1890, 6, 5, 46, 18, 42, 34, 16, 12, 4, 3, 0, 2028, None, 40000, [
        ("Bundesliga", "league", 21, 1890, 6, 5, 46, 18, 42, 34, 16, 12, 4, "Regular Season")
    ]),

    # ==========================================
    # SERIE A: COMO
    # ==========================================
    ("Pepe Reina", "Spain", 43, "GK", "Serie A", "Como", 1440, 0, 0, 0, 0, 1, 1, 0, 32, 0, 1, 0, 2026, None, 30000, [
        ("Serie A", "league", 16, 1440, 0, 0, 0, 0, 1, 1, 0, 32, 0, "Regular Season")
    ]),
    ("Emil Audero", "Italy", 29, "GK", "Serie A", "Como", 1800, 0, 0, 0, 0, 0, 1, 1, 44, 1, 1, 0, 2028, None, 45000, [
        ("Serie A", "league", 20, 1800, 0, 0, 0, 0, 0, 1, 1, 44, 1, "Regular Season")
    ]),
    ("Alberto Moreno", "Spain", 34, "DEF", "Serie A", "Como", 2250, 1, 4, 22, 7, 38, 56, 34, 38, 10, 6, 1, 2026, None, 45000, [
        ("Serie A", "league", 25, 2250, 1, 4, 22, 7, 38, 56, 34, 38, 10, "Regular Season")
    ]),
    ("Alberto Dossena", "Italy", 27, "DEF", "Serie A", "Como", 2700, 2, 1, 18, 6, 8, 64, 52, 124, 26, 5, 0, 2028, None, 40000, [
        ("Serie A", "league", 30, 2700, 2, 1, 18, 6, 8, 64, 52, 124, 26, "Regular Season")
    ]),
    ("Sergi Roberto", "Spain", 34, "MID", "Serie A", "Como", 2340, 2, 4, 28, 9, 44, 68, 38, 32, 12, 4, 0, 2026, None, 55000, [
        ("Serie A", "league", 26, 2340, 2, 4, 28, 9, 44, 68, 38, 32, 12, "Regular Season")
    ]),
    ("Máximo Perrone", "Argentina", 23, "MID", "Serie A", "Como", 2430, 2, 3, 24, 7, 36, 78, 46, 34, 14, 5, 0, 2028, None, 45000, [
        ("Serie A", "league", 27, 2430, 2, 3, 24, 7, 36, 78, 46, 34, 14, "Regular Season")
    ]),
    ("Gabriel Strefezza", "Brazil", 29, "FWD", "Serie A", "Como", 2610, 7, 6, 62, 24, 54, 48, 22, 14, 5, 4, 0, 2027, None, 45000, [
        ("Serie A", "league", 29, 2610, 7, 6, 62, 24, 54, 48, 22, 14, 5, "Regular Season")
    ]),
    ("Nico Paz", "Argentina", 21, "MID", "Serie A", "Como", 2520, 8, 7, 68, 26, 64, 44, 24, 16, 6, 3, 0, 2029, 60000000, 40000, [
        ("Serie A", "league", 28, 2520, 8, 7, 68, 26, 64, 44, 24, 16, 6, "Regular Season"),
        ("Coppa Italia", "domestic_cup", 2, 180, 1, 1, 5, 2, 5, 3, 1, 1, 0, "Round of 16")
    ]),
    ("Alieu Fadera", "Gambia", 24, "FWD", "Serie A", "Como", 2160, 5, 4, 42, 16, 38, 38, 18, 12, 4, 3, 0, 2028, None, 35000, [
        ("Serie A", "league", 24, 2160, 5, 4, 42, 16, 38, 38, 18, 12, 4, "Regular Season")
    ]),
    ("Andrea Belotti", "Italy", 32, "FWD", "Serie A", "Como", 1980, 8, 3, 54, 22, 28, 26, 12, 18, 5, 4, 0, 2026, None, 65000, [
        ("Serie A", "league", 22, 1980, 8, 3, 54, 22, 28, 26, 12, 18, 5, "Regular Season")
    ]),
    ("Patrick Cutrone", "Italy", 28, "FWD", "Serie A", "Como", 2700, 12, 4, 76, 32, 34, 32, 14, 16, 5, 4, 0, 2028, None, 50000, [
        ("Serie A", "league", 30, 2700, 12, 4, 76, 32, 34, 32, 14, 16, 5, "Regular Season"),
        ("Coppa Italia", "domestic_cup", 2, 180, 2, 0, 6, 3, 2, 2, 1, 1, 0, "Round of 16")
    ]),

    # ==========================================
    # SERIE A: PARMA
    # ==========================================
    ("Zion Suzuki", "Japan", 24, "GK", "Serie A", "Parma", 2970, 0, 0, 0, 0, 1, 2, 1, 78, 1, 3, 1, 2029, None, 35000, [
        ("Serie A", "league", 33, 2970, 0, 0, 0, 0, 1, 2, 1, 78, 1, "Regular Season"),
        ("Asian Cup 2024", "international", 5, 450, 0, 0, 0, 0, 0, 1, 0, 8, 0, "Quarter-Finalist")
    ]),
    ("Emanuele Valeri", "Italy", 27, "DEF", "Serie A", "Parma", 2610, 2, 4, 26, 8, 42, 68, 38, 46, 12, 5, 0, 2027, None, 35000, [
        ("Serie A", "league", 29, 2610, 2, 4, 26, 8, 42, 68, 38, 46, 12, "Regular Season")
    ]),
    ("Alessandro Circati", "Australia", 22, "DEF", "Serie A", "Parma", 2430, 1, 1, 14, 4, 8, 64, 48, 108, 22, 4, 0, 2028, None, 30000, [
        ("Serie A", "league", 27, 2430, 1, 1, 14, 4, 8, 64, 48, 108, 22, "Regular Season")
    ]),
    ("Enrico Delprato", "Italy", 26, "DEF", "Serie A", "Parma", 2880, 3, 2, 22, 8, 18, 74, 52, 116, 26, 5, 0, 2028, None, 40000, [
        ("Serie A", "league", 32, 2880, 3, 2, 22, 8, 18, 74, 52, 116, 26, "Regular Season")
    ]),
    ("Adrián Bernabé", "Spain", 25, "MID", "Serie A", "Parma", 2790, 4, 6, 52, 18, 68, 72, 38, 26, 10, 6, 0, 2028, None, 45000, [
        ("Serie A", "league", 31, 2790, 4, 6, 52, 18, 68, 72, 38, 26, 10, "Regular Season"),
        ("Olympics 2024", "international", 6, 480, 1, 2, 8, 3, 12, 14, 7, 4, 1, "🏆 Gold Medalist")
    ]),
    ("Dennis Man", "Romania", 28, "FWD", "Serie A", "Parma", 2880, 11, 7, 78, 32, 66, 46, 22, 16, 6, 3, 0, 2027, None, 50000, [
        ("Serie A", "league", 32, 2880, 11, 7, 78, 32, 66, 46, 22, 16, 6, "Regular Season"),
        ("UEFA Euro 2024", "international", 4, 340, 0, 2, 6, 2, 8, 6, 3, 2, 1, "Round of 16")
    ]),
    ("Valentin Mihăilă", "Romania", 26, "FWD", "Serie A", "Parma", 2430, 6, 5, 58, 22, 48, 38, 18, 12, 4, 4, 0, 2027, None, 40000, [
        ("Serie A", "league", 27, 2430, 6, 5, 58, 22, 48, 38, 18, 12, 4, "Regular Season"),
        ("UEFA Euro 2024", "international", 3, 210, 0, 0, 4, 1, 4, 4, 2, 1, 0, "Round of 16")
    ]),
    ("Ange-Yoan Bonny", "France", 22, "FWD", "Serie A", "Parma", 2520, 9, 5, 64, 26, 42, 34, 14, 14, 5, 4, 0, 2028, None, 35000, [
        ("Serie A", "league", 28, 2520, 9, 5, 64, 26, 42, 34, 14, 14, 5, "Regular Season")
    ]),
    ("Matteo Cancellieri", "Italy", 24, "FWD", "Serie A", "Parma", 2070, 5, 3, 44, 16, 32, 32, 14, 10, 3, 3, 0, 2028, None, 40000, [
        ("Serie A", "league", 23, 2070, 5, 3, 44, 16, 32, 32, 14, 10, 3, "Regular Season")
    ]),
    ("Simon Sohm", "Switzerland", 25, "MID", "Serie A", "Parma", 2610, 3, 3, 36, 12, 38, 76, 44, 38, 16, 5, 0, 2027, None, 35000, [
        ("Serie A", "league", 29, 2610, 3, 3, 36, 12, 38, 76, 44, 38, 16, "Regular Season")
    ]),

    # ==========================================
    # SERIE A: LECCE
    # ==========================================
    ("Wladimiro Falcone", "Italy", 31, "GK", "Serie A", "Lecce", 3150, 0, 0, 0, 0, 1, 3, 1, 88, 1, 2, 0, 2028, None, 35000, [
        ("Serie A", "league", 35, 3150, 0, 0, 0, 0, 1, 3, 1, 88, 1, "Regular Season")
    ]),
    ("Antonino Gallo", "Italy", 26, "DEF", "Serie A", "Lecce", 2700, 1, 4, 22, 6, 36, 78, 44, 48, 14, 6, 1, 2027, None, 30000, [
        ("Serie A", "league", 30, 2700, 1, 4, 22, 6, 36, 78, 44, 48, 14, "Regular Season")
    ]),
    ("Federico Baschirotto", "Italy", 29, "DEF", "Serie A", "Lecce", 3060, 2, 1, 24, 7, 10, 74, 56, 162, 34, 7, 0, 2027, None, 35000, [
        ("Serie A", "league", 34, 3060, 2, 1, 24, 7, 10, 74, 56, 162, 34, "Regular Season")
    ]),
    ("Kialonda Gaspar", "Angola", 28, "DEF", "Serie A", "Lecce", 2790, 1, 0, 16, 5, 6, 68, 52, 148, 28, 5, 0, 2028, None, 30000, [
        ("Serie A", "league", 31, 2790, 1, 0, 16, 5, 6, 68, 52, 148, 28, "Regular Season"),
        ("AFCON 2024", "international", 5, 450, 0, 0, 2, 0, 1, 11, 8, 22, 5, "Quarter-Finalist")
    ]),
    ("Patrick Dorgu", "Denmark", 21, "DEF", "Serie A", "Lecce", 2610, 4, 2, 38, 14, 34, 72, 42, 44, 16, 5, 1, 2029, 35000000, 30000, [
        ("Serie A", "league", 29, 2610, 4, 2, 38, 14, 34, 72, 42, 44, 16, "Regular Season"),
        ("UEFA Nations League", "international", 4, 280, 1, 0, 4, 2, 3, 7, 4, 4, 1, "League Phase")
    ]),
    ("Ylber Ramadani", "Albania", 30, "MID", "Serie A", "Lecce", 2880, 1, 2, 28, 7, 28, 94, 58, 42, 18, 8, 0, 2027, None, 35000, [
        ("Serie A", "league", 32, 2880, 1, 2, 28, 7, 28, 94, 58, 42, 18, "Regular Season"),
        ("UEFA Euro 2024", "international", 3, 270, 0, 0, 2, 0, 2, 8, 6, 4, 2, "Group Stage")
    ]),
    ("Nikola Krstović", "Montenegro", 26, "FWD", "Serie A", "Lecce", 2880, 12, 3, 92, 34, 32, 32, 12, 18, 5, 6, 1, 2028, None, 40000, [
        ("Serie A", "league", 32, 2880, 12, 3, 92, 34, 32, 32, 12, 18, 5, "Regular Season")
    ]),
    ("Ante Rebić", "Croatia", 32, "FWD", "Serie A", "Lecce", 1620, 4, 3, 36, 14, 26, 24, 10, 12, 4, 4, 0, 2026, None, 50000, [
        ("Serie A", "league", 18, 1620, 4, 3, 36, 14, 26, 24, 10, 12, 4, "Regular Season")
    ]),

    # ==========================================
    # LIGUE 1: AJ AUXERRE
    # ==========================================
    ("Donovan Léon", "France", 33, "GK", "Ligue 1", "AJ Auxerre", 2700, 0, 0, 0, 0, 1, 2, 1, 62, 1, 1, 0, 2026, None, 25000, [
        ("Ligue 1", "league", 30, 2700, 0, 0, 0, 0, 1, 2, 1, 62, 1, "Regular Season")
    ]),
    ("Gideon Mensah", "Ghana", 28, "DEF", "Ligue 1", "AJ Auxerre", 2520, 1, 3, 18, 5, 34, 68, 42, 46, 12, 4, 0, 2027, None, 30000, [
        ("Ligue 1", "league", 28, 2520, 1, 3, 18, 5, 34, 68, 42, 46, 12, "Regular Season"),
        ("AFCON 2024", "international", 3, 270, 0, 0, 2, 0, 2, 7, 5, 6, 2, "Group Stage")
    ]),
    ("Jubal", "Brazil", 33, "DEF", "Ligue 1", "AJ Auxerre", 2880, 4, 1, 26, 10, 8, 68, 54, 138, 30, 6, 0, 2026, None, 35000, [
        ("Ligue 1", "league", 32, 2880, 4, 1, 26, 10, 8, 68, 54, 138, 30, "Regular Season")
    ]),
    ("Sinaly Diomandé", "Ivory Coast", 25, "DEF", "Ligue 1", "AJ Auxerre", 2430, 2, 0, 16, 5, 6, 62, 46, 118, 24, 5, 1, 2027, None, 35000, [
        ("Ligue 1", "league", 27, 2430, 2, 0, 16, 5, 6, 62, 46, 118, 24, "Regular Season")
    ]),
    ("Elisha Owusu", "Ghana", 28, "MID", "Ligue 1", "AJ Auxerre", 2790, 2, 3, 28, 8, 32, 84, 52, 42, 16, 7, 0, 2027, None, 32000, [
        ("Ligue 1", "league", 31, 2790, 2, 3, 28, 8, 32, 84, 52, 42, 16, "Regular Season")
    ]),
    ("Gaëtan Perrin", "France", 30, "MID", "Ligue 1", "AJ Auxerre", 2700, 8, 7, 64, 26, 62, 44, 22, 16, 6, 3, 0, 2027, None, 35000, [
        ("Ligue 1", "league", 30, 2700, 8, 7, 64, 26, 62, 44, 22, 16, 6, "Regular Season")
    ]),
    ("Hamed Junior Traorè", "Ivory Coast", 26, "MID", "Ligue 1", "AJ Auxerre", 2340, 7, 5, 58, 24, 52, 42, 20, 14, 5, 4, 0, 2028, None, 45000, [
        ("Ligue 1", "league", 26, 2340, 7, 5, 58, 24, 52, 42, 20, 14, 5, "Regular Season")
    ]),
    ("Lassine Sinayoko", "Mali", 26, "FWD", "Ligue 1", "AJ Auxerre", 2520, 8, 6, 62, 24, 46, 44, 22, 18, 6, 5, 0, 2027, None, 30000, [
        ("Ligue 1", "league", 28, 2520, 8, 6, 62, 24, 46, 44, 22, 18, 6, "Regular Season"),
        ("AFCON 2024", "international", 5, 410, 3, 1, 10, 5, 5, 6, 3, 2, 1, "Quarter-Finalist")
    ]),
    ("Ado Onaiwu", "Japan", 30, "FWD", "Ligue 1", "AJ Auxerre", 2160, 9, 3, 56, 22, 28, 26, 12, 14, 4, 3, 0, 2026, None, 35000, [
        ("Ligue 1", "league", 24, 2160, 9, 3, 56, 22, 28, 26, 12, 14, 4, "Regular Season")
    ]),

    # ==========================================
    # MARQUEE STARS MISSING ACROSS TOP 5 CLUBS
    # ==========================================
    ("Cole Palmer", "England", 24, "MID", "Premier League", "Chelsea", 3060, 22, 13, 108, 48, 88, 42, 22, 14, 5, 5, 0, 2033, None, 180000, [
        ("Premier League", "league", 34, 3060, 22, 13, 108, 48, 88, 42, 22, 14, 5, "Young Player of Season"),
        ("FA Cup", "domestic_cup", 5, 450, 2, 2, 16, 7, 14, 6, 3, 2, 1, "Semi-Finalist"),
        ("Carabao Cup", "domestic_cup", 6, 540, 2, 2, 18, 8, 16, 7, 4, 3, 1, "Finalist"),
        ("UEFA Euro 2024", "international", 5, 145, 1, 1, 6, 3, 5, 2, 1, 0, 0, "🏆 Final Goalscorer & Runner-Up")
    ]),
    ("Nicolas Jackson", "Senegal", 25, "FWD", "Premier League", "Chelsea", 2700, 16, 6, 84, 38, 44, 34, 16, 18, 6, 10, 0, 2033, None, 120000, [
        ("Premier League", "league", 30, 2700, 16, 6, 84, 38, 44, 34, 16, 18, 6, "Regular Season"),
        ("FA Cup", "domestic_cup", 5, 430, 2, 1, 14, 6, 6, 5, 2, 3, 1, "Semi-Finalist"),
        ("AFCON 2024", "international", 4, 210, 0, 0, 5, 2, 3, 3, 1, 1, 0, "Round of 16")
    ]),
    ("Riccardo Calafiori", "Italy", 24, "DEF", "Premier League", "Arsenal", 2430, 2, 3, 22, 8, 34, 74, 56, 92, 22, 5, 0, 2029, None, 120000, [
        ("Premier League", "league", 27, 2430, 2, 3, 22, 8, 34, 74, 56, 92, 22, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 510, 1, 1, 6, 2, 8, 16, 12, 18, 4, "Quarter-Finalist"),
        ("UEFA Euro 2024", "international", 3, 270, 0, 1, 3, 1, 4, 8, 7, 12, 3, "Round of 16")
    ]),
    ("Mikel Merino", "Spain", 30, "MID", "Premier League", "Arsenal", 2610, 5, 4, 46, 17, 44, 88, 54, 52, 20, 6, 0, 2028, None, 130000, [
        ("Premier League", "league", 29, 2610, 5, 4, 46, 17, 44, 88, 54, 52, 20, "Regular Season"),
        ("UEFA Euro 2024", "international", 7, 280, 1, 0, 6, 2, 5, 14, 8, 9, 3, "🏆 European Champion (Quarter-Final Hero)")
    ]),
    ("Dani Olmo", "Spain", 28, "MID", "La Liga", "FC Barcelona", 2340, 10, 7, 68, 28, 72, 46, 22, 16, 6, 4, 0, 2030, 500000000, 180000, [
        ("La Liga", "league", 26, 2340, 10, 7, 68, 28, 72, 46, 22, 16, 6, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 490, 3, 2, 16, 7, 14, 9, 4, 3, 1, "Quarter-Finalist"),
        ("UEFA Euro 2024", "international", 6, 430, 3, 2, 15, 6, 14, 11, 5, 4, 1, "🏆 Euro 2024 Golden Boot & Champion")
    ]),
    ("Marc Casadó", "Spain", 22, "MID", "La Liga", "FC Barcelona", 2430, 2, 5, 24, 8, 48, 86, 58, 38, 16, 5, 0, 2028, 100000000, 50000, [
        ("La Liga", "league", 27, 2430, 2, 5, 24, 8, 48, 86, 58, 38, 16, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 520, 0, 2, 5, 1, 10, 18, 11, 7, 2, "Quarter-Finalist")
    ]),
    ("Julián Álvarez", "Argentina", 26, "FWD", "La Liga", "Atlético Madrid", 2880, 18, 8, 96, 42, 64, 48, 24, 18, 6, 3, 0, 2030, 250000000, 200000, [
        ("La Liga", "league", 32, 2880, 18, 8, 96, 42, 64, 48, 24, 18, 6, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 510, 4, 2, 18, 8, 11, 8, 4, 2, 1, "Round of 16"),
        ("Copa América 2024", "international", 6, 470, 2, 1, 14, 6, 8, 12, 5, 3, 1, "🏆 Copa América Champion")
    ]),
    ("Conor Gallagher", "England", 26, "MID", "La Liga", "Atlético Madrid", 2700, 6, 4, 48, 18, 46, 96, 62, 44, 18, 8, 0, 2029, 150000000, 140000, [
        ("La Liga", "league", 30, 2700, 6, 4, 48, 18, 46, 96, 62, 44, 18, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 480, 1, 1, 8, 3, 7, 18, 11, 8, 3, "Round of 16"),
        ("UEFA Euro 2024", "international", 5, 210, 0, 0, 3, 1, 3, 9, 5, 4, 2, "Finalist")
    ]),
    ("Robin Le Normand", "Spain", 29, "DEF", "La Liga", "Atlético Madrid", 2790, 2, 1, 18, 6, 8, 72, 58, 142, 28, 6, 0, 2029, 100000000, 110000, [
        ("La Liga", "league", 31, 2790, 2, 1, 18, 6, 8, 72, 58, 142, 28, "Regular Season"),
        ("UEFA Euro 2024", "international", 6, 510, 0, 0, 3, 1, 2, 16, 12, 26, 6, "🏆 European Champion")
    ]),
    ("Michael Olise", "France", 24, "FWD", "Bundesliga", "Bayern Munich", 2700, 15, 12, 88, 38, 82, 54, 28, 16, 6, 4, 0, 2029, None, 190000, [
        ("Bundesliga", "league", 30, 2700, 15, 12, 88, 38, 82, 54, 28, 16, 6, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 510, 3, 3, 16, 7, 14, 9, 4, 2, 1, "Quarter-Finalist"),
        ("Olympics 2024", "international", 6, 520, 2, 5, 18, 8, 22, 12, 6, 3, 1, "Silver Medalist")
    ]),
    ("João Palhinha", "Portugal", 31, "MID", "Bundesliga", "Bayern Munich", 2610, 3, 2, 34, 10, 26, 114, 68, 56, 22, 9, 0, 2028, None, 175000, [
        ("Bundesliga", "league", 29, 2610, 3, 2, 34, 10, 26, 114, 68, 56, 22, "Regular Season"),
        ("UEFA Champions League", "continental", 5, 420, 0, 0, 4, 1, 3, 18, 11, 8, 4, "Quarter-Finalist"),
        ("UEFA Euro 2024", "international", 4, 340, 0, 0, 3, 1, 2, 19, 11, 7, 3, "Quarter-Finalist")
    ]),
    ("Serhou Guirassy", "Guinea", 30, "FWD", "Bundesliga", "Borussia Dortmund", 2700, 24, 5, 96, 46, 38, 28, 12, 22, 6, 3, 0, 2028, None, 140000, [
        ("Bundesliga", "league", 30, 2700, 24, 5, 96, 46, 38, 28, 12, 22, 6, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 520, 5, 1, 22, 10, 6, 5, 2, 3, 1, "Quarter-Finalist"),
        ("AFCON 2024", "international", 4, 310, 1, 0, 8, 3, 3, 3, 1, 2, 0, "Quarter-Finalist")
    ]),
    ("Teun Koopmeiners", "Netherlands", 28, "MID", "Serie A", "Juventus", 2880, 12, 7, 82, 32, 74, 68, 38, 34, 12, 5, 0, 2029, None, 150000, [
        ("Serie A", "league", 32, 2880, 12, 7, 82, 32, 74, 68, 38, 34, 12, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 510, 2, 2, 14, 5, 11, 12, 6, 5, 2, "Round of 16"),
        ("UEFA Europa League", "continental", 12, 1040, 3, 2, 28, 11, 24, 24, 14, 12, 4, "🏆 Europa League Winner")
    ]),
    ("Douglas Luiz", "Brazil", 28, "MID", "Serie A", "Juventus", 2610, 7, 7, 58, 22, 66, 82, 48, 36, 16, 8, 0, 2029, None, 140000, [
        ("Serie A", "league", 29, 2610, 7, 7, 58, 22, 66, 82, 48, 36, 16, "Regular Season"),
        ("Copa América 2024", "international", 3, 160, 0, 0, 3, 1, 3, 6, 4, 3, 1, "Quarter-Finalist")
    ]),
    ("Michele Di Gregorio", "Italy", 29, "GK", "Serie A", "Juventus", 2970, 0, 0, 0, 0, 1, 2, 1, 76, 1, 1, 0, 2029, None, 90000, [
        ("Serie A", "league", 33, 2970, 0, 0, 0, 0, 1, 2, 1, 76, 1, "Serie A Best Goalkeeper 23/24"),
        ("UEFA Champions League", "continental", 6, 540, 0, 0, 0, 0, 0, 1, 0, 12, 0, "Round of 16")
    ]),
    ("Romelu Lukaku", "Belgium", 33, "FWD", "Serie A", "Napoli", 2700, 18, 6, 88, 42, 42, 26, 12, 24, 8, 4, 0, 2027, None, 160000, [
        ("Serie A", "league", 30, 2700, 18, 6, 88, 42, 42, 26, 12, 24, 8, "Regular Season"),
        ("UEFA Euro 2024", "international", 4, 360, 3, 1, 14, 7, 6, 3, 1, 2, 1, "Round of 16")
    ]),
    ("Scott McTominay", "Scotland", 29, "MID", "Serie A", "Napoli", 2790, 8, 4, 62, 24, 38, 84, 52, 48, 20, 7, 0, 2028, None, 95000, [
        ("Serie A", "league", 31, 2790, 8, 4, 62, 24, 38, 84, 52, 48, 20, "Regular Season"),
        ("UEFA Euro 2024", "international", 3, 270, 1, 0, 6, 2, 3, 8, 5, 4, 2, "Group Stage")
    ]),
    ("João Neves", "Portugal", 21, "MID", "Ligue 1", "Paris Saint-Germain", 2790, 3, 8, 42, 16, 68, 98, 62, 34, 14, 5, 0, 2029, None, 140000, [
        ("Ligue 1", "league", 31, 2790, 3, 8, 42, 16, 68, 98, 62, 34, 14, "Regular Season"),
        ("UEFA Champions League", "continental", 6, 520, 1, 2, 8, 3, 12, 18, 11, 6, 2, "League Phase"),
        ("UEFA Euro 2024", "international", 2, 110, 0, 0, 2, 1, 2, 5, 3, 2, 0, "Quarter-Finalist")
    ]),
    ("Mason Greenwood", "England", 24, "FWD", "Ligue 1", "Olympique de Marseille", 2880, 19, 7, 98, 44, 64, 38, 18, 14, 5, 4, 0, 2029, None, 120000, [
        ("Ligue 1", "league", 32, 2880, 19, 7, 98, 44, 64, 38, 18, 14, 5, "Regular Season"),
        ("Coupe de France", "domestic_cup", 3, 270, 3, 1, 12, 6, 6, 3, 1, 1, 0, "Round of 16")
    ]),
    ("Pierre-Emile Højbjerg", "Denmark", 31, "MID", "Ligue 1", "Olympique de Marseille", 2970, 3, 4, 38, 12, 46, 96, 64, 54, 22, 7, 0, 2028, None, 110000, [
        ("Ligue 1", "league", 33, 2970, 3, 4, 38, 12, 46, 96, 64, 54, 22, "Regular Season"),
        ("UEFA Euro 2024", "international", 4, 360, 0, 1, 6, 2, 6, 14, 9, 8, 3, "Round of 16")
    ])
]

# Insert players
inserted_count = 0
comp_inserted_count = 0

for p in NEW_PLAYERS:
    name = p[0]
    if name.lower() in existing_names:
        print(f"Skipping {name}, already in database.")
        continue
    
    curr_p_id += 1
    nation, age, pos, league, team, mins, goals, assists = p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]
    shots, sot, chances, tackles, interc, clears, blocks, yellow, red = p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17]
    contract_year, release_clause, wage = p[18], p[19], p[20]
    comps = p[21]
    
    # Calculate modern market value:
    # Base valuation
    base_val = 15000000.0
    if goals + assists > 20:
        base_val += (goals * 4000000.0) + (assists * 2500000.0)
    elif goals + assists > 10:
        base_val += (goals * 3000000.0) + (assists * 2000000.0)
    else:
        base_val += (goals * 2000000.0) + (assists * 1500000.0)
        
    if pos in ("DEF", "GK"):
        base_val += (tackles * 350000.0) + (interc * 300000.0) + (clears * 150000.0)
    elif pos == "MID":
        base_val += (chances * 500000.0) + (tackles * 200000.0)
        
    # Age factor
    if age <= 21:
        base_val *= 1.40
    elif age <= 24:
        base_val *= 1.25
    elif age <= 27:
        base_val *= 1.10
    elif age <= 30:
        base_val *= 0.90
    else:
        base_val *= 0.60
        
    # Contract factor
    if contract_year >= 2030:
        base_val *= 1.20
    elif contract_year >= 2028:
        base_val *= 1.08
    elif contract_year == 2026:
        base_val *= 0.70
        
    # Buyout clause ceiling
    if release_clause and release_clause < base_val:
        base_val = float(release_clause)
        
    mkt_val = round(base_val, -5)
    
    # Defaults for secondary stats
    height = random.choice([178, 182, 185, 188, 191]) if pos in ("DEF", "GK") else random.choice([172, 175, 178, 180, 184])
    weight = round(height * 0.42, 1)
    drib_comp = round(chances * 0.7)
    drib_att = round(drib_comp * 1.5)
    passes_comp = round(mins * 0.55)
    passes_att = round(passes_comp * 1.22)
    prog_passes = round(passes_comp * 0.12)
    aerials = round((tackles + clears) * 0.3)
    touches = round(passes_att * 1.4)
    apps = max(18, round(mins / 85))
    cs = round(apps * 0.35) if pos in ("DEF", "GK") else 0
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
    inserted_count += 1
    
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
        comp_inserted_count += 1

conn.commit()
print(f"SUCCESS: Inserted {inserted_count} new players.")
print(f"SUCCESS: Inserted {comp_inserted_count} competition breakdown stats.")

# Verification query
c.execute("SELECT count(*) FROM players")
total_players = c.fetchone()[0]
c.execute("SELECT count(*) FROM player_competition_stats")
total_comps = c.fetchone()[0]
print(f"NEW DATABASE TOTALS: {total_players} players | {total_comps} competition records.")

conn.close()
