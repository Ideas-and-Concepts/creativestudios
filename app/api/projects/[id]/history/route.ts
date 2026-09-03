import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";
import { getDb } from "@/db";
import { auditLogs } from "@/db/workflow";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const idSchema = z.string().uuid();

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  if (!idSchema.safeParse(id).success) {
    return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
  }

  try {
    const data = await getDb()
      .select()
      .from(auditLogs)
      .where(eq(auditLogs.projectId, id))
      .orderBy(desc(auditLogs.createdAt));

    return NextResponse.json({ data });
  } catch (error) {
    console.error("GET /api/projects/[id]/history failed", error);
    return NextResponse.json(
      { error: "Database is not configured or unavailable." },
      { status: 503 },
    );
  }
}
