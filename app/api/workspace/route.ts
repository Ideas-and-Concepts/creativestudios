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

function validId(value: unknown) {
  return typeof value === "string" && z.string().uuid().safeParse(value).success;
}

async function parseBody(request: Request, module: ModuleName) {
  return schemas[module].safeParse(await request.json().catch(() => null));
}

function normalizeValues(module: ModuleName, values: Record<string, unknown>) {
  const normalized = { ...values } as Record<string, unknown>;
  if (module === "architecture") { normalized.status ??= "planned"; normalized.progress ??= 0; }
  if (module === "tasks") { normalized.status ??= "open"; normalized.priority ??= "normal"; if (normalized.dueDate) normalized.dueDate = new Date(String(normalized.dueDate)); }
  if (module === "rfis") normalized.status ??= "open";
  if (module === "approvals") normalized.status ??= "pending";
  if (module === "documents") normalized.isApproved ??= false;
  return normalized;
}

export async function GET(request: Request) {
  const module = moduleName(request);
  if (!module) return NextResponse.json({ error: "Unsupported workspace module." }, { status: 400 });
  const projectId = new URL(request.url).searchParams.get("projectId");
  if (projectId && !validId(projectId)) return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
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
  const parsed = await parseBody(request, module);
  if (!parsed.success) return NextResponse.json({ error: "Invalid record data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const table = tables[module] as any;
    const values = normalizeValues(module, parsed.data as Record<string, unknown>);
    const result = await getDb().insert(table).values(values).returning();
    const row = (result as any[])[0];
    return NextResponse.json({ data: row }, { status: 201 });
  } catch (error) {
    console.error(`POST /api/workspace?module=${module} failed`, error);
    return NextResponse.json({ error: "Unable to create record." }, { status: 500 });
  }
}

export async function PATCH(request: Request) {
  const module = moduleName(request);
  const id = new URL(request.url).searchParams.get("id");
  if (!module) return NextResponse.json({ error: "Unsupported workspace module." }, { status: 400 });
  if (!validId(id)) return NextResponse.json({ error: "Invalid record id." }, { status: 400 });
  const parsed = await parseBody(request, module);
  if (!parsed.success) return NextResponse.json({ error: "Invalid record data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const table = tables[module] as any;
    const values = normalizeValues(module, parsed.data as Record<string, unknown>);
    const result = await getDb().update(table).set({ ...values, updatedAt: new Date() }).where(eq(table.id, id)).returning();
    const row = (result as any[])[0];
    if (!row) return NextResponse.json({ error: "Record not found." }, { status: 404 });
    return NextResponse.json({ data: row });
  } catch (error) {
    console.error(`PATCH /api/workspace?module=${module}&id=${id} failed`, error);
    return NextResponse.json({ error: "Unable to update record." }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  const module = moduleName(request);
  const id = new URL(request.url).searchParams.get("id");
  if (!module) return NextResponse.json({ error: "Unsupported workspace module." }, { status: 400 });
  if (!validId(id)) return NextResponse.json({ error: "Invalid record id." }, { status: 400 });
  try {
    const table = tables[module] as any;
    const result = await getDb().delete(table).where(eq(table.id, id)).returning({ id: table.id });
    const row = (result as any[])[0];
    if (!row) return NextResponse.json({ error: "Record not found." }, { status: 404 });
    return NextResponse.json({ data: row });
  } catch (error) {
    console.error(`DELETE /api/workspace?module=${module}&id=${id} failed`, error);
    return NextResponse.json({ error: "Unable to delete record." }, { status: 500 });
  }
}
