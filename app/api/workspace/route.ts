import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { approvals, architectureWorks, documents, rfis, tasks } from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const schemas = {
  documents: z.object({ projectId: z.string().uuid(), title: z.string().trim().min(1).max(200), documentType: z.string().trim().min(1).max(100), fileUrl: z.string().trim().max(1000).optional().nullable(), revision: z.string().trim().max(30).optional().nullable(), isApproved: z.boolean().optional() }),
  architecture: z.object({ projectId: z.string().uuid(), category: z.string().trim().min(1).max(120), description: z.string().trim().min(1).max(2000), status: z.enum(["planned", "in_progress", "completed", "on_hold"]).optional(), progress: z.number().int().min(0).max(100).optional(), notes: z.string().trim().max(4000).optional().nullable() }),
  tasks: z.object({ projectId: z.string().uuid(), title: z.string().trim().min(1).max(200), description: z.string().trim().max(4000).optional().nullable(), status: z.string().trim().max(50).optional(), priority: z.string().trim().max(50).optional(), dueDate: z.string().datetime().optional().nullable() }),
  rfis: z.object({ projectId: z.string().uuid(), rfiNumber: z.string().trim().min(1).max(60), subject: z.string().trim().min(1).max(200), question: z.string().trim().min(1).max(5000), response: z.string().trim().max(5000).optional().nullable(), status: z.string().trim().max(50).optional() }),
  approvals: z.object({ projectId: z.string().uuid(), subject: z.string().trim().min(1).max(200), approvalType: z.string().trim().min(1).max(100), status: z.string().trim().max(50).optional(), comments: z.string().trim().max(5000).optional().nullable() }),
} as const;

const tables = { documents, architecture: architectureWorks, tasks, rfis, approvals } as const;
type ModuleName = keyof typeof tables;

function moduleName(request: Request): ModuleName | null {
  const value = new URL(request.url).searchParams.get("module") as ModuleName | null;
  return value && value in tables ? value : null;
}

export async function GET(request: Request) {
  const module = moduleName(request);
  if (!module) return NextResponse.json({ error: "Unsupported workspace module." }, { status: 400 });
  const projectId = new URL(request.url).searchParams.get("projectId");
  if (projectId && !z.string().uuid().safeParse(projectId).success) return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
  try {
    const table = tables[module] as any;
    const rows = projectId
      ? await getDb().select().from(table).where(eq(table.projectId, projectId)).orderBy(desc(table.createdAt))
      : await getDb().select().from(table).orderBy(desc(table.createdAt));
    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error(`GET /api/workspace?module=${module} failed`, error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const module = moduleName(request);
  if (!module) return NextResponse.json({ error: "Unsupported workspace module." }, { status: 400 });
  const parsed = schemas[module].safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid record data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const table = tables[module] as any;
    const values: any = { ...parsed.data };
    if (module === "architecture") { values.status ??= "planned"; values.progress ??= 0; }
    if (module === "tasks") { values.status ??= "open"; values.priority ??= "normal"; if (values.dueDate) values.dueDate = new Date(values.dueDate); }
    if (module === "rfis") values.status ??= "open";
    if (module === "approvals") values.status ??= "pending";
    if (module === "documents") { values.isApproved ??= false; }
    const [row] = await getDb().insert(table).values(values).returning();
    return NextResponse.json({ data: row }, { status: 201 });
  } catch (error) {
    console.error(`POST /api/workspace?module=${module} failed`, error);
    return NextResponse.json({ error: "Unable to create record." }, { status: 500 });
  }
}
