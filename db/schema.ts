import {
  boolean,
  decimal,
  integer,
  pgEnum,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core";

export const projectStatus = pgEnum("project_status", [
  "planning",
  "active",
  "on_hold",
  "completed",
  "cancelled",
]);

export const workStatus = pgEnum("work_status", [
  "planned",
  "in_progress",
  "completed",
  "on_hold",
]);

export const drawingDiscipline = pgEnum("drawing_discipline", [
  "architectural",
  "structural",
]);

export const mepDiscipline = pgEnum("mep_discipline", [
  "mechanical",
  "electrical",
  "plumbing",
  "fire_protection",
  "hvac",
  "public_health",
  "other",
]);

export const projects = pgTable("projects", {
  id: uuid("id").defaultRandom().primaryKey(),
  code: text("code").notNull().unique(),
  name: text("name").notNull(),
  clientName: text("client_name"),
  location: text("location"),
  description: text("description"),
  status: projectStatus("status").default("planning").notNull(),
  startDate: timestamp("start_date", { withTimezone: true }),
  targetEndDate: timestamp("target_end_date", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const architectureWorks = pgTable("architecture_works", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  category: text("category").notNull(),
  description: text("description").notNull(),
  status: workStatus("status").default("planned").notNull(),
  progress: integer("progress").default(0).notNull(),
  notes: text("notes"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const engineeringWorks = pgTable("engineering_works", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  category: text("category").notNull(),
  description: text("description").notNull(),
  status: workStatus("status").default("planned").notNull(),
  progress: integer("progress").default(0).notNull(),
  notes: text("notes"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const mepWorks = pgTable("mep_works", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  drawingId: uuid("drawing_id").references(() => drawings.id, { onDelete: "set null" }),
  discipline: mepDiscipline("discipline").notNull(),
  category: text("category").notNull(),
  description: text("description").notNull(),
  specification: text("specification"),
  status: workStatus("status").default("planned").notNull(),
  progress: integer("progress").default(0).notNull(),
  notes: text("notes"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const drawings = pgTable("drawings", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  drawingNumber: text("drawing_number").notNull(),
  title: text("title").notNull(),
  discipline: drawingDiscipline("discipline").notNull(),
  revision: text("revision").default("A").notNull(),
  status: text("status").default("draft").notNull(),
  fileUrl: text("file_url"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const boqItems = pgTable("boq_items", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  drawingId: uuid("drawing_id").references(() => drawings.id, { onDelete: "set null" }),
  itemCode: text("item_code").notNull(),
  category: text("category").notNull(),
  element: text("element").notNull(),
  description: text("description").notNull(),
  quantity: decimal("quantity", { precision: 14, scale: 3 }).default("0").notNull(),
  unit: text("unit").notNull(),
  rate: decimal("rate", { precision: 14, scale: 2 }).default("0").notNull(),
  amount: decimal("amount", { precision: 16, scale: 2 }).default("0").notNull(),
  status: workStatus("status").default("planned").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const constructionActivities = pgTable("construction_activities", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  activityCode: text("activity_code").notNull(),
  name: text("name").notNull(),
  discipline: text("discipline"),
  status: workStatus("status").default("planned").notNull(),
  progress: integer("progress").default(0).notNull(),
  plannedQuantity: decimal("planned_quantity", { precision: 14, scale: 3 }).default("0").notNull(),
  actualQuantity: decimal("actual_quantity", { precision: 14, scale: 3 }).default("0").notNull(),
  unit: text("unit"),
  notes: text("notes"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const documents = pgTable("documents", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  title: text("title").notNull(),
  documentType: text("document_type").notNull(),
  fileUrl: text("file_url"),
  revision: text("revision"),
  isApproved: boolean("is_approved").default(false).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const tasks = pgTable("tasks", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  title: text("title").notNull(),
  description: text("description"),
  status: text("status").default("open").notNull(),
  priority: text("priority").default("normal").notNull(),
  dueDate: timestamp("due_date", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const rfis = pgTable("rfis", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  rfiNumber: text("rfi_number").notNull(),
  subject: text("subject").notNull(),
  question: text("question").notNull(),
  response: text("response"),
  status: text("status").default("open").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const approvals = pgTable("approvals", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "cascade" }).notNull(),
  subject: text("subject").notNull(),
  approvalType: text("approval_type").notNull(),
  status: text("status").default("pending").notNull(),
  comments: text("comments"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const auditLogs = pgTable("audit_logs", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => projects.id, { onDelete: "set null" }),
  actorId: text("actor_id"),
  action: text("action").notNull(),
  entityType: text("entity_type").notNull(),
  entityId: text("entity_id"),
  metadata: text("metadata"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});
