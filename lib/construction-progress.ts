import { eq, sql } from "drizzle-orm";
import { getDb } from "@/db";
import { constructionActivities, siteProgressLogs } from "@/db/schema";

/** Rebuild activity execution totals from daily site progress logs. */
export async function recalculateActivityProgress(activityId: string) {
  const db = getDb();
  const [activity] = await db.select({
    id: constructionActivities.id,
    plannedQuantity: constructionActivities.plannedQuantity,
    status: constructionActivities.status,
    actualStart: constructionActivities.actualStart,
    actualEnd: constructionActivities.actualEnd,
  }).from(constructionActivities).where(eq(constructionActivities.id, activityId));
  if (!activity) throw new Error("Construction activity not found.");

  const [aggregate] = await db.select({
    actualQuantity: sql<string>`coalesce(sum(${siteProgressLogs.quantityCompleted}), 0)`,
    firstLogDate: sql<Date | null>`min(${siteProgressLogs.logDate})`,
    lastLogDate: sql<Date | null>`max(${siteProgressLogs.logDate})`,
  }).from(siteProgressLogs).where(eq(siteProgressLogs.activityId, activityId));

  const actualQuantity = Number(aggregate?.actualQuantity ?? 0);
  const plannedQuantity = Number(activity.plannedQuantity ?? 0);
  const progress = Math.max(0, Math.min(100, plannedQuantity > 0 ? Math.round((actualQuantity / plannedQuantity) * 100) : 0));
  const completed = plannedQuantity > 0 ? actualQuantity >= plannedQuantity : actualQuantity > 0;
  const status = activity.status === "on_hold" ? "on_hold" : completed ? "completed" : actualQuantity > 0 ? "in_progress" : "planned";
  const actualStart = activity.actualStart ?? aggregate?.firstLogDate ?? null;
  const actualEnd = completed ? (activity.actualEnd ?? aggregate?.lastLogDate ?? new Date()) : null;

  const [updated] = await db.update(constructionActivities).set({
    actualQuantity: String(actualQuantity), progress, status, actualStart, actualEnd, updatedAt: new Date(),
  }).where(eq(constructionActivities.id, activityId)).returning();
  return updated;
}
