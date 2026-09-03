import { getDb } from "@/db";
import { auditLogs, notifications } from "@/db/workflow";

export type WorkflowEvent = {
  projectId?: string | null;
  actor?: string | null;
  action: string;
  entityType: string;
  entityId?: string | null;
  entityLabel?: string | null;
  details?: string | null;
  metadata?: Record<string, unknown> | null;
  notification?: {
    title: string;
    message: string;
    recipient?: string | null;
    type?: string;
    severity?: string;
    actionUrl?: string | null;
  } | null;
};

export async function recordWorkflowEvent(event: WorkflowEvent) {
  const db = getDb();
  await db.insert(auditLogs).values({
    projectId: event.projectId ?? null,
    actor: event.actor ?? null,
    action: event.action,
    entityType: event.entityType,
    entityId: event.entityId ?? null,
    entityLabel: event.entityLabel ?? null,
    details: event.details ?? null,
    metadata: event.metadata ? JSON.stringify(event.metadata) : null,
  });

  if (event.notification) {
    await db.insert(notifications).values({
      projectId: event.projectId ?? null,
      title: event.notification.title,
      message: event.notification.message,
      recipient: event.notification.recipient ?? null,
      type: event.notification.type ?? "workflow",
      severity: event.notification.severity ?? "normal",
      sourceType: event.entityType,
      sourceId: event.entityId ?? null,
      actionUrl: event.notification.actionUrl ?? null,
      isRead: false,
    });
  }
}

export function workflowActor(values: Record<string, unknown>, fallback = "System") {
  return String(values.actor ?? values.updatedBy ?? values.requestedBy ?? values.raisedBy ?? fallback).trim() || fallback;
}
