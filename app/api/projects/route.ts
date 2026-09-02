import { NextResponse } from "next/server";
import { desc } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { projects } from "@/db/schema";

export const runtime = "nodejs";

const projectInput = z.object({
  code: z.string().trim().min(1).max(50),
  name: z.string().trim().min(1).max(200),
  clientName: z.string().trim().max(200).optional().nullable(),
  location: z.string().trim().max(200).optional().nullable(),
  description: z.string().trim().max(2000).optional().nullable(),
  status: z.enum(["planning", "active", "on_hold", "completed", "cancelled"]).optional(),
  startDate: z.string().datetime().optional().nullable(),
  targetEndDate: z.string().datetime().optional().nullable(),
});

export async function GET() {
  try {
    const db = getDb();
    const rows = await db.select().from(projects).orderBy(desc(projects.createdAt));
    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("GET /api/projects failed", error);
    return NextResponse.json(
      { error: "Database is not configured or unavailable." },
      { status: 503 },
    );
  }
}

export async function POST(request: Request) {
  const parsed = projectInput.safeParse(await request.json().catch(() => null));

  if (!parsed.success) {
    return NextResponse.json(
      { error: "Invalid project data.", issues: parsed.error.flatten() },
      { status: 400 },
    );
  }

  try {
    const db = getDb();
    const [project] = await db
      .insert(projects)
      .values({
        ...parsed.data,
        status: parsed.data.status ?? "planning",
      })
      .returning();

    return NextResponse.json({ data: project }, { status: 201 });
  } catch (error) {
    console.error("POST /api/projects failed", error);
    return NextResponse.json(
      { error: "Unable to create project. The project code may already exist." },
      { status: 409 },
    );
  }
}
