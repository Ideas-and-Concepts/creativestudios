import { NextResponse } from "next/server";
import { count, eq, sql } from "drizzle-orm";

import { getDb } from "@/db";
import {
  architectureWorks,
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
    const [
      projectsCount,
      drawingsCount,
      boqCount,
      activeWorksCount,
      boqValue,
      architectureProgress,
      engineeringProgress,
      mepProgress,
      constructionProgress,
      projectProgressRows,
    ] = await Promise.all([
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
      db.select({ value: sql<number | null>`avg(${architectureWorks.progress})` }).from(architectureWorks),
      db.select({ value: sql<number | null>`avg(${engineeringWorks.progress})` }).from(engineeringWorks),
      db.select({ value: sql<number | null>`avg(${mepWorks.progress})` }).from(mepWorks),
      db.select({ value: sql<number | null>`avg(${constructionActivities.progress})` }).from(constructionActivities),
      db.select({
        projectId: projects.id,
        progress: sql<number | null>`avg(${constructionActivities.progress})`,
        activityCount: count(constructionActivities.id),
      })
        .from(projects)
        .leftJoin(constructionActivities, eq(constructionActivities.projectId, projects.id))
        .groupBy(projects.id),
    ]);

    const optionalProgress = (value: unknown) => {
      const numeric = Number(value);
      return Number.isFinite(numeric) ? numeric : null;
    };

    const domainProgress = {
      architecture: optionalProgress(architectureProgress[0]?.value),
      engineering: optionalProgress(engineeringProgress[0]?.value),
      mep: optionalProgress(mepProgress[0]?.value),
      construction: optionalProgress(constructionProgress[0]?.value),
    };

    const domainValues = Object.values(domainProgress).filter((value): value is number => value !== null);
    const averageProgress = domainValues.length
      ? Math.round(domainValues.reduce((sum, value) => sum + value, 0) / domainValues.length)
      : 0;

    return NextResponse.json({
      data: {
        projects: Number(projectsCount[0]?.value ?? 0),
        drawings: Number(drawingsCount[0]?.value ?? 0),
        boqItems: Number(boqCount[0]?.value ?? 0),
        activeWorks: Number(activeWorksCount.value ?? 0),
        boqValue: Number(boqValue[0]?.value ?? 0),
        averageProgress,
        domainProgress,
        projectProgress: projectProgressRows.map((row) => ({
          projectId: row.projectId,
          progress: row.progress == null ? 0 : Math.max(0, Math.min(100, Math.round(Number(row.progress)))),
          activityCount: Number(row.activityCount ?? 0),
        })),
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
