import { NextResponse } from "next/server";
import { and, desc, eq, gte, lte } from "drizzle-orm";
import { z } from "zod";
import { getDb } from "@/db";
import { constructionActivities, projects, siteProgressLogs } from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const inspectionStatuses = ["Not recorded", "Pending", "Passed", "Failed", "Conditional"] as const;
const logSchema = z.object({
  projectId: z.string().uuid(),
  activityId: z.string().uuid(),
  logDate: z.string().datetime(),
  workDescription: z.string().trim().min(1).max(4000),
  quantityCompleted: z.coerce.number().finite().min(0).max(999999999),
  unit: z.string().trim().max(30).optional().nullable(),
  workforceCount: z.coerce.number().int().min(0).max(100000),
  equipment: z.string().trim().max(4000).optional().nullable(),
  siteConditions: z.string().trim().max(4000).optional().nullable(),
  delayHours: z.coerce.number().finite().min(0).max(999999).optional(),
  delayReason: z.string().trim().max(4000).optional().nullable(),
  inspectionStatus: z.enum(inspectionStatuses).optional(),
  notes: z.string().trim().max(4000).optional().nullable(),
});

function validId(value: unknown) {
  return typeof value === "string" && z.string().uuid().safeParse(value).success;
}

async function validateRelationship(projectId: string, activityId: string) {
  const [project, activity] = await Promise.all([
    getDb().select({ id: projects.id }).from(projects).where(eq(projects.id, projectId)),
    getDb().select({ id: constructionActivities.id, projectId: constructionActivities.projectId }).from(constructionActivities).where(eq(constructionActivities.id, activityId)),
  ]);
  if (!project[0]) return "Project not found.";
  if (!activity[0]) return "Construction activity not found.";
  if (activity[0].projectId !== projectId) return "Construction activity does not belong to the selected project.";
  return null;
}

function normalize(data: z.infer<typeof logSchema>) {
  return {
    ...data,
    logDate: new Date(data.logDate),
    quantityCompleted: String(data.quantityCompleted),
    unit: data.unit || null,
    workforceCount: data.workforceCount ?? 0,
    equipment: data.equipment || null,
    siteConditions: data.siteConditions || null,
    delayHours: String(data.delayHours ?? 0),
    delayReason: data.delayReason || null,
    inspectionStatus: data.inspectionStatus ?? "Not recorded",
    notes: data.notes || null,
  };
}

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams;
  const projectId = params.get("projectId");
  const activityId = params.get("activityId");
  const from = params.get("from");
  const to = params.get("to");
  if (projectId && !validId(projectId)) return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
  if (activityId && !validId(activityId)) return NextResponse.json({ error: "Invalid activity id." }, { status: 400 });
  if (from && Number.isNaN(new Date(from).getTime())) return NextResponse.json({ error: "Invalid from date." }, { status: 400 });
  if (to && Number.isNaN(new Date(to).getTime())) return NextResponse.json({ error: "Invalid to date." }, { status: 400 });
  try {
    const conditions = [];
    if (projectId) conditions.push(eq(siteProgressLogs.projectId, projectId));
    if (activityId) conditions.push(eq(siteProgressLogs.activityId, activityId));
    if (from) conditions.push(gte(siteProgressLogs.logDate, new Date(from)));
    if (to) conditions.push(lte(siteProgressLogs.logDate, new Date(to)));
    const rows = await getDb().select().from(siteProgressLogs).where(conditions.length ? and(...conditions) : undefined).orderBy(desc(siteProgressLogs.logDate), desc(siteProgressLogs.createdAt));
    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("GET /api/construction/progress failed", error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const parsed = logSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid site progress log data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const relationshipError = await validateRelationship(parsed.data.projectId, parsed.data.activityId);
    if (relationshipError) return NextResponse.json({ error: relationshipError }, { status: 400 });
    const values = normalize(parsed.data);
    const result = await getDb().insert(siteProgressLogs).values(values).returning();
    return NextResponse.json({ data: result[0] }, { status: 201 });
  } catch (error) {
    console.error("POST /api/construction/progress failed", error);
    return NextResponse.json({ error: "Unable to create site progress log." }, { status: 500 });
  }
}
