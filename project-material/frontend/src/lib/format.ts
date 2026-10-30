import type { CompType, DetailKey } from "./types";

export const dash = "–";

export function n(v: number | null | undefined, digits = 0): string {
  if (v === null || v === undefined || Number.isNaN(v)) return dash;
  return v.toLocaleString("en-GB", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function money(v: number | null | undefined): string {
  if (!v) return dash;
  if (v >= 1e6) return `€${(v / 1e6).toFixed(1)}m`;
  if (v >= 1e3) return `€${Math.round(v / 1e3)}k`;
  return `€${v}`;
}

export const TEAM_LOGO = (id: number) => `https://images.fotmob.com/image_resources/logo/teamlogo/${id}_small.png`;
export const PLAYER_IMG = (id: number) => `https://images.fotmob.com/image_resources/playerimages/${id}.png`;
export const COMP_LOGO = (id: number) => `https://images.fotmob.com/image_resources/logo/leaguelogo/${id}.png`;

export const COMP_TYPE_LABEL: Record<CompType, string> = {
  league: "League",
  domestic_cup: "Domestic cup",
  continental: "Continental / club",
  international: "National team",
};

export const COMP_TYPE_ORDER: CompType[] = ["league", "domestic_cup", "continental", "international"];

// Detailed stats shown on the expanded view, grouped like a match report.
export const DETAIL_GROUPS: { title: string; fields: [DetailKey, string, number?][] }[] = [
  { title: "Playing time", fields: [["matches", "Matches"], ["started", "Started"], ["minutes", "Minutes"], ["rating", "Avg rating", 2]] },
  {
    title: "Attacking",
    fields: [["goals", "Goals"], ["penalty_goals", "Penalty goals"], ["xg", "xG", 2], ["npxg", "Non-penalty xG", 2],
      ["shots", "Shots"], ["shots_on_target", "Shots on target"], ["headed_shots", "Headed shots"],
      ["touches_opp_box", "Touches in opp. box"], ["penalties_won", "Penalties won"]],
  },
  {
    title: "Creating",
    fields: [["assists", "Assists"], ["xa", "xA", 2], ["chances_created", "Chances created"],
      ["big_chances_created", "Big chances created"], ["accurate_passes", "Accurate passes"],
      ["pass_accuracy", "Pass accuracy %", 1], ["accurate_long_balls", "Accurate long balls"],
      ["accurate_crosses", "Accurate crosses"], ["line_breaking_passes", "Line-breaking passes"]],
  },
  {
    title: "Carrying & duels",
    fields: [["dribbles", "Successful dribbles"], ["dribble_success_rate", "Dribble success %", 1], ["touches", "Touches"],
      ["duels_won", "Duels won"], ["duels_won_pct", "Duels won %", 1], ["aerials_won", "Aerials won"],
      ["fouls_won", "Fouls won"], ["dispossessed", "Dispossessed"]],
  },
  {
    title: "Defending",
    fields: [["tackles", "Tackles"], ["interceptions", "Interceptions"], ["clearances", "Clearances"],
      ["blocks", "Blocked shots"], ["recoveries", "Recoveries"], ["possession_won_final_third", "Possession won, final third"],
      ["dribbled_past", "Dribbled past"], ["defensive_actions", "Defensive actions"]],
  },
  {
    title: "Goalkeeping",
    fields: [["saves", "Saves"], ["save_pct", "Save %", 1], ["goals_prevented", "Goals prevented", 2],
      ["penalties_saved", "Penalties saved"], ["high_claims", "High claims"], ["sweeper_actions", "Sweeper actions"],
      ["errors_led_to_goal", "Errors leading to goal"]],
  },
  {
    title: "Team while on pitch",
    fields: [["clean_sheets", "Clean sheets"], ["goals_conceded", "Goals conceded"], ["xg_against", "xG against", 2]],
  },
  { title: "Discipline", fields: [["yellow_cards", "Yellow cards"], ["red_cards", "Red cards"], ["fouls_committed", "Fouls committed"]] },
];
