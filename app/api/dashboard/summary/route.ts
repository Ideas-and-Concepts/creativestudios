import { NextResponse } from "next/server";
import { count, eq } from "drizzle-orm";

import { getDb } from "@/db";
import {
  boqItems,
  constructionActivities,
  drawings,
  engineeringWorks,
  mepWorks,
  projects,
} from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const db = getDb();
    const [projectsCount, drawingsCount, boqCount, activeWorksCount] = await Promise.all([
      db.select({ value: count() }).from(projects),
      db.select({ value: count() }).from(drawings),
      db.select({ value: count() }).from(boqItems),
      Promise.all([
        db.select({ value: count() }).from(engineeringWorks).where(eq(engineeringWorks.status, "in_progress")),
        db.select({ value: count() }).from(mepWorks).where(eq(mepWorks.status, "in_progress")),
        db.select({ value: count() }).from(constructionActivities).where(eq(constructionActivities.status, "in_progress")),
      ]).then(([engineering, mep, construction]) => ({
        value: engineering[0]?.value + mep[0]?.value + construction[0]?.value,
      })),
    ]);

    return NextResponse.json({
      data: {
        projects: Number(projectsCount[0]?.value ?? 0),
        drawings: Number(drawingsCount[0]?.value ?? 0),
        boqItems: Number(boqCount[0]?.value ?? 0),
        activeWorks: Number(activeWorksCount.value ?? 0),
      },
    });
  } catch (error) {
    console.error("GET /api/dashboard/summary failed", error);
    return NextResponse.json(
      { error: "Dashboard data is unavailable." },
      { status: 503 },
    );
  }
}
