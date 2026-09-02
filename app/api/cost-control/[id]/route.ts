import { NextRequest, NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { costControl, projects } from "@/db/schema";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const costTypes = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"] as const;
const statuses = ["Draft", "Active", "Approved", "Closed"] as const;

const schema = z.object({
  projectId: z.string().uuid(),
  costCode: z.string().trim().min(1).max(100),
  description: z.string().trim().min(1).max(2000),
  costType: z.enum(costTypes),
  amount: z.number().finite().min(0).max(999999999999.99),
  status: z.enum(statuses),
  notes: z.string().trim().max(4000).optional().nullable(),
});

function unavailable() {
  return NextResponse.json({ error: "Database is not configured." }, { status: 503 });
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  if (!process.env.DATABASE_URL) return unavailable();
  try {
    const { id } = await params;
    const payload = schema.parse(await request.json());
    const db = getDb();
    const project = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, payload.projectId)).limit(1);
    if (!project[0]) return NextResponse.json({ error: "Selected project does not exist." }, { status: 404 });

    const [updated] = await db.update(costControl).set({
      projectId: payload.projectId,
      costCode: payload.costCode,
      description: payload.description,
      costType: payload.costType,
      amount: payload.amount.toFixed(2),
      status: payload.status,
      notes: payload.notes || null,
      updatedAt: new Date(),
    }).where(eq(costControl.id, id)).returning();
    if (!updated) return NextResponse.json({ error: "Cost control record not found." }, { status: 404 });
    return NextResponse.json({ data: updated });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid cost control data.", details: error.flatten() }, { status: 400 });
    console.error("Cost control PUT failed:", error);
    return NextResponse.json({ error: "Unable to update cost control record." }, { status: 500 });
  }
}

export async function DELETE(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  if (!process.env.DATABASE_URL) return unavailable();
  try {
    const { id } = await params;
    const db = getDb();
    const [deleted] = await db.delete(costControl).where(eq(costControl.id, id)).returning({ id: costControl.id });
    if (!deleted) return NextResponse.json({ error: "Cost control record not found." }, { status: 404 });
    return NextResponse.json({ data: deleted });
  } catch (error) {
    console.error("Cost control DELETE failed:", error);
    return NextResponse.json({ error: "Unable to delete cost control record." }, { status: 500 });
  }
}
