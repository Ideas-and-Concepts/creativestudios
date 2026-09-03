import { NextRequest, NextResponse } from "next/server";
import { and, eq, sql } from "drizzle-orm";

import { getDb } from "@/db";
import { boqItems, constructionActivities, costControl, projects } from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const n = (value: unknown) => {
  const valueAsNumber = Number(value ?? 0);
  return Number.isFinite(valueAsNumber) ? valueAsNumber : 0;
};

const round = (value: number, decimals = 2) => {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
};

function unavailable() {
  return NextResponse.json({ error: "Database is not configured." }, { status: 503 });
}

function plannedValueAt(activity: { amount: number; plannedStart: Date | null; plannedEnd: Date | null }, asOf: Date) {
  const start = activity.plannedStart?.getTime() ?? NaN;
  const end = activity.plannedEnd?.getTime() ?? NaN;
  const value = n(activity.amount);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start || value <= 0) return 0;
  if (asOf.getTime() <= start) return 0;
  if (asOf.getTime() >= end) return value;
  return value * ((asOf.getTime() - start) / (end - start));
}

export async function GET(request: NextRequest) {
  if (!process.env.DATABASE_URL) return unavailable();

  try {
    const projectId = request.nextUrl.searchParams.get("projectId");
    if (!projectId) return NextResponse.json({ error: "projectId is required." }, { status: 400 });

    const asOfParam = request.nextUrl.searchParams.get("asOf");
    const asOf = asOfParam ? new Date(asOfParam) : new Date();
    if (Number.isNaN(asOf.getTime())) return NextResponse.json({ error: "asOf must be a valid date." }, { status: 400 });

    const db = getDb();
    const [project] = await db.select({ id: projects.id, code: projects.code, name: projects.name })
      .from(projects).where(eq(projects.id, projectId)).limit(1);
    if (!project) return NextResponse.json({ error: "Project not found." }, { status: 404 });

    const [budgetRows, actualRows, activityRows] = await Promise.all([
      db.select({ total: sql<string>`coalesce(sum(${boqItems.amount}), 0)` })
        .from(boqItems).where(eq(boqItems.projectId, projectId)),
      db.select({ total: sql<string>`coalesce(sum(${costControl.amount}), 0)` })
        .from(costControl).where(and(eq(costControl.projectId, projectId), eq(costControl.costType, "Actual Cost"))),
      db.select({
        amount: sql<string>`coalesce(${boqItems.amount}, 0)`,
        progress: constructionActivities.progress,
        plannedStart: constructionActivities.plannedStart,
        plannedEnd: constructionActivities.plannedEnd,
      })
        .from(constructionActivities)
        .leftJoin(boqItems, eq(constructionActivities.boqItemId, boqItems.id))
        .where(eq(constructionActivities.projectId, projectId)),
    ]);

    const bac = n(budgetRows[0]?.total);
    const ac = n(actualRows[0]?.total);
    const activities = activityRows.map((row) => ({
      amount: n(row.amount),
      progress: Math.min(100, Math.max(0, n(row.progress))),
      plannedStart: row.plannedStart,
      plannedEnd: row.plannedEnd,
    }));

    const pv = activities.reduce((sum, activity) => sum + plannedValueAt(activity, asOf), 0);
    const ev = activities.reduce((sum, activity) => sum + activity.amount * (activity.progress / 100), 0);
    const cv = ev - ac;
    const sv = ev - pv;
    const cpi = ac > 0 ? ev / ac : null;
    const spi = pv > 0 ? ev / pv : null;
    const eac = cpi && cpi > 0 ? bac / cpi : bac;
    const etc = Math.max(0, eac - ac);
    const vac = bac - eac;
    const physicalProgress = bac > 0 ? (ev / bac) * 100 : 0;
    const financialProgress = bac > 0 ? (ac / bac) * 100 : 0;
    const baselineCoverage = activities.filter((activity) => activity.amount > 0 && activity.plannedStart && activity.plannedEnd).length;

    return NextResponse.json({
      data: {
        project,
        asOf: asOf.toISOString(),
        bac: round(bac),
        pv: round(pv),
        ev: round(ev),
        ac: round(ac),
        cv: round(cv),
        sv: round(sv),
        cpi: cpi === null ? null : round(cpi, 3),
        spi: spi === null ? null : round(spi, 3),
        eac: round(eac),
        etc: round(etc),
        vac: round(vac),
        physicalProgress: round(Math.min(100, Math.max(0, physicalProgress)), 1),
        financialProgress: round(Math.min(100, Math.max(0, financialProgress)), 1),
        baselineCoverage,
        activitiesCount: activities.length,
      },
    });
  } catch (error) {
    console.error("Earned value GET failed:", error);
    return NextResponse.json({ error: "Unable to calculate earned value metrics." }, { status: 500 });
  }
}
