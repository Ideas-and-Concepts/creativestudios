import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
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
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]),
  progress: z.number().int().min(0).max(100),
  notes: z.string().trim().max(4000).optional().nullable(),
});

function validId(id: string) { return z.string().uuid().safeParse(id).success; }

export async function PUT(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid MEP work id." }, { status: 400 });
  const parsed = mepInput.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid MEP work data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const db = getDb();
    const [work] = await db.update(mepWorks).set({ ...parsed.data, updatedAt: new Date() }).where(eq(mepWorks.id, id)).returning();
    if (!work) return NextResponse.json({ error: "MEP work not found." }, { status: 404 });
    return NextResponse.json({ data: work });
  } catch (error) {
    console.error("PUT /api/mep/[id] failed", error);
    return NextResponse.json({ error: "Unable to update MEP work." }, { status: 500 });
  }
}

export async function DELETE(_request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid MEP work id." }, { status: 400 });
  try {
    const db = getDb();
    const [work] = await db.delete(mepWorks).where(eq(mepWorks.id, id)).returning({ id: mepWorks.id });
    if (!work) return NextResponse.json({ error: "MEP work not found." }, { status: 404 });
    return NextResponse.json({ data: work });
  } catch (error) {
    console.error("DELETE /api/mep/[id] failed", error);
    return NextResponse.json({ error: "Unable to delete MEP work." }, { status: 500 });
  }
}
