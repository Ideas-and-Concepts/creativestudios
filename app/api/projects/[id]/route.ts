import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { projects } from "@/db/schema";

export const runtime = "nodejs";

const projectUpdate = z.object({
  code: z.string().trim().min(1).max(50),
  name: z.string().trim().min(1).max(200),
  clientName: z.string().trim().max(200).optional().nullable(),
  location: z.string().trim().max(200).optional().nullable(),
  description: z.string().trim().max(2000).optional().nullable(),
  status: z.enum(["planning", "active", "on_hold", "completed", "cancelled"]),
});

type RouteContext = {
  params: Promise<{ id: string }>;
};

function isValidId(id: string) {
  return z.string().uuid().safeParse(id).success;
}

export async function GET(_request: Request, { params }: RouteContext) {
  const { id } = await params;

  if (!isValidId(id)) {
    return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
  }

  try {
    const db = getDb();
    const [project] = await db.select().from(projects).where(eq(projects.id, id)).limit(1);

    if (!project) {
      return NextResponse.json({ error: "Project not found." }, { status: 404 });
    }

    return NextResponse.json({ data: project });
  } catch (error) {
    console.error("GET /api/projects/[id] failed", error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function PUT(request: Request, { params }: RouteContext) {
  const { id } = await params;

  if (!isValidId(id)) {
    return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
  }

  const parsed = projectUpdate.safeParse(await request.json().catch(() => null));

  if (!parsed.success) {
    return NextResponse.json(
      { error: "Invalid project data.", issues: parsed.error.flatten() },
      { status: 400 },
    );
  }

  try {
    const db = getDb();
    const [project] = await db
      .update(projects)
      .set({ ...parsed.data, updatedAt: new Date() })
      .where(eq(projects.id, id))
      .returning();

    if (!project) {
      return NextResponse.json({ error: "Project not found." }, { status: 404 });
    }

    return NextResponse.json({ data: project });
  } catch (error) {
    console.error("PUT /api/projects/[id] failed", error);
    return NextResponse.json({ error: "Unable to update project. The project code may already exist." }, { status: 409 });
  }
}

export async function DELETE(_request: Request, { params }: RouteContext) {
  const { id } = await params;

  if (!isValidId(id)) {
    return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
  }

  try {
    const db = getDb();
    const [project] = await db.delete(projects).where(eq(projects.id, id)).returning({ id: projects.id });

    if (!project) {
      return NextResponse.json({ error: "Project not found." }, { status: 404 });
    }

    return NextResponse.json({ data: project });
  } catch (error) {
    console.error("DELETE /api/projects/[id] failed", error);
    return NextResponse.json({ error: "Unable to delete project." }, { status: 500 });
  }
}
