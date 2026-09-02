import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { engineeringWorks } from "@/db/schema";

export const runtime = "nodejs";

type RouteContext = { params: Promise<{ id: string }> };

const workUpdate = z.object({
  projectId: z.string().uuid(),
  category: z.string().trim().min(1).max(120),
  description: z.string().trim().min(1).max(2000),
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]),
  progress: z.number().int().min(0).max(100),
  notes: z.string().trim().max(4000).optional().nullable(),
});

function validId(id: string) { return z.string().uuid().safeParse(id).success; }

export async function PUT(request: Request, { params }: RouteContext) {
  const { id } = await params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid engineering work id." }, { status: 400 });
  const parsed = workUpdate.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid engineering work data.", issues: parsed.error.flatten() }, { status: 400 });

  try {
    const db = getDb();
    const [work] = await db.update(engineeringWorks)
      .set({ ...parsed.data, updatedAt: new Date() })
      .where(eq(engineeringWorks.id, id))
      .returning();
    if (!work) return NextResponse.json({ error: "Engineering work not found." }, { status: 404 });
    return NextResponse.json({ data: work });
  } catch (error) {
    console.error("PUT /api/engineering/[id] failed", error);
    return NextResponse.json({ error: "Unable to update engineering work." }, { status: 500 });
  }
}

export async function DELETE(_request: Request, { params }: RouteContext) {
  const { id } = await params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid engineering work id." }, { status: 400 });

  try {
    const db = getDb();
    const [work] = await db.delete(engineeringWorks).where(eq(engineeringWorks.id, id)).returning({ id: engineeringWorks.id });
    if (!work) return NextResponse.json({ error: "Engineering work not found." }, { status: 404 });
    return NextResponse.json({ data: work });
  } catch (error) {
    console.error("DELETE /api/engineering/[id] failed", error);
    return NextResponse.json({ error: "Unable to delete engineering work." }, { status: 500 });
  }
}
