import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { constructionActivities, projects } from "@/db/schema";

export const runtime = "nodejs";

const inputSchema = z.object({
  projectId: z.string().uuid(),
  activityCode: z.string().trim().min(1).max(80),
  name: z.string().trim().min(1).max(250),
  discipline: z.string().trim().max(120).optional().nullable(),
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]).optional(),
  progress: z.number().int().min(0).max(100).optional(),
  plannedQuantity: z.number().finite().min(0).max(100000000).optional(),
  actualQuantity: z.number().finite().min(0).max(100000000).optional(),
  unit: z.string().trim().max(30).optional().nullable(),
  notes: z.string().trim().max(4000).optional().nullable(),
});

export async function GET(request: Request) {
  try {
    const projectId = new URL(request.url).searchParams.get("projectId");
    if (projectId && !z.string().uuid().safeParse(projectId).success) {
      return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
    }

    const db = getDb();
    const rows = projectId
      ? await db.select().from(constructionActivities).where(eq(constructionActivities.projectId, projectId)).orderBy(desc(constructionActivities.createdAt))
      : await db.select().from(constructionActivities).orderBy(desc(constructionActivities.createdAt));

    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("GET /api/construction failed", error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const parsed = inputSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid construction activity data.", issues: parsed.error.flatten() }, { status: 400 });
  }

  try {
    const db = getDb();
    const [project] = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, parsed.data.projectId)).limit(1);
    if (!project) return NextResponse.json({ error: "Project not found." }, { status: 404 });

    const [activity] = await db.insert(constructionActivities).values({
      ...parsed.data,
      discipline: parsed.data.discipline || null,
      unit: parsed.data.unit || null,
      notes: parsed.data.notes || null,
      status: parsed.data.status ?? "planned",
      progress: parsed.data.progress ?? 0,
      plannedQuantity: String(parsed.data.plannedQuantity ?? 0),
      actualQuantity: String(parsed.data.actualQuantity ?? 0),
    }).returning();

    return NextResponse.json({ data: activity }, { status: 201 });
  } catch (error) {
    console.error("POST /api/construction failed", error);
    return NextResponse.json({ error: "Unable to create construction activity." }, { status: 500 });
  }
}
