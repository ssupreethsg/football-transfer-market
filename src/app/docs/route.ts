import { NextResponse } from "next/server";

export async function GET() {
  const backendBase = process.env.BACKEND_URL;
  if (backendBase) {
    try {
      const res = await fetch(`${backendBase}/docs`, { cache: "no-store" });
      if (res.ok) {
        const html = await res.text();
        return new NextResponse(html, {
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });
      }
    } catch {
      // Fallback
    }
  }

  return new NextResponse(
    `<!DOCTYPE html><html><head><title>API Docs</title></head><body style="font-family:sans-serif;padding:2rem;background:#0f172a;color:#f8fafc">
    <h1>Football Transfer Analytics API</h1>
    <p>Endpoints available:</p>
    <ul>
      <li><a style="color:#38bdf8" href="/api/players">/api/players</a> (query params: league, team, position, search, min_value, max_value, has_release_clause, skip, limit)</li>
      <li><a style="color:#38bdf8" href="/api/stats/summary">/api/stats/summary</a></li>
    </ul>
    </body></html>`,
    {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    }
  );
}

