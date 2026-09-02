import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function GET() {
  return NextResponse.json({
    ok: true,
    service: "creative-studios",
    database: Boolean(process.env.DATABASE_URL),
    timestamp: new Date().toISOString(),
  });
}
