import { NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { boqItems } from "@/db/schema";

export const runtime = "nodejs";

const itemInput = z.object({
  projectId: z.string().uuid(),
  drawingId: z.string().uuid().optional().nullable(),
  itemCode: z.string().trim().min(1).max(100),
  category: z.string().trim().min(1).max(120),
  element: z.string().trim().min(1).max(160),
  description: z.string().trim().min(1).max(2000),
  quantity: z.coerce.number().finite().min(0).max(9999999999.999),
  unit: z.string().trim().min(1).max(30),
  rate: z.coerce.number().finite().min(0).max(999999999999.99),
  status: z.enum(["planned", "in_progress", "completed", "on_hold"]),
});

function decimal(value: number, scale: number) {
  return value.toFixed(scale);
}

function validId(id: string) {
  return z.string().uuid().safeParse(id).success;
}

export async function PUT(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid BOQ item id." }, { status: 400 });

  const parsed = itemInput.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid BOQ item data.", issues: parsed.error.flatten() }, { status: 400 });
  }

  try {
    const db = getDb();
    const amount = parsed.data.quantity * parsed.data.rate;
    const [item] = await db.update(boqItems).set({
      ...parsed.data,
      quantity: decimal(parsed.data.quantity, 3),
      rate: decimal(parsed.data.rate, 2),
      amount: decimal(amount, 2),
      updatedAt: new Date(),
    }).where(eq(boqItems.id, id)).returning();

    if (!item) return NextResponse.json({ error: "BOQ item not found." }, { status: 404 });
    return NextResponse.json({ data: item });
  } catch (error) {
    console.error("PUT /api/boq/[id] failed", error);
    return NextResponse.json({ error: "Unable to update BOQ item." }, { status: 500 });
  }
}

export async function DELETE(_request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid BOQ item id." }, { status: 400 });

  try {
    const db = getDb();
    const [item] = await db.delete(boqItems).where(eq(boqItems.id, id)).returning({ id: boqItems.id });
    if (!item) return NextResponse.json({ error: "BOQ item not found." }, { status: 404 });
    return NextResponse.json({ data: item });
  } catch (error) {
    console.error("DELETE /api/boq/[id] failed", error);
    return NextResponse.json({ error: "Unable to delete BOQ item." }, { status: 500 });
  }
}
