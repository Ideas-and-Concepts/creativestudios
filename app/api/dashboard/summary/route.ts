import { NextResponse } from "next/server";
import { and, count, eq, ne, sql } from "drizzle-orm";

import { getDb } from "@/db";
import {
  architectureWorks,
  boqItems,
  constructionActivities,
  costControl,
  drawings,
  engineeringWorks,
  mepWorks,
  projects,
  purchaseOrders,
} from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const numeric = (value: unknown) => {
  const n = Number(value ?? 0);
  return Number.isFinite(n) ? n : 0;
};

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
      committedCost,
      actualCost,
      earnedValue,
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
      db.select({ total: sql<string>`coalesce(sum(${purchaseOrders.totalAmount}), 0)` })
        .from(purchaseOrders)
        .where(and(ne(purchaseOrders.status, "draft"), ne(purchaseOrders.status, "cancelled"))),
      db.select({ total: sql<string>`coalesce(sum(${costControl.amount}), 0)` })
        .from(costControl)
        .where(eq(costControl.costType, "Actual Cost")),
      db.select({
        value: sql<string>`coalesce(sum(${boqItems.amount} * coalesce(${constructionActivities.progress}, 0) / 100.0), 0)`,
      })
        .from(constructionActivities)
        .innerJoin(boqItems, eq(constructionActivities.boqItemId, boqItems.id)),
    ]);

    const optionalProgress = (value: unknown) => {
      const n = Number(value);
      return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : null;
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

    const budget = numeric(boqValue[0]?.value);
    const committed = numeric(committedCost[0]?.total);
    const actual = numeric(actualCost[0]?.total);
    const ev = numeric(earnedValue[0]?.value);
    const forecast = actual > 0 && ev > 0 ? budget / (ev / actual) : Math.max(actual, committed);
    const variance = budget - forecast;
    const cpi = actual > 0 ? ev / actual : null;

    return NextResponse.json({
      data: {
        projects: Number(projectsCount[0]?.value ?? 0),
        drawings: Number(drawingsCount[0]?.value ?? 0),
        boqItems: Number(boqCount[0]?.value ?? 0),
        activeWorks: Number(activeWorksCount.value ?? 0),
        boqValue: budget,
        averageProgress,
        domainProgress,
        projectProgress: projectProgressRows.map((row) => ({
          projectId: row.projectId,
          progress: row.progress == null ? 0 : Math.max(0, Math.min(100, Math.round(Number(row.progress)))),
          activityCount: Number(row.activityCount ?? 0),
        })),
        commercial: {
          budget,
          committed,
          actual,
          earnedValue: ev,
          forecast,
          variance,
          cpi: cpi == null ? null : Math.round(cpi * 100) / 100,
          budgetUtilisation: budget > 0 ? Math.round((actual / budget) * 1000) / 10 : 0,
        },
      },
    });
  } catch (error) {
    console.error("GET /api/dashboard/summary failed", error);
    return NextResponse.json({ error: "Dashboard data is unavailable." }, { status: 503 });
  }
}
