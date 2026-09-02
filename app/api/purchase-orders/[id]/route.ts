import { NextResponse } from "next/server";
import { and, eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "@/db";
import { boqItems, projects, purchaseOrderItems, purchaseOrders, suppliers } from "@/db/schema";

export const runtime = "nodejs";

const itemSchema = z.object({
  boqItemId: z.string().uuid().nullable().optional(),
  description: z.string().trim().min(1).max(2000),
  quantity: z.coerce.number().finite().positive(),
  unit: z.string().trim().min(1).max(50),
  unitRate: z.coerce.number().finite().nonnegative(),
});

const schema = z.object({
  projectId: z.string().uuid(),
  supplierId: z.string().uuid(),
  poNumber: z.string().trim().min(1).max(80),
  status: z.enum(["draft", "requested", "approved", "ordered", "partially_received", "received", "cancelled"]),
  orderDate: z.string().datetime().nullable().optional(),
  expectedDeliveryDate: z.string().datetime().nullable().optional(),
  taxAmount: z.coerce.number().finite().nonnegative(),
  notes: z.string().trim().max(4000).nullable().optional(),
  items: z.array(itemSchema).min(1).max(200),
});

const uuid = z.string().uuid();

export async function PUT(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!uuid.safeParse(id).success) return NextResponse.json({ error: "Invalid purchase order ID." }, { status: 400 });
  try {
    const body = schema.parse(await request.json());
    const db = getDb();
    const [project] = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, body.projectId)).limit(1);
    const [supplier] = await db.select({ id: suppliers.id }).from(suppliers).where(and(eq(suppliers.id, body.supplierId), eq(suppliers.isActive, true))).limit(1);
    if (!project) return NextResponse.json({ error: "Project not found." }, { status: 404 });
    if (!supplier) return NextResponse.json({ error: "Active supplier not found." }, { status: 404 });

    const boqIds = body.items.map((item) => item.boqItemId).filter((value): value is string => Boolean(value));
    if (boqIds.length) {
      const linked = await db.select({ id: boqItems.id, projectId: boqItems.projectId }).from(boqItems);
      const allowed = new Set(linked.filter((row) => row.projectId === body.projectId).map((row) => row.id));
      if (boqIds.some((itemId) => !allowed.has(itemId))) return NextResponse.json({ error: "One or more BOQ items do not belong to the selected project." }, { status: 400 });
    }

    const subtotal = body.items.reduce((sum, item) => sum + item.quantity * item.unitRate, 0);
    const totalAmount = subtotal + body.taxAmount;
    const [order] = await db.update(purchaseOrders).set({
      projectId: body.projectId,
      supplierId: body.supplierId,
      poNumber: body.poNumber,
      status: body.status,
      orderDate: body.orderDate ? new Date(body.orderDate) : null,
      expectedDeliveryDate: body.expectedDeliveryDate ? new Date(body.expectedDeliveryDate) : null,
      subtotal: subtotal.toFixed(2),
      taxAmount: body.taxAmount.toFixed(2),
      totalAmount: totalAmount.toFixed(2),
      notes: body.notes || null,
      updatedAt: new Date(),
    }).where(eq(purchaseOrders.id, id)).returning();
    if (!order) return NextResponse.json({ error: "Purchase order not found." }, { status: 404 });

    await db.delete(purchaseOrderItems).where(eq(purchaseOrderItems.purchaseOrderId, id));
    await db.insert(purchaseOrderItems).values(body.items.map((item) => ({
      purchaseOrderId: id,
      boqItemId: item.boqItemId || null,
      description: item.description,
      quantity: item.quantity.toFixed(3),
      unit: item.unit,
      unitRate: item.unitRate.toFixed(2),
      amount: (item.quantity * item.unitRate).toFixed(2),
    })));

    return NextResponse.json({ data: { ...order, items: body.items } });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid purchase order data.", details: error.flatten() }, { status: 400 });
    return NextResponse.json({ error: "Unable to update purchase order." }, { status: 409 });
  }
}

export async function DELETE(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!uuid.safeParse(id).success) return NextResponse.json({ error: "Invalid purchase order ID." }, { status: 400 });
  try {
    const db = getDb();
    const [order] = await db.delete(purchaseOrders).where(eq(purchaseOrders.id, id)).returning({ id: purchaseOrders.id });
    if (!order) return NextResponse.json({ error: "Purchase order not found." }, { status: 404 });
    return NextResponse.json({ data: order });
  } catch {
    return NextResponse.json({ error: "Unable to delete purchase order." }, { status: 409 });
  }
}
