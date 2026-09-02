import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { drawings } from "@/db/schema";

export const runtime = "nodejs";

const drawingInput = z.object({
  projectId: z.string().uuid(),
  drawingNumber: z.string().trim().min(1).max(100),
  title: z.string().trim().min(1).max(250),
  discipline: z.enum(["architectural", "structural"]),
  revision: z.string().trim().min(1).max(20),
  status: z.enum(["draft", "in_review", "approved", "issued", "superseded"]),
  fileUrl: z.string().trim().url().max(2000).optional().nullable(),
});

export async function GET(request: Request) {
  try {
    const projectId = new URL(request.url).searchParams.get("projectId");
    if (projectId && !z.string().uuid().safeParse(projectId).success) {
      return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
    }
    const db = getDb();
    const rows = projectId
      ? await db.select().from(drawings).where(eq(drawings.projectId, projectId)).orderBy(desc(drawings.createdAt))
      : await db.select().from(drawings).orderBy(desc(drawings.createdAt));
    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("GET /api/drawings failed", error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const parsed = drawingInput.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid drawing data.", issues: parsed.error.flatten() }, { status: 400 });

  try {
    const db = getDb();
    const [drawing] = await db.insert(drawings).values(parsed.data).returning();
    return NextResponse.json({ data: drawing }, { status: 201 });
  } catch (error) {
    console.error("POST /api/drawings failed", error);
    return NextResponse.json({ error: "Unable to register drawing." }, { status: 500 });
  }
}
