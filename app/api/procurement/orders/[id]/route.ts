import { NextRequest, NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "../../../../../db";
import { boqItems, projects, purchaseOrderItems, purchaseOrders, suppliers } from "../../../../../db/schema";

export const runtime = "nodejs";

const statuses = ["draft", "requested", "approved", "ordered", "partially_received", "received", "cancelled"] as const;
const idSchema = z.string().uuid();
const itemSchema = z.object({
  boqItemId: z.string().uuid().nullable().optional(),
  description: z.string().trim().min(1).max(2000),
  quantity: z.number().positive().max(100000000),
  unit: z.string().trim().min(1).max(30),
  unitRate: z.number().min(0).max(1000000000),
});
const orderSchema = z.object({
  projectId: z.string().uuid(),
  supplierId: z.string().uuid(),
  poNumber: z.string().trim().min(1).max(80),
  status: z.enum(statuses).default("draft"),
  orderDate: z.string().datetime({ offset: true }).nullable().optional(),
  expectedDeliveryDate: z.string().datetime({ offset: true }).nullable().optional(),
  taxRate: z.number().min(0).max(100).default(0),
  notes: z.string().trim().max(4000).nullable().optional(),
  items: z.array(itemSchema).min(1).max(500),
});

function decimal(value: number, scale: number) { return Number(value.toFixed(scale)); }

export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid purchase order ID." }, { status: 400 });

  try {
    const body = orderSchema.parse(await request.json());
    const db = getDb();

    const [existing] = await db.select({ id: purchaseOrders.id }).from(purchaseOrders).where(eq(purchaseOrders.id, id)).limit(1);
    if (!existing) return NextResponse.json({ error: "Purchase order not found." }, { status: 404 });

    const [project] = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, body.projectId)).limit(1);
    if (!project) return NextResponse.json({ error: "Project not found." }, { status: 400 });

    const [supplier] = await db.select({ id: suppliers.id, isActive: suppliers.isActive }).from(suppliers).where(eq(suppliers.id, body.supplierId)).limit(1);
    if (!supplier) return NextResponse.json({ error: "Supplier not found." }, { status: 400 });
    if (!supplier.isActive) return NextResponse.json({ error: "The selected supplier is inactive." }, { status: 400 });

    for (const item of body.items) {
      if (item.boqItemId) {
        const [boq] = await db.select({ id: boqItems.id, projectId: boqItems.projectId }).from(boqItems).where(eq(boqItems.id, item.boqItemId)).limit(1);
        if (!boq) return NextResponse.json({ error: "A linked BOQ item was not found." }, { status: 400 });
        if (boq.projectId !== body.projectId) return NextResponse.json({ error: "Every linked BOQ item must belong to the selected project." }, { status: 400 });
      }
    }

    const subtotal = decimal(body.items.reduce((sum, item) => sum + item.quantity * item.unitRate, 0), 2);
    const taxAmount = decimal(subtotal * (body.taxRate / 100), 2);
    const totalAmount = decimal(subtotal + taxAmount, 2);

    const [order] = await db.update(purchaseOrders).set({
      projectId: body.projectId,
      supplierId: body.supplierId,
      poNumber: body.poNumber,
      status: body.status,
      orderDate: body.orderDate ? new Date(body.orderDate) : null,
      expectedDeliveryDate: body.expectedDeliveryDate ? new Date(body.expectedDeliveryDate) : null,
      subtotal: subtotal.toFixed(2),
      taxAmount: taxAmount.toFixed(2),
      totalAmount: totalAmount.toFixed(2),
      notes: body.notes?.trim() || null,
      updatedAt: new Date(),
    }).where(eq(purchaseOrders.id, id)).returning();

    await db.delete(purchaseOrderItems).where(eq(purchaseOrderItems.purchaseOrderId, id));
    try {
      await db.insert(purchaseOrderItems).values(body.items.map((item) => ({
        purchaseOrderId: id,
        boqItemId: item.boqItemId ?? null,
        description: item.description,
        quantity: item.quantity.toFixed(3),
        unit: item.unit,
        unitRate: item.unitRate.toFixed(2),
        amount: decimal(item.quantity * item.unitRate, 2).toFixed(2),
      })));
    } catch (itemError) {
      throw itemError;
    }

    return NextResponse.json({ data: order });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid purchase order data.", details: error.flatten() }, { status: 400 });
    console.error(`PUT /api/procurement/orders/${id} failed`, error);
    return NextResponse.json({ error: "Unable to update purchase order. The PO number may already exist." }, { status: 409 });
  }
}

export async function DELETE(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid purchase order ID." }, { status: 400 });

  try {
    const db = getDb();
    const [order] = await db.delete(purchaseOrders).where(eq(purchaseOrders.id, id)).returning({ id: purchaseOrders.id });
    if (!order) return NextResponse.json({ error: "Purchase order not found." }, { status: 404 });
    return NextResponse.json({ data: order });
  } catch (error) {
    console.error(`DELETE /api/procurement/orders/${id} failed`, error);
    return NextResponse.json({ error: "Unable to delete purchase order." }, { status: 409 });
  }
}
