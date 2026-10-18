import { NextResponse } from "next/server";

export async function GET() {
  const backendBase = process.env.BACKEND_URL;
  if (backendBase) {
    try {
      const res = await fetch(`${backendBase}/openapi.json`, { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        return NextResponse.json(data);
      }
    } catch {
      // Fallback
    }
  }

  return NextResponse.json({
    openapi: "3.1.0",
    info: {
      title: "Football Transfer Analytics API",
      version: "2.3.0",
      description: "Standalone Vercel Deployment & Backend API"
    },
    paths: {
      "/api/players": { get: { summary: "List players with filters" } },
      "/api/stats/summary": { get: { summary: "Database summary metrics" } }
    }
  });
}

