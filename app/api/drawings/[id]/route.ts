import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { drawings } from "@/db/schema";

export const runtime = "nodejs";

type RouteContext = { params: Promise<{ id: string }> };

const drawingUpdate = z.object({
  projectId: z.string().uuid(),
  drawingNumber: z.string().trim().min(1).max(100),
  title: z.string().trim().min(1).max(250),
  discipline: z.enum(["architectural", "structural"]),
  revision: z.string().trim().min(1).max(20),
  status: z.enum(["draft", "in_review", "approved", "issued", "superseded"]),
  fileUrl: z.string().trim().url().max(2000).optional().nullable(),
});

function validId(id: string) { return z.string().uuid().safeParse(id).success; }

export async function PUT(request: Request, { params }: RouteContext) {
  const { id } = await params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid drawing id." }, { status: 400 });
  const parsed = drawingUpdate.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid drawing data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const db = getDb();
    const [drawing] = await db.update(drawings).set({ ...parsed.data, updatedAt: new Date() }).where(eq(drawings.id, id)).returning();
    if (!drawing) return NextResponse.json({ error: "Drawing not found." }, { status: 404 });
    return NextResponse.json({ data: drawing });
  } catch (error) {
    console.error("PUT /api/drawings/[id] failed", error);
    return NextResponse.json({ error: "Unable to update drawing." }, { status: 500 });
  }
}

export async function DELETE(_request: Request, { params }: RouteContext) {
  const { id } = await params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid drawing id." }, { status: 400 });
  try {
    const db = getDb();
    const [drawing] = await db.delete(drawings).where(eq(drawings.id, id)).returning({ id: drawings.id });
    if (!drawing) return NextResponse.json({ error: "Drawing not found." }, { status: 404 });
    return NextResponse.json({ data: drawing });
  } catch (error) {
    console.error("DELETE /api/drawings/[id] failed", error);
    return NextResponse.json({ error: "Unable to delete drawing." }, { status: 500 });
  }
}
