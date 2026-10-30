// Shapes of the static dataset in public/data (built by backend/pipeline/build_dataset.py).
// A null value means the source has no number for it; it is shown as "–", never as 0.

export type CompType = "league" | "domestic_cup" | "continental" | "international";

export type Detailed = Partial<Record<DetailKey, number | null>>;

export type DetailKey =
  | "minutes" | "matches" | "started" | "rating" | "goals" | "assists" | "penalty_goals"
  | "xg" | "npxg" | "xgot" | "shots" | "shots_on_target" | "headed_shots" | "xa"
  | "chances_created" | "big_chances_created" | "accurate_passes" | "pass_accuracy"
  | "accurate_long_balls" | "long_ball_accuracy" | "accurate_crosses" | "cross_accuracy"
  | "line_breaking_passes" | "dribbles" | "dribble_success_rate" | "touches" | "touches_opp_box"
  | "duels_won" | "duels_won_pct" | "aerials_won" | "aerials_won_pct" | "dispossessed" | "fouls_won"
  | "penalties_won" | "tackles" | "interceptions" | "clearances" | "blocks" | "recoveries"
  | "dribbled_past" | "defensive_actions" | "possession_won_final_third" | "fouls_committed"
  | "yellow_cards" | "red_cards" | "clean_sheets" | "goals_conceded" | "xg_against" | "saves"
  | "save_pct" | "penalties_conceded" | "penalty_save_pct" | "goals_prevented" | "high_claims" | "sweeper_actions" | "penalties_saved"
  | "errors_led_to_goal";

export interface Basic {
  appearances: number | null;
  goals: number | null;
  assists: number | null;
  incomplete?: string[];
}

export interface CompetitionEntry extends Basic {
  competition: string;
  competition_id: number;
  country: string | null;
  type: CompType;
  team: string;
  edition: string;
  rating: number | null;
  detailed: Detailed | null;
}

export interface Season {
  season: string;
  teams: string[];
  competitions: CompetitionEntry[];
  totals: Basic;
  totals_detailed: Detailed | null;
}

export interface CareerCompetition extends Basic {
  competition: string;
  competition_id: number;
  type: CompType;
  seasons: number;
  detailed: Detailed | null;
}

export interface PlayerFile {
  id: number;
  name: string;
  team: string;
  team_id: number;
  league: string;
  on_loan: boolean | null;
  position: string | null;
  position_group: string | null;
  nationality: string | null;
  birth_date: string | null;
  age: number | null;
  height_cm: number | null;
  preferred_foot: string | null;
  contract_end: string | null;
  market_value: { value_eur: number; date: string; source: string } | null;
  career_totals: Basic & { detailed: Detailed | null; detailed_seasons: string[] };
  career_by_competition: CareerCompetition[];
  seasons: Season[];
  source: { provider: string; url: string };
}

export interface SeasonLine {
  appearances: number | null;
  goals: number | null;
  assists: number | null;
  minutes: number | null;
}

export interface IndexRow {
  id: number;
  name: string;
  team: string;
  team_id: number;
  league: string;
  position: string | null;
  position_group: string | null;
  nationality: string | null;
  age: number | null;
  market_value_eur: number | null;
  current_season: SeasonLine | null;
  last_season: SeasonLine | null;
  last_season_name: string | null;
  career: { appearances: number | null; goals: number | null; assists: number | null };
}

export interface Meta {
  built_at: string;
  current_season: string;
  players: number;
  clubs: number;
  leagues: Record<string, number>;
  source: string;
}
