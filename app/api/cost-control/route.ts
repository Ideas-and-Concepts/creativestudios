import { NextRequest, NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
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

export async function GET(request: NextRequest) {
  if (!process.env.DATABASE_URL) return unavailable();
  try {
    const projectId = request.nextUrl.searchParams.get("projectId");
    const db = getDb();
    const rows = projectId
      ? await db.select().from(costControl).where(eq(costControl.projectId, projectId)).orderBy(desc(costControl.updatedAt))
      : await db.select().from(costControl).orderBy(desc(costControl.updatedAt));
    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("Cost control GET failed:", error);
    return NextResponse.json({ error: "Unable to load cost control records." }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  if (!process.env.DATABASE_URL) return unavailable();
  try {
    const payload = schema.parse(await request.json());
    const db = getDb();
    const project = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, payload.projectId)).limit(1);
    if (!project[0]) return NextResponse.json({ error: "Selected project does not exist." }, { status: 404 });

    const [created] = await db.insert(costControl).values({
      projectId: payload.projectId,
      costCode: payload.costCode,
      description: payload.description,
      costType: payload.costType,
      amount: payload.amount.toFixed(2),
      status: payload.status,
      notes: payload.notes || null,
    }).returning();
    return NextResponse.json({ data: created }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid cost control data.", details: error.flatten() }, { status: 400 });
    console.error("Cost control POST failed:", error);
    return NextResponse.json({ error: "Unable to create cost control record." }, { status: 500 });
  }
}
