import { NextRequest, NextResponse } from "next/server";
import rawPlayers from "@/data/players.json";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const backendBase = process.env.BACKEND_URL;

  if (backendBase) {
    try {
      const res = await fetch(`${backendBase}/players/${id}`, { cache: "no-store" });
      if (res.ok) {
        return NextResponse.json(await res.json());
      }
    } catch {
      // Fallback
    }
  }

  const pid = parseInt(id, 10);
  const player = (rawPlayers as any[]).find((p) => p.id === pid);
  if (!player) {
    return NextResponse.json({ detail: "Player not found" }, { status: 404 });
  }
  return NextResponse.json(player);
}

