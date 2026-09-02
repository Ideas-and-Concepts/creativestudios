import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { constructionActivities, projects } from "@/db/schema";

export const runtime = "nodejs";

const idSchema = z.string().uuid();
const inputSchema = z.object({
  projectId: z.string().uuid(),
  activityCode: z.string().trim().min(1).max(80),
  name: z.string().trim().min(1).max(250),
  discipline: z.string().trim().max(120).optional().nullable(),
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]),
  progress: z.number().int().min(0).max(100),
  plannedQuantity: z.number().finite().min(0).max(100000000),
  actualQuantity: z.number().finite().min(0).max(100000000),
  unit: z.string().trim().max(30).optional().nullable(),
  notes: z.string().trim().max(4000).optional().nullable(),
});

export async function PUT(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid construction activity id." }, { status: 400 });

  const parsed = inputSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid construction activity data.", issues: parsed.error.flatten() }, { status: 400 });

  try {
    const db = getDb();
    const [project] = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, parsed.data.projectId)).limit(1);
    if (!project) return NextResponse.json({ error: "Project not found." }, { status: 404 });

    const [activity] = await db.update(constructionActivities).set({
      ...parsed.data,
      discipline: parsed.data.discipline || null,
      unit: parsed.data.unit || null,
      notes: parsed.data.notes || null,
      plannedQuantity: String(parsed.data.plannedQuantity),
      actualQuantity: String(parsed.data.actualQuantity),
      updatedAt: new Date(),
    }).where(eq(constructionActivities.id, id)).returning();

    if (!activity) return NextResponse.json({ error: "Construction activity not found." }, { status: 404 });
    return NextResponse.json({ data: activity });
  } catch (error) {
    console.error("PUT /api/construction/[id] failed", error);
    return NextResponse.json({ error: "Unable to update construction activity." }, { status: 500 });
  }
}

export async function DELETE(_request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid construction activity id." }, { status: 400 });

  try {
    const db = getDb();
    const [activity] = await db.delete(constructionActivities).where(eq(constructionActivities.id, id)).returning({ id: constructionActivities.id });
    if (!activity) return NextResponse.json({ error: "Construction activity not found." }, { status: 404 });
    return NextResponse.json({ data: activity });
  } catch (error) {
    console.error("DELETE /api/construction/[id] failed", error);
    return NextResponse.json({ error: "Unable to delete construction activity." }, { status: 500 });
  }
}
