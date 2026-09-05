import { NextRequest, NextResponse } from "next/server";
import { and, eq, sql } from "drizzle-orm";

import { getDb } from "@/db";
import { boqItems, constructionActivities, costControl, projects, siteProgressLogs } from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const n = (value: unknown) => {
  const valueAsNumber = Number(value ?? 0);
  return Number.isFinite(valueAsNumber) ? valueAsNumber : 0;
};

const clamp = (value: number, low = 0, high = 100) => Math.max(low, Math.min(high, value));
const round = (value: number, decimals = 2) => {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
};

function unavailable() {
  return NextResponse.json({ error: "Database is not configured." }, { status: 503 });
}

function plannedValueAt(amount: number, start: Date | null, end: Date | null, asOf: Date) {
  if (amount <= 0 || !start || !end || end.getTime() <= start.getTime()) return 0;
  if (asOf.getTime() <= start.getTime()) return 0;
  if (asOf.getTime() >= end.getTime()) return amount;
  return amount * ((asOf.getTime() - start.getTime()) / (end.getTime() - start.getTime()));
}

function progressFromQuantity(plannedQuantity: number, actualQuantity: number) {
  return plannedQuantity > 0 && actualQuantity > 0 ? clamp((actualQuantity / plannedQuantity) * 100) : null;
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

    const [boqRows, actualRows, activityRows, logRows] = await Promise.all([
      db.select({ id: boqItems.id, itemCode: boqItems.itemCode, amount: boqItems.amount })
        .from(boqItems).where(eq(boqItems.projectId, projectId)),
      db.select({ total: sql<string>`coalesce(sum(${costControl.amount}), 0)` })
        .from(costControl)
        .where(and(eq(costControl.projectId, projectId), eq(costControl.costType, "Actual Cost"))),
      db.select({
        id: constructionActivities.id,
        boqItemId: constructionActivities.boqItemId,
        amount: sql<string>`coalesce(${boqItems.amount}, 0)`,
        progress: constructionActivities.progress,
        plannedQuantity: constructionActivities.plannedQuantity,
        actualQuantity: constructionActivities.actualQuantity,
        unit: constructionActivities.unit,
        plannedStart: constructionActivities.plannedStart,
        plannedEnd: constructionActivities.plannedEnd,
      })
        .from(constructionActivities)
        .leftJoin(boqItems, eq(constructionActivities.boqItemId, boqItems.id))
        .where(eq(constructionActivities.projectId, projectId)),
      db.select({
        activityId: siteProgressLogs.activityId,
        quantityCompleted: siteProgressLogs.quantityCompleted,
        unit: siteProgressLogs.unit,
      })
        .from(siteProgressLogs)
        .where(eq(siteProgressLogs.projectId, projectId)),
    ]);

    const logsByActivity = new Map<string, { quantity: number; units: Set<string> }>();
    for (const log of logRows) {
      const key = String(log.activityId);
      const current = logsByActivity.get(key) ?? { quantity: 0, units: new Set<string>() };
      current.quantity += n(log.quantityCompleted);
      const unit = String(log.unit ?? "").trim().toLowerCase();
      if (unit) current.units.add(unit);
      logsByActivity.set(key, current);
    }

    const boqById = new Map(boqRows.map((row) => [row.id, n(row.amount)]));
    const grouped = new Map<string, {
      amount: number;
      progress: number;
      start: Date | null;
      end: Date | null;
    }>();

    for (const activity of activityRows) {
      const amount = activity.boqItemId ? (boqById.get(activity.boqItemId) ?? n(activity.amount)) : 0;
      if (amount <= 0 || !activity.boqItemId) continue;

      let progress = clamp(n(activity.progress));
      const plannedQuantity = n(activity.plannedQuantity);
      const actualQuantity = n(activity.actualQuantity);
      const log = logsByActivity.get(String(activity.id));
      const activityUnit = String(activity.unit ?? "").trim().toLowerCase();
      const logUnitsMatch = !log || !activityUnit || [...log.units].every((unit) => unit === activityUnit);
      const loggedQuantity = log && logUnitsMatch ? log.quantity : 0;
      const quantityProgress = progressFromQuantity(plannedQuantity, Math.max(actualQuantity, loggedQuantity));
      if (quantityProgress !== null) progress = Math.max(progress, quantityProgress);

      const current = grouped.get(String(activity.boqItemId));
      if (!current) {
        grouped.set(String(activity.boqItemId), {
          amount,
          progress,
          start: activity.plannedStart,
          end: activity.plannedEnd,
        });
      } else {
        current.progress = Math.max(current.progress, progress);
        if (activity.plannedStart && (!current.start || activity.plannedStart < current.start)) current.start = activity.plannedStart;
        if (activity.plannedEnd && (!current.end || activity.plannedEnd > current.end)) current.end = activity.plannedEnd;
      }
    }

    const baselines = [...grouped.values()];
    const bac = boqRows.reduce((sum, row) => sum + n(row.amount), 0);
    const ac = n(actualRows[0]?.total);
    const pv = baselines.reduce((sum, row) => sum + plannedValueAt(row.amount, row.start, row.end, asOf), 0);
    const ev = baselines.reduce((sum, row) => sum + row.amount * row.progress / 100, 0);
    const cv = ev - ac;
    const sv = ev - pv;
    const cpi = ac > 0 ? ev / ac : null;
    const spi = pv > 0 ? ev / pv : null;
    const eac = cpi && cpi > 0 ? bac / cpi : bac;
    const etc = Math.max(0, eac - ac);
    const vac = bac - eac;
    const tcpiBac = bac - ac > 0 ? (bac - ev) / (bac - ac) : null;
    const tcpiEac = eac - ac > 0 ? (bac - ev) / (eac - ac) : null;
    const baselineCoverage = baselines.filter((row) => row.amount > 0 && row.start && row.end).length;

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
        tcpiBac: tcpiBac === null ? null : round(tcpiBac, 3),
        tcpiEac: tcpiEac === null ? null : round(tcpiEac, 3),
        physicalProgress: round(clamp(bac > 0 ? (ev / bac) * 100 : 0), 1),
        financialProgress: round(clamp(bac > 0 ? (ac / bac) * 100 : 0), 1),
        baselineCoverage,
        activitiesCount: activityRows.length,
        baselineItems: baselines.length,
        siteLogs: logRows.length,
      },
    });
  } catch (error) {
    console.error("Earned value GET failed:", error);
    return NextResponse.json({ error: "Unable to calculate earned value metrics." }, { status: 500 });
  }
}
