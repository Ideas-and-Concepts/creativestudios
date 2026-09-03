import { NextResponse } from "next/server";
import { count, eq, sql } from "drizzle-orm";

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
    const [projectsCount, drawingsCount, boqCount, activeWorksCount, boqValue, progressRows] = await Promise.all([
      db.select({ value: count() }).from(projects),
      db.select({ value: count() }).from(drawings),
      db.select({ value: count() }).from(boqItems),
      Promise.all([
        db.select({ value: count() }).from(engineeringWorks).where(eq(engineeringWorks.status, "in_progress")),
        db.select({ value: count() }).from(mepWorks).where(eq(mepWorks.status, "in_progress")),
        db.select({ value: count() }).from(constructionActivities).where(eq(constructionActivities.status, "in_progress")),
      ]).then(([engineering, mep, construction]) => ({
        value: Number(engineering[0]?.value ?? 0) + Number(mep[0]?.value ?? 0) + Number(construction[0]?.value ?? 0),
      })),
      db.select({ value: sql<string>`coalesce(sum(${boqItems.amount}), 0)` }).from(boqItems),
      Promise.all([
        db.select({ value: sql<number>`coalesce(avg(${engineeringWorks.progress}), 0)` }).from(engineeringWorks),
        db.select({ value: sql<number>`coalesce(avg(${mepWorks.progress}), 0)` }).from(mepWorks),
        db.select({ value: sql<number>`coalesce(avg(${constructionActivities.progress}), 0)` }).from(constructionActivities),
      ]),
    ]);

    const progressValues = progressRows.map((row) => Number(row[0]?.value ?? 0)).filter((value) => Number.isFinite(value));
    const averageProgress = progressValues.length
      ? Math.round(progressValues.reduce((sum, value) => sum + value, 0) / progressValues.length)
      : 0;

    return NextResponse.json({
      data: {
        projects: Number(projectsCount[0]?.value ?? 0),
        drawings: Number(drawingsCount[0]?.value ?? 0),
        boqItems: Number(boqCount[0]?.value ?? 0),
        activeWorks: Number(activeWorksCount.value ?? 0),
        boqValue: Number(boqValue[0]?.value ?? 0),
        averageProgress,
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
