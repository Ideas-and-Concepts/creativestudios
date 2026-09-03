import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { boqItems, constructionActivities, projects } from "@/db/schema";

export const runtime = "nodejs";

const idSchema = z.string().uuid();
const inputSchema = z.object({
  projectId: z.string().uuid(), boqItemId: z.string().uuid().optional().nullable(), activityCode: z.string().trim().min(1).max(80), name: z.string().trim().min(1).max(250), discipline: z.string().trim().max(120).optional().nullable(), contractor: z.string().trim().max(200).optional().nullable(), status: z.enum(["planned", "in_progress", "completed", "on_hold"]), progress: z.number().int().min(0).max(100), plannedQuantity: z.number().finite().min(0).max(100000000), actualQuantity: z.number().finite().min(0).max(100000000), unit: z.string().trim().max(30).optional().nullable(), plannedStart: z.string().datetime().optional().nullable(), plannedEnd: z.string().datetime().optional().nullable(), actualStart: z.string().datetime().optional().nullable(), actualEnd: z.string().datetime().optional().nullable(), notes: z.string().trim().max(4000).optional().nullable(),
}).superRefine((value, ctx) => { if (value.plannedStart && value.plannedEnd && new Date(value.plannedEnd) < new Date(value.plannedStart)) ctx.addIssue({ code: "custom", path: ["plannedEnd"], message: "Planned end cannot be before planned start." }); if (value.actualStart && value.actualEnd && new Date(value.actualEnd) < new Date(value.actualStart)) ctx.addIssue({ code: "custom", path: ["actualEnd"], message: "Actual end cannot be before actual start." }); });

async function validateLinks(data: z.infer<typeof inputSchema>) {
  const db = getDb(); const [project] = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, data.projectId)).limit(1); if (!project) return "Project not found.";
  if (data.boqItemId) { const [item] = await db.select({ id: boqItems.id, projectId: boqItems.projectId }).from(boqItems).where(eq(boqItems.id, data.boqItemId)).limit(1); if (!item) return "BOQ item not found."; if (item.projectId !== data.projectId) return "BOQ item does not belong to the selected project."; }
  return null;
}

function normalize(data: z.infer<typeof inputSchema>) { return { ...data, boqItemId: data.boqItemId || null, discipline: data.discipline || null, contractor: data.contractor || null, unit: data.unit || null, notes: data.notes || null, plannedQuantity: String(data.plannedQuantity), actualQuantity: String(data.actualQuantity), plannedStart: data.plannedStart ? new Date(data.plannedStart) : null, plannedEnd: data.plannedEnd ? new Date(data.plannedEnd) : null, actualStart: data.actualStart ? new Date(data.actualStart) : null, actualEnd: data.actualEnd ? new Date(data.actualEnd) : null }; }

export async function GET(_request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid construction activity id." }, { status: 400 });
  try {
    const [activity] = await getDb().select().from(constructionActivities).where(eq(constructionActivities.id, id)).limit(1);
    if (!activity) return NextResponse.json({ error: "Construction activity not found." }, { status: 404 });
    const [project] = await getDb().select({ id: projects.id, code: projects.code, name: projects.name }).from(projects).where(eq(projects.id, activity.projectId)).limit(1);
    const boq = activity.boqItemId ? (await getDb().select({ id: boqItems.id, itemCode: boqItems.itemCode, description: boqItems.description, quantity: boqItems.quantity, unit: boqItems.unit }).from(boqItems).where(eq(boqItems.id, activity.boqItemId)).limit(1))[0] : null;
    return NextResponse.json({ data: { ...activity, project: project ?? null, boqItem: boq ?? null } });
  } catch (error) {
    console.error("GET /api/construction/[id] failed", error);
    return NextResponse.json({ error: "Unable to load construction activity." }, { status: 503 });
  }
}

export async function PUT(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params; if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid construction activity id." }, { status: 400 });
  const parsed = inputSchema.safeParse(await request.json().catch(() => null)); if (!parsed.success) return NextResponse.json({ error: "Invalid construction activity data.", issues: parsed.error.flatten() }, { status: 400 });
  try { const linkError = await validateLinks(parsed.data); if (linkError) return NextResponse.json({ error: linkError }, { status: linkError === "Project not found." || linkError === "BOQ item not found." ? 404 : 400 }); const [activity] = await getDb().update(constructionActivities).set({ ...normalize(parsed.data), updatedAt: new Date() }).where(eq(constructionActivities.id, id)).returning(); if (!activity) return NextResponse.json({ error: "Construction activity not found." }, { status: 404 }); return NextResponse.json({ data: activity }); }
  catch (error) { console.error("PUT /api/construction/[id] failed", error); return NextResponse.json({ error: "Unable to update construction activity." }, { status: 500 }); }
}

export async function DELETE(_request: Request, context: { params: Promise<{ id: string }> }) { const { id } = await context.params; if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid construction activity id." }, { status: 400 }); try { const [activity] = await getDb().delete(constructionActivities).where(eq(constructionActivities.id, id)).returning({ id: constructionActivities.id }); if (!activity) return NextResponse.json({ error: "Construction activity not found." }, { status: 404 }); return NextResponse.json({ data: activity }); } catch (error) { console.error("DELETE /api/construction/[id] failed", error); return NextResponse.json({ error: "Unable to delete construction activity." }, { status: 500 }); } }
