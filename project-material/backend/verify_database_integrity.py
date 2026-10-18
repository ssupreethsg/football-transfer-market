#!/usr/bin/env python3
"""
================================================================================
E2E Verification Test Suite for Football Transfer Analytics Database
Target Database: backend/sql_app.db
August 30, 2026 Ground Truth & Integrity Specification
================================================================================

This test suite executes a comprehensive, 4-tier verification protocol:
- Tier 1: 96-Club Coverage Verification across 5 European Leagues
- Tier 2: Squad Size Boundaries [20, 33] for all 96 Clubs
- Tier 3: 2025/2026 Mega-Transfers Ground-Truth Verification
- Tier 4: Global Departures & Contract Expirations Zero-Check (Saudi/MLS/Brazil/Turkey/Retired)
- Extended Tier 5: Foreign Key Referential Integrity & Schema Sanity Audit

Exit Code:
- 0: All tiers and assertions passed (100% compliant)
- 1: One or more test assertions failed
================================================================================
"""

import os
import sys
import sqlite3
import argparse
import json
import unicodedata
import re
from typing import Dict, List, Tuple, Any, Optional

# --- Configuration & Ground Truth Constants ---

TOP_5_LEAGUES = [
    "Premier League",
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Ligue 1"
]

EXPECTED_LEAGUE_CLUB_COUNTS = {
    "Premier League": 20,
    "La Liga": 20,
    "Serie A": 20,
    "Bundesliga": 18,
    "Ligue 1": 18
}

TOTAL_EXPECTED_CLUBS = 96

SQUAD_SIZE_MIN = 20
SQUAD_SIZE_MAX = 33

# Tier 3: Mega-Transfers (Player Name, Target Team, Former/Legacy Team to Reject)
# Format: (Player Name Search, Target Team, Former Team / Forbidden Legacy Club)
MEGA_TRANSFERS = [
    ("Kylian Mbappé", "Real Madrid", "Paris Saint-Germain"),
    ("Julián Álvarez", "Atlético Madrid", "Manchester City"),
    ("Dani Olmo", "FC Barcelona", "RB Leipzig"),
    ("Riccardo Calafiori", "Arsenal", "Bologna"),
    ("Pedro Neto", "Chelsea", "Wolverhampton Wanderers"),
    ("Matthijs de Ligt", "Manchester United", "Bayern Munich"),
    ("Noussair Mazraoui", "Manchester United", "Bayern Munich"),
    ("Michael Olise", "Bayern Munich", "Crystal Palace"),
    ("João Neves", "Paris Saint-Germain", "Benfica"),
    ("Teun Koopmeiners", "Juventus", "Atalanta"),
    ("Douglas Luiz", "Juventus", "Aston Villa"),
    ("Mikel Merino", "Arsenal", "Real Sociedad"),
    ("Conor Gallagher", "Atlético Madrid", "Chelsea"),
    ("Alexander Sørloth", "Atlético Madrid", "Villarreal"),
    ("Romelu Lukaku", "Napoli", "Chelsea"),
    ("Scott McTominay", "Napoli", "Manchester United"),
]

# Tier 4: Global Departures (Saudi Pro League, MLS, Brazil, Qatar, Turkey, Greece, Championship, Retired)
# These players MUST NOT appear in any Top 5 European League squad
GLOBAL_DEPARTURES = [
    ("Nacho", "Al Qadsiah / Saudi Pro League"),
    ("Joselu", "Al Gharafa / Qatar"),
    ("Memphis Depay", "Corinthians / Brazil"),
    ("Thiago Silva", "Fluminense / Brazil"),
    ("Olivier Giroud", "LAFC / MLS"),
    ("Marco Reus", "LA Galaxy / MLS"),
    ("Raphaël Varane", "Como / Retired"),
    ("Toni Kroos", "Retired"),
    ("Sergio Ramos", "Free Agent / Departed"),
    ("Joel Matip", "Free Agent / Retired"),
    ("Thiago Alcântara", "Retired"),
    ("Keylor Navas", "Free Agent / Departed"),
    ("Wissam Ben Yedder", "Free Agent / Departed"),
    ("Ciro Immobile", "Besiktas / Turkey"),
    ("Victor Osimhen", "Galatasaray / Turkey"),
    ("Sofyan Amrabat", "Fenerbahce / Turkey"),
    ("Anthony Martial", "AEK Athens / Greece"),
    ("Felipe Anderson", "Palmeiras / Brazil"),
    ("Philippe Coutinho", "Vasco da Gama / Brazil"),
    ("Ivan Toney", "Al Ahli / Saudi Pro League"),
    ("Cristiano Ronaldo", "Al Nassr / Saudi Pro League"),
    ("Karim Benzema", "Al Ittihad / Saudi Pro League"),
    ("Neymar Jr", "Al Hilal / Saudi Pro League"),
    ("Sadio Mané", "Al Nassr / Saudi Pro League"),
    ("Riyad Mahrez", "Al Ahli / Saudi Pro League"),
    ("Roberto Firmino", "Al Ahli / Saudi Pro League"),
    ("Jordan Henderson", "Ajax / Departed"),
]


