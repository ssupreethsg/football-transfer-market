"use client";

import Link from "next/link";
import { Fragment, useEffect, useState } from "react";
import type { Basic, CompType, Detailed, PlayerFile, Season } from "@/lib/types";
import {
  COMP_LOGO, COMP_TYPE_LABEL, COMP_TYPE_ORDER, DETAIL_GROUPS, PLAYER_IMG, TEAM_LOGO, dash, money, n,
} from "@/lib/format";

type Row = Basic & {
  key: string;
  label: string;
  sub?: string;
  notes?: string[];
  competition_id?: number;
  type?: CompType;
  rating?: number | null;
  detailed: Detailed | null;
};

export default function PlayerView({ id }: { id: string }) {
  const [p, setP] = useState<PlayerFile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"career" | "seasons">("career");
  const validId = /^\d+$/.test(id);

  useEffect(() => {
    if (!validId) return;
    fetch(`/data/players/${id}.json`)
      .then((r) => {
        if (!r.ok) throw new Error("Player not found.");
        return r.json();
      })
      .then(setP)
      .catch((e) => setError(String(e.message || e)));
  }, [id, validId]);

  if (!validId) return <Shell><p className="text-red-400">Player not found.</p></Shell>;
  if (error) return <Shell><p className="text-red-400">{error}</p></Shell>;
  if (!p) return <Shell><p className="text-slate-500">Loading…</p></Shell>;

  const ct = p.career_totals;
  return (
    <Shell>
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={PLAYER_IMG(p.id)} alt="" className="w-24 h-24 rounded-full bg-slate-800 object-cover" />
        <div className="min-w-0">
          <h1 className="text-3xl font-black">{p.name}</h1>
          <p className="text-slate-300 flex items-center gap-2 mt-1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={TEAM_LOGO(p.team_id)} alt="" className="w-5 h-5" />
            {p.team} · {p.league}{p.on_loan ? " (on loan)" : ""}
          </p>
          <p className="text-sm text-slate-400 mt-1">
            {[p.position, p.nationality, p.age && `${p.age} yrs`, p.height_cm && `${p.height_cm} cm`,
              p.preferred_foot && `${p.preferred_foot} foot`, p.contract_end && `contract to ${p.contract_end.slice(0, 4)}`]
              .filter(Boolean).join(" · ")}
          </p>
        </div>
        <div className="sm:ml-auto text-left sm:text-right">
          <p className="text-[11px] uppercase tracking-wide text-slate-500">Market value</p>
          <p className="text-2xl font-black text-emerald-400">{money(p.market_value?.value_eur)}</p>
          {p.market_value && <p className="text-[11px] text-slate-500">{p.market_value.source}, {p.market_value.date}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
        <Kpi label="Career appearances" value={n(ct.appearances)} note={ct.incomplete?.includes("appearances")} />
        <Kpi label="Career goals" value={n(ct.goals)} note={ct.incomplete?.includes("goals")} />
        <Kpi label="Career assists" value={n(ct.assists)} note={ct.incomplete?.includes("assists")} />
        <Kpi label={`Minutes (${ct.detailed_seasons.at(-1) ?? ""}–now)`} value={n(ct.detailed?.minutes)} />
      </div>

      <div className="flex gap-2 mt-8 mb-4">
        {([["career", "Career (cumulative)"], ["seasons", "Season by season"]] as const).map(([k, label]) => (
          <button key={k} onClick={() => setTab(k)}
            className={`px-4 py-2 rounded-full text-sm font-semibold border cursor-pointer ${tab === k
              ? "bg-emerald-500 text-slate-950 border-emerald-500" : "border-slate-700 text-slate-300 hover:border-emerald-500/60"}`}>
            {label}
          </button>
        ))}
      </div>

      {tab === "career" ? <Career p={p} /> : <Seasons p={p} />}

      <p className="text-xs text-slate-500 mt-10">
        Source: <a className="underline" href={p.source.url} target="_blank" rel="noreferrer">{p.source.provider}</a>.
        Appearances, goals and assists cover the whole career. Detailed stats (minutes, xG, dribbles, tackles…) are
        available for {ct.detailed_seasons.join(", ") || "no seasons"}. &ldquo;{dash}&rdquo; = not available from the source;
        &ldquo;*&rdquo; = total includes competitions where the source has no figure. Friendlies are excluded.
      </p>
    </Shell>
  );
}

function Career({ p }: { p: PlayerFile }) {
  const ct = p.career_totals;
  const rows: Row[] = p.career_by_competition.map((c) => ({
    ...c, key: `${c.competition_id}-${c.type}`, label: c.competition,
    sub: `${c.seasons} season${c.seasons === 1 ? "" : "s"}`,
  }));
  const since = ct.detailed_seasons.at(-1);
  return (
    <>
      <p className="text-xs text-slate-400 mb-3">
        Apps, goals and assists: whole career.{" "}
        {since
          ? <>Minutes, xG, xA, shots, dribbles, chances, tackles and rating: {since} onwards only.</>
          : <>No detailed stats are available for this player.</>}
        {p.position_group === "keepers" && " The source does not publish minutes for goalkeepers."}
      </p>
      <StatTable
        rows={rows}
        total={{ ...ct, key: "total", label: "All competitions", rating: ct.detailed?.rating ?? null, detailed: ct.detailed }}
        grouped
      />
    </>
  );
}

function Seasons({ p }: { p: PlayerFile }) {
  const [open, setOpen] = useState<string>(p.seasons[0]?.season ?? "");
  return (
    <div className="space-y-3">
      {p.seasons.map((s) => (
        <div key={s.season} className="border border-slate-800 rounded-2xl overflow-hidden">
          <button onClick={() => setOpen(open === s.season ? "" : s.season)}
            className="w-full flex flex-wrap items-center gap-x-4 gap-y-1 px-4 py-3 bg-slate-900/70 hover:bg-slate-900 text-left cursor-pointer">
            <span className="font-black text-lg w-24">{s.season}</span>
            <span className="text-sm text-slate-400 flex-1 min-w-40">{s.teams.join(" · ")}</span>
            <span className="text-sm">
              <b>{n(s.totals.appearances)}</b> apps · <b>{n(s.totals.goals)}</b> G · <b>{n(s.totals.assists)}</b> A
              {s.totals.incomplete?.length ? "*" : ""}
              {s.totals_detailed?.minutes != null && <span className="text-slate-400"> · {n(s.totals_detailed.minutes)} min</span>}
            </span>
            <span className="text-slate-500">{open === s.season ? "▲" : "▼"}</span>
          </button>
          {open === s.season && <div className="p-3"><SeasonTable s={s} /></div>}
        </div>
      ))}
    </div>
  );
}

function SeasonTable({ s }: { s: Season }) {
  const rows: Row[] = s.competitions.map((c, i) => ({
    ...c, key: `${c.competition_id}-${c.team}-${i}`, label: c.competition,
    sub: c.by_team
      ? c.by_team.map((t) => `${t.team}: ${n(t.appearances)} apps, ${n(t.goals)} G, ${n(t.assists)} A`).join(" · ")
      : s.teams.length > 1 ? c.team : c.edition !== s.season ? c.edition : undefined,
  }));
  return (
    <StatTable rows={rows} total={{
      ...s.totals, key: "total", label: `${s.season} total`,
      rating: s.totals_detailed?.rating ?? null, detailed: s.totals_detailed,
    }} />
  );
}

function StatTable({ rows, total, grouped }: { rows: Row[]; total: Row; grouped?: boolean }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const cols: [string, (r: Row) => string][] = [
    ["Apps", (r) => n(r.appearances)],
    ["Min", (r) => n(r.detailed?.minutes)],
    ["Goals", (r) => n(r.goals) + (r.incomplete?.includes("goals") ? "*" : "")],
    ["Assists", (r) => n(r.assists) + (r.incomplete?.includes("assists") ? "*" : "")],
    ["xG", (r) => n(r.detailed?.xg, 1)],
    ["xA", (r) => n(r.detailed?.xa, 1)],
    ["Shots", (r) => n(r.detailed?.shots)],
    ["Dribbles", (r) => n(r.detailed?.dribbles)],
    ["Chances", (r) => n(r.detailed?.chances_created)],
    ["Tackles", (r) => n(r.detailed?.tackles)],
    ["Rating", (r) => n(r.rating ?? r.detailed?.rating, 2)],
  ];
  const groups = grouped
    ? COMP_TYPE_ORDER.map((t) => [t, rows.filter((r) => r.type === t)] as const).filter(([, rs]) => rs.length)
    : [[null, rows] as const];

  const line = (r: Row, strong = false) => (
    <Fragment key={r.key}>
      <tr onClick={() => r.detailed && setExpanded(expanded === r.key ? null : r.key)}
        className={`border-t border-slate-800 ${r.detailed ? "cursor-pointer hover:bg-slate-900" : ""} ${strong ? "bg-slate-900/80 font-bold" : ""}`}>
        <td className="py-2 pr-3 pl-2 sticky left-0 bg-slate-950">
          <div className="flex items-center gap-2 min-w-44">
            {r.competition_id != null && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={COMP_LOGO(r.competition_id)} alt="" loading="lazy" className="w-5 h-5 object-contain" />
            )}
            <div>
              <div>{r.label} {r.detailed && <span className="text-slate-500 text-xs">{expanded === r.key ? "▲" : "▼"}</span>}</div>
              {r.sub && <div className="text-[11px] text-slate-500 font-normal">{r.sub}</div>}
              {r.notes?.map((t) => <div key={t} className="text-[11px] text-amber-400/80 font-normal">ⓘ {t}</div>)}
            </div>
          </div>
        </td>
        {cols.map(([h, f]) => <td key={h} className="py-2 px-2 text-right tabular-nums">{f(r)}</td>)}
      </tr>
      {expanded === r.key && r.detailed && (
        <tr className="bg-slate-900/50"><td colSpan={cols.length + 1} className="p-3"><DetailGrid d={r.detailed} /></td></tr>
      )}
    </Fragment>
  );

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[11px] uppercase tracking-wide text-slate-500">
            <th className="text-left py-2 pl-2 sticky left-0 bg-slate-950">Competition</th>
            {cols.map(([h]) => <th key={h} className="text-right py-2 px-2">{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {groups.map(([t, rs]) => (
            <Fragment key={t ?? "all"}>
              {t && (
                <tr><td colSpan={cols.length + 1} className="pt-4 pb-1 pl-2 text-xs font-bold text-emerald-400 uppercase tracking-wide">
                  {COMP_TYPE_LABEL[t]}
                </td></tr>
              )}
              {rs.map((r) => line(r))}
            </Fragment>
          ))}
          {line(total, true)}
        </tbody>
      </table>
      <p className="text-[11px] text-slate-500 mt-2">Click a row with ▼ to see every detailed stat for it.</p>
    </div>
  );
}

function DetailGrid({ d }: { d: Detailed }) {
  const groups = DETAIL_GROUPS.map((g) => ({ ...g, fields: g.fields.filter(([k]) => d[k] != null) }))
    .filter((g) => g.fields.length);
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {groups.map((g) => (
        <div key={g.title}>
          <p className="text-xs font-bold text-emerald-400 uppercase tracking-wide mb-1">{g.title}</p>
          {g.fields.map(([k, label, digits]) => (
            <div key={k} className="flex justify-between text-xs py-0.5 border-b border-slate-800/60">
              <span className="text-slate-400">{label}</span>
              <span className="tabular-nums">{n(d[k], digits ?? 0)}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function Kpi({ label, value, note }: { label: string; value: string; note?: boolean }) {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4">
      <p className="text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="text-2xl font-black mt-1">{value}{note ? "*" : ""}</p>
    </div>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
        <Link href="/" className="text-sm text-emerald-400 hover:underline">← All players</Link>
        <div className="mt-6">{children}</div>
      </div>
    </main>
  );
}
