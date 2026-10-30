"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { IndexRow, Meta } from "@/lib/types";
import { PLAYER_IMG, TEAM_LOGO, money, n } from "@/lib/format";

const LEAGUES = ["All", "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"];
const POSITIONS: [string, string][] = [["All", "All"], ["keepers", "Goalkeepers"], ["defenders", "Defenders"],
  ["midfielders", "Midfielders"], ["attackers", "Attackers"]];
const SORTS: [string, string][] = [
  ["value", "Market value"], ["cur_goals", "Goals this season"], ["cur_ga", "Goals + assists this season"],
  ["last_goals", "Goals last season"], ["last_ga", "Goals + assists last season"], ["career_goals", "Career goals"],
  ["name", "Name"],
];
const PAGE = 60;

const fold = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const ga = (l: { goals: number | null; assists: number | null } | null) => (l?.goals ?? 0) + (l?.assists ?? 0);

export default function Home() {
  const [rows, setRows] = useState<IndexRow[] | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [league, setLeague] = useState("All");
  const [position, setPosition] = useState("All");
  const [club, setClub] = useState("All");
  const [sort, setSort] = useState("value");
  const [limit, setLimit] = useState(PAGE);

  useEffect(() => {
    Promise.all([fetch("/data/index.json"), fetch("/data/meta.json")])
      .then(async ([a, b]) => {
        if (!a.ok || !b.ok) throw new Error("Could not load the player dataset.");
        setRows(await a.json());
        setMeta(await b.json());
      })
      .catch((e) => setError(String(e.message || e)));
  }, []);

  const clubs = useMemo(() => {
    if (!rows) return [];
    const set = new Set(rows.filter((r) => league === "All" || r.league === league).map((r) => r.team));
    return [...set].sort((a, b) => a.localeCompare(b));
  }, [rows, league]);

  const filtered = useMemo(() => {
    if (!rows) return [];
    const q = fold(query.trim());
    const out = rows.filter((r) =>
      (league === "All" || r.league === league) &&
      (position === "All" || r.position_group === position) &&
      (club === "All" || r.team === club) &&
      (!q || fold(r.name).includes(q) || fold(r.team).includes(q)));
    const key: Record<string, (r: IndexRow) => number> = {
      value: (r) => r.market_value_eur ?? 0,
      cur_goals: (r) => r.current_season?.goals ?? 0,
      cur_ga: (r) => ga(r.current_season),
      last_goals: (r) => r.last_season?.goals ?? 0,
      last_ga: (r) => ga(r.last_season),
      career_goals: (r) => r.career.goals ?? 0,
    };
    if (sort === "name") out.sort((a, b) => a.name.localeCompare(b.name));
    else out.sort((a, b) => key[sort](b) - key[sort](a));
    return out;
  }, [rows, query, league, position, club, sort]);

  const pill = (active: boolean) =>
    `px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors cursor-pointer ${active
      ? "bg-emerald-500 text-slate-950 border-emerald-500"
      : "bg-slate-900 text-slate-300 border-slate-700 hover:border-emerald-500/60"}`;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 text-center">
          <h1 className="text-3xl md:text-5xl font-black tracking-tight">
            Football <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">Transfer Market</span>
          </h1>
          <p className="text-slate-400 mt-3 max-w-2xl mx-auto text-sm md:text-base">
            Every player at every club in Europe&rsquo;s top 5 leagues, with full career stats split by season and by competition:
            league, domestic cups, European and international matches.
          </p>
          {meta && (
            <p className="text-xs text-slate-500 mt-3">
              {n(meta.players)} players · {meta.clubs} clubs · season {meta.current_season} · updated{" "}
              {new Date(meta.built_at).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
            </p>
          )}
          <div className="max-w-xl mx-auto mt-6">
            <input
              value={query}
              onChange={(e) => { setQuery(e.target.value); setLimit(PAGE); }}
              placeholder="Search a player or club (e.g. Haaland, Mbappé, Bayern)"
              className="w-full bg-slate-900 border border-slate-700 rounded-full py-3 px-5 text-sm focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>
      </header>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        <div className="flex flex-wrap gap-2 mb-3">
          {LEAGUES.map((l) => (
            <button key={l} className={pill(league === l)} onClick={() => { setLeague(l); setClub("All"); setLimit(PAGE); }}>{l}</button>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2 mb-6">
          {POSITIONS.map(([k, label]) => (
            <button key={k} className={pill(position === k)} onClick={() => { setPosition(k); setLimit(PAGE); }}>{label}</button>
          ))}
          <select value={club} onChange={(e) => { setClub(e.target.value); setLimit(PAGE); }}
            className="bg-slate-900 border border-slate-700 rounded-full px-3 py-1.5 text-xs">
            <option value="All">All clubs</option>
            {clubs.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={sort} onChange={(e) => setSort(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-full px-3 py-1.5 text-xs sm:ml-auto">
            {SORTS.map(([k, label]) => <option key={k} value={k}>Sort: {label}</option>)}
          </select>
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}
        {!rows && !error && <p className="text-slate-500 text-sm">Loading players…</p>}
        {rows && (
          <>
            <p className="text-xs text-slate-500 mb-3">{n(filtered.length)} players</p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {filtered.slice(0, limit).map((r) => (
                <Link key={r.id} href={`/players/${r.id}`}
                  className="block bg-slate-900/70 border border-slate-800 rounded-2xl p-4 hover:border-emerald-500/50 transition-colors">
                  <div className="flex items-center gap-3">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={PLAYER_IMG(r.id)} alt="" loading="lazy" className="w-12 h-12 rounded-full bg-slate-800 object-cover" />
                    <div className="min-w-0">
                      <p className="font-bold truncate">{r.name}</p>
                      <p className="text-xs text-slate-400 flex items-center gap-1 truncate">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={TEAM_LOGO(r.team_id)} alt="" loading="lazy" className="w-4 h-4" />
                        {r.team}
                      </p>
                      <p className="text-[11px] text-slate-500 truncate">{[r.position, r.nationality, r.age && `${r.age} yrs`].filter(Boolean).join(" · ")}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mt-4 text-center">
                    <Line label={meta?.current_season ?? "This season"} l={r.current_season} />
                    <Line label={r.last_season_name ?? "Last season"} l={r.last_season} />
                    <div>
                      <p className="text-[10px] uppercase tracking-wide text-slate-500">Value</p>
                      <p className="text-sm font-bold text-emerald-400">{money(r.market_value_eur)}</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
            {limit < filtered.length && (
              <div className="text-center mt-6">
                <button onClick={() => setLimit(limit + PAGE)}
                  className="px-5 py-2 rounded-full border border-slate-700 text-sm hover:border-emerald-500 cursor-pointer">
                  Show more
                </button>
              </div>
            )}
          </>
        )}
      </section>

      <footer className="max-w-7xl mx-auto px-4 sm:px-6 py-8 text-xs text-slate-500 border-t border-slate-800">
        Stats: FotMob (match data by Opta / Stats Perform); league goals and assists cross-checked with Understat.
        Market values: SciSports via FotMob. &ldquo;–&rdquo; means the source has no figure for that stat.
      </footer>
    </main>
  );
}

function Line({ label, l }: { label: string; l: IndexRow["current_season"] }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-wide text-slate-500 truncate">{label}</p>
      <p className="text-sm font-bold">
        {l ? `${n(l.goals)} G · ${n(l.assists)} A` : "–"}
      </p>
      <p className="text-[10px] text-slate-500">{l ? `${n(l.appearances)} apps` : ""}</p>
    </div>
  );
}
