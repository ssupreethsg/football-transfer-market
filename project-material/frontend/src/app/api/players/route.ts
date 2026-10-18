import { NextRequest, NextResponse } from "next/server";
import rawPlayers from "@/data/players.json";

interface CompetitionStat {
  id: number;
  player_id: number;
  competition_name: string;
  competition_type: string;
  season?: string;
  appearances: number;
  minutes_played: number;
  goals: number;
  assists: number;
  shots: number;
  shots_on_target: number;
  chances_created: number;
  tackles_won: number;
  interceptions: number;
  clearances: number;
  blocks: number;
  yellow_cards: number;
  red_cards: number;
  stage_reached?: string;
}

interface PlayerRecord {
  id: number;
  name: string;
  nation?: string;
  age: number;
  position?: string;
  height_cm?: number;
  weight_kg?: number;
  league: string;
  team: string;
  appearances: number;
  minutes_played: number;
  goals: number;
  assists: number;
  shots: number;
  shots_on_target: number;
  dribbles_completed: number;
  dribbles_attempted: number;
  chances_created: number;
  passes_completed: number;
  passes_attempted: number;
  progressive_passes: number;
  tackles_won: number;
  defense_interceptions: number;
  clearances: number;
  blocks: number;
  aerials_won: number;
  clean_sheets: number;
  saves: number;
  goals_conceded: number;
  touches: number;
  yellow_cards: number;
  red_cards: number;
  contract_expires_year?: number;
  release_clause_eur?: number | null;
  wage_eur_weekly?: number;
  buyback_clause_eur?: number | null;
  sell_on_pct?: number | null;
  predicted_market_value_eur: number;
  competition_stats?: CompetitionStat[];
}

const playersData = rawPlayers as PlayerRecord[];

export async function GET(request: NextRequest) {
  const backendBase = process.env.BACKEND_URL;
  const searchParams = request.nextUrl.searchParams;

  if (backendBase) {
    try {
      const searchStr = searchParams.toString();
      const backendUrl = `${backendBase}/players${searchStr ? `?${searchStr}` : ""}`;
      const res = await fetch(backendUrl, { cache: "no-store" });
      if (res.ok) {
        return NextResponse.json(await res.json());
      }
    } catch {
      // Fallback to embedded dataset below
    }
  }

  // Standalone serverless mode for Vercel
  let filtered = [...playersData];

  const league = searchParams.get("league");
  if (league && league !== "All") {
    filtered = filtered.filter((p) =>
      p.league.toLowerCase().includes(league.toLowerCase())
    );
  }

  const team = searchParams.get("team");
  if (team) {
    filtered = filtered.filter((p) =>
      p.team.toLowerCase().includes(team.toLowerCase())
    );
  }

  const position = searchParams.get("position");
  if (position && position !== "All") {
    filtered = filtered.filter((p) => p.position === position.toUpperCase());
  }

  const normalize = (str: string) =>
    str ? str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase() : "";

  const search = searchParams.get("search");
  if (search) {
    const s = normalize(search);
    filtered = filtered.filter(
      (p) =>
        normalize(p.name).includes(s) || normalize(p.team).includes(s)
    );
  }


  const minValue = searchParams.get("min_value");
  if (minValue) {
    filtered = filtered.filter(
      (p) => p.predicted_market_value_eur >= parseFloat(minValue)
    );
  }

  const maxValue = searchParams.get("max_value");
  if (maxValue) {
    filtered = filtered.filter(
      (p) => p.predicted_market_value_eur <= parseFloat(maxValue)
    );
  }

  const hasReleaseClause = searchParams.get("has_release_clause");
  if (hasReleaseClause === "true") {
    filtered = filtered.filter(
      (p) => p.release_clause_eur != null && p.release_clause_eur > 0
    );
  } else if (hasReleaseClause === "false") {
    filtered = filtered.filter((p) => p.release_clause_eur == null);
  }

  const sortByValue = searchParams.get("sort_by_value") !== "false";
  if (sortByValue) {
    filtered.sort(
      (a, b) => b.predicted_market_value_eur - a.predicted_market_value_eur
    );
  } else {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  }

  const skip = parseInt(searchParams.get("skip") || "0", 10);
  const limit = parseInt(searchParams.get("limit") || "100", 10);

  return NextResponse.json(filtered.slice(skip, skip + limit));
}

