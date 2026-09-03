import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { boqItems, constructionActivities, projects } from "@/db/schema";

export const runtime = "nodejs";

const dateValue = z.string().datetime().optional().nullable();
const inputSchema = z.object({
  projectId: z.string().uuid(),
  boqItemId: z.string().uuid().optional().nullable(),
  activityCode: z.string().trim().min(1).max(80),
  name: z.string().trim().min(1).max(250),
  discipline: z.string().trim().max(120).optional().nullable(),
  contractor: z.string().trim().max(200).optional().nullable(),
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]).optional(),
  progress: z.number().int().min(0).max(100).optional(),
  plannedQuantity: z.number().finite().min(0).max(100000000).optional(),
  actualQuantity: z.number().finite().min(0).max(100000000).optional(),
  unit: z.string().trim().max(30).optional().nullable(),
  plannedStart: dateValue,
  plannedEnd: dateValue,
  actualStart: dateValue,
  actualEnd: dateValue,
  notes: z.string().trim().max(4000).optional().nullable(),
}).superRefine((value, ctx) => {
  if (value.plannedStart && value.plannedEnd && new Date(value.plannedEnd) < new Date(value.plannedStart)) ctx.addIssue({ code: "custom", path: ["plannedEnd"], message: "Planned end cannot be before planned start." });
  if (value.actualStart && value.actualEnd && new Date(value.actualEnd) < new Date(value.actualStart)) ctx.addIssue({ code: "custom", path: ["actualEnd"], message: "Actual end cannot be before actual start." });
});

async function validateLinks(data: z.infer<typeof inputSchema>) {
  const db = getDb();
  const [project] = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, data.projectId)).limit(1);
  if (!project) return "Project not found.";
  if (data.boqItemId) {
    const [item] = await db.select({ id: boqItems.id, projectId: boqItems.projectId }).from(boqItems).where(eq(boqItems.id, data.boqItemId)).limit(1);
    if (!item) return "BOQ item not found.";
    if (item.projectId !== data.projectId) return "BOQ item does not belong to the selected project.";
  }
  return null;
}

function normalize(data: z.infer<typeof inputSchema>) {
  return { ...data, boqItemId: data.boqItemId || null, discipline: data.discipline || null, contractor: data.contractor || null, unit: data.unit || null, notes: data.notes || null, status: data.status ?? "planned", progress: data.progress ?? 0, plannedQuantity: String(data.plannedQuantity ?? 0), actualQuantity: String(data.actualQuantity ?? 0), plannedStart: data.plannedStart ? new Date(data.plannedStart) : null, plannedEnd: data.plannedEnd ? new Date(data.plannedEnd) : null, actualStart: data.actualStart ? new Date(data.actualStart) : null, actualEnd: data.actualEnd ? new Date(data.actualEnd) : null };
}

export async function GET(request: Request) {
  try {
    const projectId = new URL(request.url).searchParams.get("projectId");
    if (projectId && !z.string().uuid().safeParse(projectId).success) return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
    const db = getDb();
    const rows = projectId ? await db.select().from(constructionActivities).where(eq(constructionActivities.projectId, projectId)).orderBy(desc(constructionActivities.createdAt)) : await db.select().from(constructionActivities).orderBy(desc(constructionActivities.createdAt));
    return NextResponse.json({ data: rows });
  } catch (error) { console.error("GET /api/construction failed", error); return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 }); }
}

export async function POST(request: Request) {
  const parsed = inputSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid construction activity data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const linkError = await validateLinks(parsed.data);
    if (linkError) return NextResponse.json({ error: linkError }, { status: linkError === "Project not found." || linkError === "BOQ item not found." ? 404 : 400 });
    const [activity] = await getDb().insert(constructionActivities).values(normalize(parsed.data)).returning();
    return NextResponse.json({ data: activity }, { status: 201 });
  } catch (error) { console.error("POST /api/construction failed", error); return NextResponse.json({ error: "Unable to create construction activity." }, { status: 500 }); }
}
