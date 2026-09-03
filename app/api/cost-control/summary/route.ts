import { NextRequest, NextResponse } from "next/server";
import { and, eq, ne, sql } from "drizzle-orm";

import { getDb } from "@/db";
import { boqItems, constructionActivities, costControl, purchaseOrders, projects } from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function unavailable() {
  return NextResponse.json({ error: "Database is not configured." }, { status: 503 });
}

const numeric = (value: unknown) => {
  const n = Number(value ?? 0);
  return Number.isFinite(n) ? n : 0;
};

export async function GET(request: NextRequest) {
  if (!process.env.DATABASE_URL) return unavailable();

  try {
    const projectId = request.nextUrl.searchParams.get("projectId");
    if (!projectId) return NextResponse.json({ error: "projectId is required." }, { status: 400 });

    const db = getDb();
    const [project] = await db.select({ id: projects.id, code: projects.code, name: projects.name })
      .from(projects).where(eq(projects.id, projectId)).limit(1);
    if (!project) return NextResponse.json({ error: "Project not found." }, { status: 404 });

    const [budgetRows, commitmentRows, actualRows, activityRows] = await Promise.all([
      db.select({ total: sql<string>`coalesce(sum(${boqItems.amount}), 0)` })
        .from(boqItems).where(eq(boqItems.projectId, projectId)),
      db.select({ total: sql<string>`coalesce(sum(${purchaseOrders.totalAmount}), 0)` })
        .from(purchaseOrders)
        .where(and(eq(purchaseOrders.projectId, projectId), ne(purchaseOrders.status, "draft"), ne(purchaseOrders.status, "cancelled"))),
      db.select({ total: sql<string>`coalesce(sum(${costControl.amount}), 0)` })
        .from(costControl)
        .where(and(eq(costControl.projectId, projectId), eq(costControl.costType, "Actual Cost"))),
      db.select({ planned: sql<string>`coalesce(sum(${constructionActivities.plannedQuantity}), 0)`, actual: sql<string>`coalesce(sum(${constructionActivities.actualQuantity}), 0)` })
        .from(constructionActivities).where(eq(constructionActivities.projectId, projectId)),
    ]);

    const budget = numeric(budgetRows[0]?.total);
    const committed = numeric(commitmentRows[0]?.total);
    const actual = numeric(actualRows[0]?.total);
    const forecast = Math.max(actual, committed);
    const variance = budget - forecast;
    const plannedQuantity = numeric(activityRows[0]?.planned);
    const actualQuantity = numeric(activityRows[0]?.actual);
    const progress = plannedQuantity > 0 ? Math.min(100, Math.max(0, (actualQuantity / plannedQuantity) * 100)) : 0;

    return NextResponse.json({
      data: {
        project,
        budget,
        committed,
        actual,
        forecast,
        variance,
        progress: Math.round(progress * 10) / 10,
        plannedQuantity,
        actualQuantity,
        remainingBudget: Math.max(0, budget - actual),
      },
    });
  } catch (error) {
    console.error("Cost control summary GET failed:", error);
    return NextResponse.json({ error: "Unable to calculate project cost summary." }, { status: 500 });
  }
}
