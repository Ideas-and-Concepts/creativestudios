import { NextResponse } from "next/server";
import { and, count, eq, isNotNull, ne, sql } from "drizzle-orm";

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
  siteProgressLogs,
} from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const numeric = (value: unknown) => {
  const n = Number(value ?? 0);
  return Number.isFinite(n) ? n : 0;
};

const clampProgress = (value: unknown) => Math.max(0, Math.min(100, numeric(value)));

function commercialMetrics(budget: number, committed: number, actual: number, earnedValue: number) {
  const cpi = actual > 0 ? earnedValue / actual : null;
  const forecast = cpi && cpi > 0 ? budget / cpi : Math.max(actual, committed);
  const variance = budget - forecast;

  return {
    budget,
    committed,
    actual,
    earnedValue,
    forecast,
    variance,
    cpi: cpi == null ? null : Math.round(cpi * 100) / 100,
    budgetUtilisation: budget > 0 ? Math.round((actual / budget) * 1000) / 10 : 0,
  };
}

export async function GET() {
  try {
    const db = getDb();

    // Site quantities improve physical progress when the activity has a planned
    // quantity and the logged unit matches the activity unit. Otherwise the
    // activity's own progress remains the fallback. A BOQ item is still valued
    // only once when multiple construction activities reference it.
    const activityProgress = db
      .select({
        activityId: constructionActivities.id,
        boqItemId: constructionActivities.boqItemId,
        progress: sql<number>`least(100, greatest(0,
          greatest(
            coalesce(${constructionActivities.progress}, 0),
            case
              when coalesce(${constructionActivities.plannedQuantity}, 0) > 0
                and coalesce(${constructionActivities.unit}, '') <> ''
              then coalesce(sum(
                case when lower(trim(coalesce(${siteProgressLogs.unit}, ''))) = lower(trim(coalesce(${constructionActivities.unit}, '')))
                  then coalesce(${siteProgressLogs.quantityCompleted}, 0)
                  else 0
                end
              ), 0) / ${constructionActivities.plannedQuantity} * 100
              else 0
            end,
            case
              when coalesce(${constructionActivities.plannedQuantity}, 0) > 0
              then coalesce(${constructionActivities.actualQuantity}, 0) / ${constructionActivities.plannedQuantity} * 100
              else 0
            end
          )
        ))`.as("progress"),
      })
      .from(constructionActivities)
      .leftJoin(siteProgressLogs, eq(siteProgressLogs.activityId, constructionActivities.id))
      .where(isNotNull(constructionActivities.boqItemId))
      .groupBy(
        constructionActivities.id,
        constructionActivities.boqItemId,
        constructionActivities.progress,
        constructionActivities.plannedQuantity,
        constructionActivities.actualQuantity,
        constructionActivities.unit,
      )
      .as("activity_progress");

    const progressByBoqItem = db
      .select({
        boqItemId: activityProgress.boqItemId,
        progress: sql<number>`least(100, greatest(0, max(${activityProgress.progress})))`.as("progress"),
      })
      .from(activityProgress)
      .groupBy(activityProgress.boqItemId)
      .as("progress_by_boq_item");

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
      boqByProject,
      committedByProject,
      actualByProject,
      earnedValueByProject,
      drawingsByProject,
      activeWorksByProject,
      siteLogCount,
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
        progress: sql<number | null>`case when coalesce(sum(${constructionActivities.plannedQuantity}), 0) > 0 then least(100, greatest(0, (sum(coalesce(${constructionActivities.actualQuantity}, 0)) / sum(${constructionActivities.plannedQuantity})) * 100)) else null end`.as("progress"),
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
        value: sql<string>`coalesce(sum(${boqItems.amount} * coalesce(${progressByBoqItem.progress}, 0) / 100.0), 0)`,
      })
        .from(boqItems)
        .leftJoin(progressByBoqItem, eq(progressByBoqItem.boqItemId, boqItems.id)),
      db.select({
        projectId: boqItems.projectId,
        total: sql<string>`coalesce(sum(${boqItems.amount}), 0)`,
      }).from(boqItems).groupBy(boqItems.projectId),
      db.select({
        projectId: purchaseOrders.projectId,
        total: sql<string>`coalesce(sum(${purchaseOrders.totalAmount}), 0)`,
      })
        .from(purchaseOrders)
        .where(and(ne(purchaseOrders.status, "draft"), ne(purchaseOrders.status, "cancelled")))
        .groupBy(purchaseOrders.projectId),
      db.select({
        projectId: costControl.projectId,
        total: sql<string>`coalesce(sum(${costControl.amount}), 0)`,
      }).from(costControl).where(eq(costControl.costType, "Actual Cost")).groupBy(costControl.projectId),
      db.select({
        projectId: boqItems.projectId,
        value: sql<string>`coalesce(sum(${boqItems.amount} * coalesce(${progressByBoqItem.progress}, 0) / 100.0), 0)`,
      })
        .from(boqItems)
        .leftJoin(progressByBoqItem, eq(progressByBoqItem.boqItemId, boqItems.id))
        .groupBy(boqItems.projectId),
      db.select({ projectId: drawings.projectId, total: count() }).from(drawings).groupBy(drawings.projectId),
      db.select({ projectId: constructionActivities.projectId, total: count() })
        .from(constructionActivities)
        .where(eq(constructionActivities.status, "in_progress"))
        .groupBy(constructionActivities.projectId),
      db.select({ value: count() }).from(siteProgressLogs),
    ]);

    const optionalProgress = (value: unknown) => {
      const n = Number(value);
      return Number.isFinite(n) ? clampProgress(n) : null;
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
    const commercial = commercialMetrics(budget, committed, actual, ev);

    const budgetMap = new Map(boqByProject.map(row => [row.projectId, numeric(row.total)]));
    const committedMap = new Map(committedByProject.map(row => [row.projectId, numeric(row.total)]));
    const actualMap = new Map(actualByProject.map(row => [row.projectId, numeric(row.total)]));
    const earnedValueMap = new Map(earnedValueByProject.map(row => [row.projectId, numeric(row.value)]));
    const drawingsMap = new Map(drawingsByProject.map(row => [row.projectId, Number(row.total ?? 0)]));
    const activeWorksMap = new Map(activeWorksByProject.map(row => [row.projectId, Number(row.total ?? 0)]));

    const projectMetrics = projectProgressRows.map(row => {
      const projectId = row.projectId;
      const projectBudget = budgetMap.get(projectId) ?? 0;
      const projectActual = actualMap.get(projectId) ?? 0;
      const projectEv = earnedValueMap.get(projectId) ?? 0;
      const cpi = projectActual > 0 ? projectEv / projectActual : null;
      const eac = cpi && cpi > 0 ? projectBudget / cpi : projectBudget;
      const tcpiBac = projectBudget - projectActual > 0 ? (projectBudget - projectEv) / (projectBudget - projectActual) : null;
      const tcpiEac = eac - projectActual > 0 ? (projectBudget - projectEv) / (eac - projectActual) : null;

      return {
        projectId,
        progress: row.progress == null ? null : Math.round(clampProgress(row.progress)),
        activityCount: Number(row.activityCount ?? 0),
        drawings: drawingsMap.get(projectId) ?? 0,
        activeWorks: activeWorksMap.get(projectId) ?? 0,
        boqValue: projectBudget,
        commercial: {
          ...commercialMetrics(projectBudget, committedMap.get(projectId) ?? 0, projectActual, projectEv),
          tcpiBac: tcpiBac == null ? null : Math.round(tcpiBac * 1000) / 1000,
          tcpiEac: tcpiEac == null ? null : Math.round(tcpiEac * 1000) / 1000,
        },
      };
    });

    return NextResponse.json({
      data: {
        projects: Number(projectsCount[0]?.value ?? 0),
        drawings: Number(drawingsCount[0]?.value ?? 0),
        boqItems: Number(boqCount[0]?.value ?? 0),
        activeWorks: Number(activeWorksCount.value ?? 0),
        siteProgressLogs: Number(siteLogCount[0]?.value ?? 0),
        boqValue: budget,
        averageProgress,
        domainProgress,
        projectProgress: projectProgressRows.map((row) => ({
          projectId: row.projectId,
          progress: row.progress == null ? 0 : Math.round(clampProgress(row.progress)),
          activityCount: Number(row.activityCount ?? 0),
        })),
        projectMetrics,
        commercial,
        commercialByProject: projectMetrics.map(row => ({ projectId: row.projectId, ...row.commercial })),
      },
    });
  } catch (error) {
    console.error("GET /api/dashboard/summary failed", error);
    return NextResponse.json({ error: "Dashboard data is unavailable." }, { status: 503 });
  }
}
