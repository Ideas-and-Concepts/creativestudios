import { boolean, index, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";
import { projects } from "./schema";

export const notifications = pgTable("notifications", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  message: text("message").notNull(),
  type: text("type").default("info").notNull(),
  severity: text("severity").default("normal").notNull(),
  recipient: text("recipient"),
  sourceType: text("source_type"),
  sourceId: text("source_id"),
  actionUrl: text("action_url"),
  isRead: boolean("is_read").default(false).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  readAt: timestamp("read_at", { withTimezone: true }),
}, (table) => ({
  projectIdx: index("notifications_project_idx").on(table.projectId),
  recipientIdx: index("notifications_recipient_idx").on(table.recipient),
  readIdx: index("notifications_read_idx").on(table.isRead),
  createdIdx: index("notifications_created_idx").on(table.createdAt),
}));

export const auditLogs = pgTable("audit_logs", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }),
  actor: text("actor"),
  action: text("action").notNull(),
  entityType: text("entity_type").notNull(),
  entityId: text("entity_id"),
  entityLabel: text("entity_label"),
  details: text("details"),
  metadata: text("metadata"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => ({
  projectIdx: index("audit_logs_project_idx").on(table.projectId),
  entityIdx: index("audit_logs_entity_idx").on(table.entityType, table.entityId),
  createdIdx: index("audit_logs_created_idx").on(table.createdAt),
}));
