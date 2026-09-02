import { NextResponse } from "next/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { boqItems } from "@/db/schema";

export const runtime = "nodejs";

const boqInput = z.object({
  projectId: z.string().uuid(),
  drawingId: z.string().uuid().optional().nullable(),
  itemCode: z.string().trim().min(1).max(100),
  category: z.string().trim().min(1).max(120),
  element: z.string().trim().min(1).max(160),
  description: z.string().trim().min(1).max(2000),
  quantity: z.coerce.number().finite().min(0).max(9999999999.999),
  unit: z.string().trim().min(1).max(30),
  rate: z.coerce.number().finite().min(0).max(999999999999.99),
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]).optional(),
});

function decimal(value: number, scale: number) {
  return value.toFixed(scale);
}

export async function GET(request: Request) {
  try {
    const projectId = new URL(request.url).searchParams.get("projectId");
    if (projectId && !z.string().uuid().safeParse(projectId).success) {
      return NextResponse.json({ error: "Invalid project id." }, { status: 400 });
    }

    const db = getDb();
    const rows = projectId
      ? await db.select().from(boqItems).where(eq(boqItems.projectId, projectId)).orderBy(desc(boqItems.createdAt))
      : await db.select().from(boqItems).orderBy(desc(boqItems.createdAt));

    return NextResponse.json({ data: rows });
  } catch (error) {
    console.error("GET /api/boq failed", error);
    return NextResponse.json({ error: "Database is not configured or unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  const parsed = boqInput.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid BOQ item data.", issues: parsed.error.flatten() }, { status: 400 });
  }

  try {
    const db = getDb();
    const amount = parsed.data.quantity * parsed.data.rate;
    const [item] = await db.insert(boqItems).values({
      ...parsed.data,
      quantity: decimal(parsed.data.quantity, 3),
      rate: decimal(parsed.data.rate, 2),
      amount: decimal(amount, 2),
      status: parsed.data.status ?? "planned",
    }).returning();

    return NextResponse.json({ data: item }, { status: 201 });
  } catch (error) {
    console.error("POST /api/boq failed", error);
    return NextResponse.json({ error: "Unable to create BOQ item." }, { status: 500 });
  }
}
