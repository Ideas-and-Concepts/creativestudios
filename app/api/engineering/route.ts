import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { engineeringWorks } from "@/db/schema";

export const runtime = "nodejs";

const engineeringInput = z.object({
  projectId: z.string().uuid(),
  category: z.string().trim().min(1).max(120),
  description: z.string().trim().min(1).max(2000),
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
      ? await db.select().from(engineeringWorks).where(eq(engineeringWorks.projectId, projectId)).orderBy(desc(engineeringWorks.createdAt))
      : await db.select().from(engineeringWorks).orderBy(desc(engineeringWorks.createdAt));

    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("GET /api/engineering failed", error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const parsed = engineeringInput.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid engineering work data.", issues: parsed.error.flatten() }, { status: 400 });
  }

  try {
    const db = getDb();
    const [work] = await db.insert(engineeringWorks).values({
      ...parsed.data,
      status: parsed.data.status ?? "planned",
      progress: parsed.data.progress ?? 0,
    }).returning();

    return NextResponse.json({ data: work }, { status: 201 });
  } catch (error) {
    console.error("POST /api/engineering failed", error);
    return NextResponse.json({ error: "Unable to create engineering work." }, { status: 500 });
  }
}
