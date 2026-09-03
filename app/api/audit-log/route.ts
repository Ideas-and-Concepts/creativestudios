import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";
import { getDb } from "@/db";
import { auditLogs } from "@/db/workflow";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const schema = z.object({ projectId: z.string().uuid().optional().nullable(), actor: z.string().trim().max(200).optional().nullable(), action: z.string().trim().min(1).max(100), entityType: z.string().trim().min(1).max(100), entityId: z.string().trim().max(100).optional().nullable(), entityLabel: z.string().trim().max(300).optional().nullable(), details: z.string().trim().max(5000).optional().nullable(), metadata: z.string().trim().max(10000).optional().nullable() });
export async function GET(request: Request) { try { const projectId = new URL(request.url).searchParams.get("projectId"); const rows = await getDb().select().from(auditLogs).where(projectId ? eq(auditLogs.projectId, projectId) : undefined).orderBy(desc(auditLogs.createdAt)); return NextResponse.json({ data: rows }); } catch (error) { console.error("GET /api/audit-log failed", error); return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 }); } }
export async function POST(request: Request) { const parsed = schema.safeParse(await request.json().catch(() => null)); if (!parsed.success) return NextResponse.json({ error: "Invalid audit event.", issues: parsed.error.flatten() }, { status: 400 }); try { const result = await getDb().insert(auditLogs).values(parsed.data as any).returning(); return NextResponse.json({ data: result[0] }, { status: 201 }); } catch (error) { console.error("POST /api/audit-log failed", error); return NextResponse.json({ error: "Unable to create audit event." }, { status: 500 }); } }
