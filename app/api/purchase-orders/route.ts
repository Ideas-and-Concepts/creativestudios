import { NextResponse } from "next/server";
import { and, desc, eq } from "drizzle-orm";
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

const orderSchema = z.object({
  projectId: z.string().uuid(),
  supplierId: z.string().uuid(),
  poNumber: z.string().trim().min(1).max(80),
  status: z.enum(["draft", "requested", "approved", "ordered", "partially_received", "received", "cancelled"]).default("draft"),
  orderDate: z.string().datetime().nullable().optional(),
  expectedDeliveryDate: z.string().datetime().nullable().optional(),
  taxAmount: z.coerce.number().finite().nonnegative().default(0),
  notes: z.string().trim().max(4000).nullable().optional(),
  items: z.array(itemSchema).min(1).max(200),
});

export async function GET(request: Request) {
  try {
    const db = getDb();
    const projectId = new URL(request.url).searchParams.get("projectId");
    const orders = projectId && z.string().uuid().safeParse(projectId).success
      ? await db.select({ order: purchaseOrders, project: projects, supplier: suppliers })
          .from(purchaseOrders)
          .innerJoin(projects, eq(purchaseOrders.projectId, projects.id))
          .innerJoin(suppliers, eq(purchaseOrders.supplierId, suppliers.id))
          .where(eq(purchaseOrders.projectId, projectId))
          .orderBy(desc(purchaseOrders.createdAt))
      : await db.select({ order: purchaseOrders, project: projects, supplier: suppliers })
          .from(purchaseOrders)
          .innerJoin(projects, eq(purchaseOrders.projectId, projects.id))
          .innerJoin(suppliers, eq(purchaseOrders.supplierId, suppliers.id))
          .orderBy(desc(purchaseOrders.createdAt));

    const data = await Promise.all(orders.map(async ({ order, project, supplier }) => {
      const items = await db.select().from(purchaseOrderItems).where(eq(purchaseOrderItems.purchaseOrderId, order.id));
      return { ...order, project, supplier, items };
    }));
    return NextResponse.json({ data });
  } catch {
    return NextResponse.json({ error: "Database unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  try {
    const body = orderSchema.parse(await request.json());
    const db = getDb();

    const [project] = await db.select({ id: projects.id }).from(projects).where(eq(projects.id, body.projectId)).limit(1);
    const [supplier] = await db.select({ id: suppliers.id }).from(suppliers).where(and(eq(suppliers.id, body.supplierId), eq(suppliers.isActive, true))).limit(1);
    if (!project) return NextResponse.json({ error: "Project not found." }, { status: 404 });
    if (!supplier) return NextResponse.json({ error: "Active supplier not found." }, { status: 404 });

    const boqIds = body.items.map((item) => item.boqItemId).filter((id): id is string => Boolean(id));
    if (boqIds.length) {
      const linked = await db.select({ id: boqItems.id, projectId: boqItems.projectId }).from(boqItems);
      const allowed = new Set(linked.filter((row) => row.projectId === body.projectId).map((row) => row.id));
      if (boqIds.some((id) => !allowed.has(id))) return NextResponse.json({ error: "One or more BOQ items do not belong to the selected project." }, { status: 400 });
    }

    const subtotal = body.items.reduce((sum, item) => sum + item.quantity * item.unitRate, 0);
    const taxAmount = body.taxAmount;
    const totalAmount = subtotal + taxAmount;

    const [order] = await db.insert(purchaseOrders).values({
      projectId: body.projectId,
      supplierId: body.supplierId,
      poNumber: body.poNumber,
      status: body.status,
      orderDate: body.orderDate ? new Date(body.orderDate) : null,
      expectedDeliveryDate: body.expectedDeliveryDate ? new Date(body.expectedDeliveryDate) : null,
      subtotal: subtotal.toFixed(2),
      taxAmount: taxAmount.toFixed(2),
      totalAmount: totalAmount.toFixed(2),
      notes: body.notes || null,
    }).returning();

    await db.insert(purchaseOrderItems).values(body.items.map((item) => ({
      purchaseOrderId: order.id,
      boqItemId: item.boqItemId || null,
      description: item.description,
      quantity: item.quantity.toFixed(3),
      unit: item.unit,
      unitRate: item.unitRate.toFixed(2),
      amount: (item.quantity * item.unitRate).toFixed(2),
    })));

    return NextResponse.json({ data: { ...order, items: body.items } }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid purchase order data.", details: error.flatten() }, { status: 400 });
    return NextResponse.json({ error: "Unable to create purchase order. The PO number may already exist." }, { status: 409 });
  }
}