# --- Helper Functions ---

def strip_accents(s: str) -> str:
    """Normalize string and remove diacritics for resilient matching."""
    if not s:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def normalize_string(s: str) -> str:
    """Lowercase, strip accents, and remove punctuation for robust comparison."""
    s = strip_accents(s).lower()
    return re.sub(r'[^a-z0-9\s]', '', s).strip()


class TestResult:
    def __init__(self, name: str, tier: str):
        self.name = name
        self.tier = tier
        self.passed = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.details: Dict[str, Any] = {}

    def fail(self, message: str):
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str):
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tier": self.tier,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
        }


class DatabaseIntegrityVerifier:
    def __init__(self, db_path: str):
        self.db_path = db_path
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.abspath(self.db_path)
        self.results: List[TestResult] = []

    def _get_connection(self) -> sqlite3.Connection:
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Target SQLite database not found at: {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================================================
    # TIER 1: 96-Club Coverage Verification
    # =========================================================================
    def verify_tier_1_club_coverage(self) -> TestResult:
        result = TestResult("Tier 1: 96-Club Coverage Verification", "Tier 1")
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 1.1 Total distinct clubs in Top 5 leagues
            placeholders = ', '.join(['?'] * len(TOP_5_LEAGUES))
            cursor.execute(
                f"SELECT count(DISTINCT team) FROM players WHERE league IN ({placeholders})",
                TOP_5_LEAGUES
            )
            total_clubs = cursor.fetchone()[0]
            result.details["total_top5_clubs"] = total_clubs
            result.details["expected_total_clubs"] = TOTAL_EXPECTED_CLUBS

            if total_clubs != TOTAL_EXPECTED_CLUBS:
                result.fail(
                    f"Expected exactly {TOTAL_EXPECTED_CLUBS} distinct clubs across Top 5 leagues, "
                    f"but found {total_clubs}."
                )

            # 1.2 Breakdown per league
            league_breakdown = {}
            cursor.execute(f"""
                SELECT league, count(DISTINCT team) as club_count, count(*) as player_count
                FROM players
                WHERE league IN ({placeholders})
                GROUP BY league
                ORDER BY league
            """, TOP_5_LEAGUES)

            rows = cursor.fetchall()
            for row in rows:
                lg = row["league"]
                c_cnt = row["club_count"]
                p_cnt = row["player_count"]
                expected_c = EXPECTED_LEAGUE_CLUB_COUNTS.get(lg, 0)
                league_breakdown[lg] = {
                    "actual_clubs": c_cnt,
                    "expected_clubs": expected_c,
                    "total_players": p_cnt
                }
                if c_cnt != expected_c:
                    result.fail(
                        f"League '{lg}': Expected {expected_c} clubs, but found {c_cnt}."
                    )

            # Check for missing leagues
            for expected_lg, expected_cnt in EXPECTED_LEAGUE_CLUB_COUNTS.items():
                if expected_lg not in league_breakdown:
                    result.fail(f"League '{expected_lg}' is completely missing from the database!")

            result.details["league_breakdown"] = league_breakdown

            # 1.3 Lower division check / distinct leagues in database
            cursor.execute("SELECT DISTINCT league FROM players")
            all_leagues = [r[0] for r in cursor.fetchall()]
            result.details["all_leagues_in_db"] = all_leagues

        except Exception as e:
            result.fail(f"Tier 1 execution encountered exception: {str(e)}")
        finally:
            conn.close()

        self.results.append(result)
        return result

    # =========================================================================
    # TIER 2: Squad Size Boundaries Verification [20, 33]
    # =========================================================================
    def verify_tier_2_squad_sizes(self) -> TestResult:
        result = TestResult("Tier 2: Squad Size Boundaries [20, 33]", "Tier 2")
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            placeholders = ', '.join(['?'] * len(TOP_5_LEAGUES))
            query = f"""
                SELECT team, league, count(*) as squad_size
                FROM players
                WHERE league IN ({placeholders})
                GROUP BY team, league
                ORDER BY league, team
            """
            cursor.execute(query, TOP_5_LEAGUES)
            rows = cursor.fetchall()

            teams_data = []
            underpopulated_teams = []
            overpopulated_teams = []
            squad_sizes = []

            for row in rows:
                team = row["team"]
                league = row["league"]
                size = row["squad_size"]
                squad_sizes.append(size)
                teams_data.append({"team": team, "league": league, "squad_size": size})

                if size < SQUAD_SIZE_MIN:
                    underpopulated_teams.append((team, league, size))
                    result.fail(
                        f"Underpopulated squad: '{team}' ({league}) has {size} players "
                        f"(Minimum required is {SQUAD_SIZE_MIN})."
                    )
                elif size > SQUAD_SIZE_MAX:
                    overpopulated_teams.append((team, league, size))
                    result.fail(
                        f"Overpopulated squad: '{team}' ({league}) has {size} players "
                        f"(Maximum allowed is {SQUAD_SIZE_MAX})."
                    )

            result.details["total_teams_checked"] = len(teams_data)
            result.details["squad_min"] = min(squad_sizes) if squad_sizes else 0
            result.details["squad_max"] = max(squad_sizes) if squad_sizes else 0
            result.details["squad_avg"] = sum(squad_sizes) / len(squad_sizes) if squad_sizes else 0
            result.details["underpopulated_teams"] = underpopulated_teams
            result.details["overpopulated_teams"] = overpopulated_teams

            if not underpopulated_teams and not overpopulated_teams:
                result.details["status"] = (
                    f"All {len(teams_data)} teams strictly comply with squad range "
                    f"[{SQUAD_SIZE_MIN}, {SQUAD_SIZE_MAX}]."
                )

        except Exception as e:
            result.fail(f"Tier 2 execution encountered exception: {str(e)}")
        finally:
            conn.close()

        self.results.append(result)
        return result

    # =========================================================================
    # TIER 3: Mega-Transfers Verification
    # =========================================================================
    def verify_tier_3_mega_transfers(self) -> TestResult:
        result = TestResult("Tier 3: Mega-Transfers Ground-Truth Verification", "Tier 3")
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            verified_transfers = []
            failed_transfers = []

            for search_name, target_team, legacy_team in MEGA_TRANSFERS:
                # Query player by name or accent-stripped match
                norm_search = normalize_string(search_name)
                cursor.execute(
                    "SELECT id, name, team, league, predicted_market_value_eur FROM players"
                )
                all_players = cursor.fetchall()

                # Find matching players
                matches = []
                for p in all_players:
                    p_norm = normalize_string(p["name"])
                    # Check exact or strong substring match
                    if norm_search == p_norm or (len(norm_search) > 6 and norm_search in p_norm):
                        matches.append(p)

                if not matches:
                    # Fallback SQL LIKE query
                    cursor.execute(
                        "SELECT id, name, team, league, predicted_market_value_eur FROM players WHERE name LIKE ?",
                        (f"%{strip_accents(search_name).split()[-1]}%",)
                    )
                    like_rows = cursor.fetchall()
                    for r in like_rows:
                        if normalize_string(search_name) in normalize_string(r["name"]):
                            matches.append(r)

                if not matches:
                    result.fail(
                        f"Player Not Found: '{search_name}' expected at '{target_team}' "
                        f"was not found in database."
                    )
                    failed_transfers.append({
                        "player": search_name,
                        "expected_team": target_team,
                        "status": "NOT_FOUND"
                    })
                    continue

                # Evaluate match
                player_rec = matches[0]
                actual_team = player_rec["team"]
                actual_league = player_rec["league"]

                norm_actual_team = normalize_string(actual_team)
                norm_target_team = normalize_string(target_team)
                norm_legacy_team = normalize_string(legacy_team)

                is_target_match = (
                    norm_target_team in norm_actual_team or
                    norm_actual_team in norm_target_team
                )
                is_legacy_match = (
                    norm_legacy_team in norm_actual_team or
                    norm_actual_team in norm_legacy_team
                )

                if is_target_match and not is_legacy_match:
                    verified_transfers.append({
                        "player": player_rec["name"],
                        "team": actual_team,
                        "league": actual_league,
                        "status": "VERIFIED"
                    })
                else:
                    if is_legacy_match:
                        result.fail(
                            f"Legacy Team Conflict: '{player_rec['name']}' is still assigned to former club "
                            f"'{actual_team}' instead of new club '{target_team}'!"
                        )
                    else:
                        result.fail(
                            f"Wrong Club Assignment: '{player_rec['name']}' is at '{actual_team}', "
                            f"expected '{target_team}'."
                        )
                    failed_transfers.append({
                        "player": player_rec["name"],
                        "actual_team": actual_team,
                        "expected_team": target_team,
                        "status": "INCORRECT_TEAM"
                    })

            result.details["verified_transfers"] = verified_transfers
            result.details["failed_transfers"] = failed_transfers
            result.details["total_checked"] = len(MEGA_TRANSFERS)
            result.details["total_passed"] = len(verified_transfers)

        except Exception as e:
            result.fail(f"Tier 3 execution encountered exception: {str(e)}")
        finally:
            conn.close()

        self.results.append(result)
        return result

    # =========================================================================
    # TIER 4: Global Departures Zero-Check
    # =========================================================================
    def verify_tier_4_global_departures(self) -> TestResult:
        result = TestResult("Tier 4: Global Departures Zero-Check", "Tier 4")
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            departed_violations = []

            placeholders = ', '.join(['?'] * len(TOP_5_LEAGUES))

            for departed_name, destination in GLOBAL_DEPARTURES:
                norm_dep = normalize_string(departed_name)

                # Fetch all top 5 players to perform robust normalized check
                cursor.execute(
                    f"SELECT id, name, team, league FROM players WHERE league IN ({placeholders})",
                    TOP_5_LEAGUES
                )
                rows = cursor.fetchall()

                for row in rows:
                    p_name = row["name"]
                    p_norm = normalize_string(p_name)

                    # Match condition: exact match or precise full token match
                    match_found = False
                    if norm_dep == p_norm:
                        match_found = True
                    elif " " in departed_name and norm_dep in p_norm:
                        # Multi-word name like "Sergio Ramos", "Cristiano Ronaldo"
                        match_found = True
                    elif len(departed_name) >= 5 and p_norm == norm_dep:
                        match_found = True
                    elif departed_name in ["Nacho", "Joselu"] and p_name.strip().lower() in [departed_name.lower(), f"{departed_name.lower()} fernandez"]:
                        match_found = True

                    if match_found:
                        # Found a departed player lingering in a Top 5 club
                        violation = {
                            "player_name": p_name,
                            "searched_as": departed_name,
                            "team": row["team"],
                            "league": row["league"],
                            "destination": destination
                        }
                        departed_violations.append(violation)
                        result.fail(
                            f"Departed Player Lingering: '{p_name}' was found at '{row['team']}' ({row['league']}), "
                            f"but departed to '{destination}' and must be purged."
                        )

            result.details["total_departures_checked"] = len(GLOBAL_DEPARTURES)
            result.details["violations_count"] = len(departed_violations)
            result.details["violations"] = departed_violations

            if not departed_violations:
                result.details["status"] = (
                    f"All {len(GLOBAL_DEPARTURES)} global departed players confirmed purged (0 lingering in Top 5 leagues)."
                )

        except Exception as e:
            result.fail(f"Tier 4 execution encountered exception: {str(e)}")
        finally:
            conn.close()

        self.results.append(result)
        return result

    # =========================================================================
    # EXTENDED TIER 5: Referential Integrity & Data Sanity Audit
    # =========================================================================
    def verify_tier_5_extended_integrity(self) -> TestResult:
        result = TestResult("Tier 5: Referential Integrity & Schema Sanity Audit", "Extended Tier 5")
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 5.1 Orphaned competition stats check
            cursor.execute("""
                SELECT count(*) FROM player_competition_stats 
                WHERE player_id NOT IN (SELECT id FROM players)
            """)
            orphaned_stats = cursor.fetchone()[0]
            result.details["orphaned_competition_stats"] = orphaned_stats
            if orphaned_stats > 0:
                result.fail(f"Referential integrity failure: Found {orphaned_stats} orphaned competition stats records.")

            # 5.2 Players missing names, positions, or invalid ages
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN name IS NULL OR TRIM(name) = '' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN age IS NULL OR age < 15 OR age > 45 THEN 1 ELSE 0 END),
                    SUM(CASE WHEN position IS NULL OR position NOT IN ('FWD', 'MID', 'DEF', 'GK') THEN 1 ELSE 0 END),
                    SUM(CASE WHEN predicted_market_value_eur IS NULL OR predicted_market_value_eur <= 0 THEN 1 ELSE 0 END)
                FROM players
                WHERE league IN ('Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1')
            """)
            null_names, invalid_ages, invalid_positions, invalid_values = cursor.fetchone()

            result.details["null_or_empty_names"] = null_names or 0
            result.details["invalid_ages"] = invalid_ages or 0
            result.details["invalid_positions"] = invalid_positions or 0
            result.details["invalid_market_values"] = invalid_values or 0

            if null_names and null_names > 0:
                result.fail(f"Data sanity failure: {null_names} players have null/empty names.")
            if invalid_ages and invalid_ages > 0:
                result.fail(f"Data sanity failure: {invalid_ages} players have unrealistic/null ages.")
            if invalid_positions and invalid_positions > 0:
                result.fail(f"Data sanity failure: {invalid_positions} players have invalid positions.")
            if invalid_values and invalid_values > 0:
                result.fail(f"Data sanity failure: {invalid_values} players have null/negative market valuation.")

        except Exception as e:
            result.fail(f"Tier 5 execution encountered exception: {str(e)}")
        finally:
            conn.close()

        self.results.append(result)
        return result

    # =========================================================================
    # MASTER RUNNER
    # =========================================================================
    def run_all(self) -> Tuple[bool, List[TestResult]]:
        self.results.clear()
        self.verify_tier_1_club_coverage()
        self.verify_tier_2_squad_sizes()
        self.verify_tier_3_mega_transfers()
        self.verify_tier_4_global_departures()
        self.verify_tier_5_extended_integrity()

        all_passed = all(r.passed for r in self.results)
        return all_passed, self.results


# --- Console Reporter & Formatter ---

def format_report(db_path: str, results: List[TestResult], all_passed: bool) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append("  EUROPEAN FOOTBALL TRANSFER ANALYTICS — E2E DATABASE VERIFICATION REPORT")
    lines.append(f"  Target Database: {db_path}")
    lines.append("=" * 80)

    for res in results:
        status_str = "[PASS]" if res.passed else "[FAIL]"
        lines.append(f"\n>>> {status_str} {res.name}")

        if res.tier == "Tier 1":
            bd = res.details.get("league_breakdown", {})
            lines.append("    League Breakdown:")
            for lg, info in bd.items():
                match_icon = "✓" if info["actual_clubs"] == info["expected_clubs"] else "✗"
                lines.append(
                    f"      {match_icon} {lg:<18} : {info['actual_clubs']:>2}/{info['expected_clubs']} clubs | "
                    f"{info['total_players']:>4} players"
                )
            lines.append(
                f"    Total Top-5 Clubs: {res.details.get('total_top5_clubs')}/{res.details.get('expected_total_clubs')}"
            )

        elif res.tier == "Tier 2":
            lines.append(
                f"    Clubs Evaluated: {res.details.get('total_teams_checked')} | "
                f"Squad Bounds: [{SQUAD_SIZE_MIN}, {SQUAD_SIZE_MAX}]"
            )
            lines.append(
                f"    Squad Size Range: Min={res.details.get('squad_min')}, "
                f"Max={res.details.get('squad_max')}, "
                f"Avg={res.details.get('squad_avg', 0):.1f} players/club"
            )
            if res.details.get("underpopulated_teams"):
                lines.append("    Underpopulated Clubs (< 20):")
                for t, lg, sz in res.details["underpopulated_teams"]:
                    lines.append(f"      - {t} ({lg}): {sz} players")
            if res.details.get("overpopulated_teams"):
                lines.append("    Overpopulated Clubs (> 33):")
                for t, lg, sz in res.details["overpopulated_teams"]:
                    lines.append(f"      - {t} ({lg}): {sz} players")

        elif res.tier == "Tier 3":
            lines.append(
                f"    Transfers Verified: {res.details.get('total_passed')}/{res.details.get('total_checked')}"
            )
            for vt in res.details.get("verified_transfers", []):
                lines.append(f"      ✓ {vt['player']:<22} -> {vt['team']} ({vt['league']})")
            for ft in res.details.get("failed_transfers", []):
                lines.append(f"      ✗ {ft.get('player'):<22} -> FAILED ({ft.get('status')})")

        elif res.tier == "Tier 4":
            lines.append(
                f"    Departures Checked: {res.details.get('total_departures_checked')} | "
                f"Active Top-5 Violations: {res.details.get('violations_count')}"
            )
            if res.details.get("violations"):
                lines.append("    Violations Found:")
                for v in res.details["violations"]:
                    lines.append(
                        f"      ✗ {v['player_name']} lingering at {v['team']} ({v['league']}) [Moved to: {v['destination']}]"
                    )

        elif res.tier == "Extended Tier 5":
            lines.append(
                f"    Orphaned Stats Records: {res.details.get('orphaned_competition_stats', 0)} | "
                f"Null Names: {res.details.get('null_or_empty_names', 0)} | "
                f"Invalid Ages: {res.details.get('invalid_ages', 0)} | "
                f"Invalid Values: {res.details.get('invalid_market_values', 0)}"
            )

        if res.errors:
            lines.append("    Errors:")
            for err in res.errors:
                lines.append(f"      [ERROR] {err}")

    lines.append("\n" + "=" * 80)
    if all_passed:
        lines.append("  FINAL RESULT: ALL TIERS PASSED [100% COMPLIANT]")
        lines.append("  Database strictly adheres to August 30, 2026 ground truth specifications.")
    else:
        lines.append("  FINAL RESULT: VERIFICATION FAILED — Integrity Violations Detected!")
    lines.append("=" * 80)

    return "\n".join(lines)


# --- Unittest Framework Integration ---

import unittest

class TestDatabaseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        default_db = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql_app.db"))
        cls.verifier = DatabaseIntegrityVerifier(default_db)

    def test_tier_1_96_club_coverage(self):
        """Tier 1: Verify exactly 96 clubs exist across the 5 leagues (20 PL, 20 La Liga, 20 Serie A, 18 Bundesliga, 18 Ligue 1)."""
        res = self.verifier.verify_tier_1_club_coverage()
        self.assertTrue(res.passed, f"Tier 1 Failed with errors: {'; '.join(res.errors)}")

    def test_tier_2_squad_size_boundaries(self):
        """Tier 2: Verify squad size is strictly between 20 and 33 for ALL 96 teams."""
        res = self.verifier.verify_tier_2_squad_sizes()
        self.assertTrue(res.passed, f"Tier 2 Failed with errors: {'; '.join(res.errors)}")

    def test_tier_3_mega_transfers_sync(self):
        """Tier 3: Verify all 16 key mega-transfers are at their August 2026 destination clubs."""
        res = self.verifier.verify_tier_3_mega_transfers()
        self.assertTrue(res.passed, f"Tier 3 Failed with errors: {'; '.join(res.errors)}")

    def test_tier_4_global_departures_zero_check(self):
        """Tier 4: Verify 0 players who departed globally or retired remain active in Top 5 leagues."""
        res = self.verifier.verify_tier_4_global_departures()
        self.assertTrue(res.passed, f"Tier 4 Failed with errors: {'; '.join(res.errors)}")

    def test_tier_5_referential_integrity_and_data_sanity(self):
        """Tier 5: Verify foreign key referential integrity and schema data quality."""
        res = self.verifier.verify_tier_5_extended_integrity()
        self.assertTrue(res.passed, f"Tier 5 Failed with errors: {'; '.join(res.errors)}")


# --- Standalone CLI Runner ---

def main():
    default_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql_app.db")
    parser = argparse.ArgumentParser(
        description="Comprehensive E2E Verification Test Suite for Football Transfer Analytics Database"
    )
    parser.add_argument(
        "--db",
        default=default_db,
        help=f"Path to SQLite database file (default: {default_db})"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output test results in machine-readable JSON format"
    )
    parser.add_argument(
        "--unittest",
        action="store_true",
        help="Run via unittest test runner instead of custom CLI reporter"
    )
    args = parser.parse_args()

    if args.unittest:
        os.environ["DB_PATH"] = args.db
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseIntegrity)
        runner = unittest.TextTestRunner(verbosity=2)
        test_result = runner.run(suite)
        sys.exit(0 if test_result.wasSuccessful() else 1)

    verifier = DatabaseIntegrityVerifier(args.db)
    all_passed, results = verifier.run_all()

    if args.json:
        payload = {
            "database_path": args.db,
            "all_passed": all_passed,
            "results": [r.to_dict() for r in results]
        }
        print(json.dumps(payload, indent=2))
    else:
        report = format_report(args.db, results, all_passed)
        print(report)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

