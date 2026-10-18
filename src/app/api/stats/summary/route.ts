import { NextRequest, NextResponse } from "next/server";
import summaryData from "@/data/summary.json";

export async function GET(request: NextRequest) {
  const backendBase = process.env.BACKEND_URL;

  if (backendBase) {
    try {
      const res = await fetch(`${backendBase}/stats/summary`, { cache: "no-store" });
      if (res.ok) {
        return NextResponse.json(await res.json());
      }
    } catch {
      // Fallback
    }
  }

  return NextResponse.json(summaryData);
}

