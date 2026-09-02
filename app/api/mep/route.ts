import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { mepWorks } from "@/db/schema";

export const runtime = "nodejs";

const mepInput = z.object({
  projectId: z.string().uuid(),
  drawingId: z.string().uuid().optional().nullable(),
  discipline: z.enum(["mechanical", "electrical", "plumbing", "fire_protection", "hvac", "public_health", "other"]),
  category: z.string().trim().min(1).max(120),
  description: z.string().trim().min(1).max(2000),
  specification: z.string().trim().max(4000).optional().nullable(),
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]).optional(),
  progress: z.number().int().min(0).max(100).optional(),
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
      ? await db.select().from(mepWorks).where(eq(mepWorks.projectId, projectId)).orderBy(desc(mepWorks.createdAt))
      : await db.select().from(mepWorks).orderBy(desc(mepWorks.createdAt));
    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("GET /api/mep failed", error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const parsed = mepInput.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid MEP work data.", issues: parsed.error.flatten() }, { status: 400 });

  try {
    const db = getDb();
    const [work] = await db.insert(mepWorks).values({
      ...parsed.data,
      status: parsed.data.status ?? "planned",
      progress: parsed.data.progress ?? 0,
    }).returning();
    return NextResponse.json({ data: work }, { status: 201 });
  } catch (error) {
    console.error("POST /api/mep failed", error);
    return NextResponse.json({ error: "Unable to create MEP work." }, { status: 500 });
  }
}
