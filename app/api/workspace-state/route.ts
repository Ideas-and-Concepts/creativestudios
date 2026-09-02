import { NextResponse } from "next/server";
import { neon } from "@neondatabase/serverless";
import { z } from "zod";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const patchSchema = z.object({
  pageConfig: z.record(z.string(), z.object({ name: z.string().trim().min(1).max(100), description: z.string().trim().max(300) })).optional(),
  theme: z.enum(["dark", "light"]).optional(),
  settings: z.record(z.string(), z.unknown()).optional(),
});

function getSql() {
  const url = process.env.DATABASE_URL?.trim();
  if (!url) throw new Error("DATABASE_URL is not configured.");
  return neon(url);
}

export async function GET() {
  try {
    const sql = getSql();
    const rows = await sql`SELECT data, updated_at FROM workspace_state WHERE id = 1 LIMIT 1`;
    const row = rows[0] as { data?: unknown; updated_at?: string } | undefined;
    return NextResponse.json({
      data: row?.data && typeof row.data === "object" ? row.data : {},
      updatedAt: row?.updated_at ?? null,
    });
  } catch (error) {
    console.error("GET /api/workspace-state failed", error);
    return NextResponse.json({ error: "Workspace state is unavailable." }, { status: 503 });
  }
}

export async function PUT(request: Request) {
  const parsed = patchSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid workspace state.", issues: parsed.error.flatten() }, { status: 400 });
  }

  try {
    const sql = getSql();
    const patch = JSON.stringify(parsed.data);
    const rows = await sql`
      INSERT INTO workspace_state (id, data, updated_at)
      VALUES (1, ${patch}::jsonb, now())
      ON CONFLICT (id) DO UPDATE
      SET data = workspace_state.data || EXCLUDED.data,
          updated_at = now()
      RETURNING data, updated_at
    `;
    return NextResponse.json({ data: rows[0]?.data ?? {}, updatedAt: rows[0]?.updated_at ?? null });
  } catch (error) {
    console.error("PUT /api/workspace-state failed", error);
    return NextResponse.json({ error: "Unable to save workspace state." }, { status: 503 });
  }
}
