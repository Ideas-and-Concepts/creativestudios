import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
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

export async function PUT(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid progress log id." }, { status: 400 });
  const parsed = logSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Invalid site progress log data.", issues: parsed.error.flatten() }, { status: 400 });
  try {
    const relationshipError = await validateRelationship(parsed.data.projectId, parsed.data.activityId);
    if (relationshipError) return NextResponse.json({ error: relationshipError }, { status: 400 });
    const values = normalize(parsed.data);
    const result = await getDb().update(siteProgressLogs).set({ ...values, updatedAt: new Date() }).where(eq(siteProgressLogs.id, id)).returning();
    if (!result[0]) return NextResponse.json({ error: "Progress log not found." }, { status: 404 });
    return NextResponse.json({ data: result[0] });
  } catch (error) {
    console.error(`PUT /api/construction/progress/${id} failed`, error);
    return NextResponse.json({ error: "Unable to update site progress log." }, { status: 500 });
  }
}

export async function DELETE(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid progress log id." }, { status: 400 });
  try {
    const result = await getDb().delete(siteProgressLogs).where(eq(siteProgressLogs.id, id)).returning({ id: siteProgressLogs.id });
    if (!result[0]) return NextResponse.json({ error: "Progress log not found." }, { status: 404 });
    return NextResponse.json({ data: result[0] });
  } catch (error) {
    console.error(`DELETE /api/construction/progress/${id} failed`, error);
    return NextResponse.json({ error: "Unable to delete site progress log." }, { status: 500 });
  }
}
