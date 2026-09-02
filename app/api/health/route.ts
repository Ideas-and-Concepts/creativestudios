import { NextResponse } from "next/server";

import { getDb } from "@/db";
import { projects } from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  if (!process.env.DATABASE_URL) {
    return NextResponse.json({ ok: false, service: "creative-studios", database: false, databaseConfigured: false, timestamp: new Date().toISOString() }, { status: 503 });
  }

  try {
    await getDb().select({ id: projects.id }).from(projects).limit(1);
    return NextResponse.json({ ok: true, service: "creative-studios", database: true, databaseConfigured: true, timestamp: new Date().toISOString() });
  } catch (error) {
    console.error("Creative Studios health check failed:", error);
    return NextResponse.json({ ok: false, service: "creative-studios", database: false, databaseConfigured: true, timestamp: new Date().toISOString() }, { status: 503 });
  }
}
