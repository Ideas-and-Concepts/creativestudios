import { NextRequest, NextResponse } from "next/server";
import { eq } from "drizzle-orm";
import { z } from "zod";

import { getDb } from "../../../../../db";
import { suppliers } from "../../../../../db/schema";

export const runtime = "nodejs";

const idSchema = z.string().uuid();
const supplierSchema = z.object({
  code: z.string().trim().min(1).max(50),
  name: z.string().trim().min(1).max(200),
  contactName: z.string().trim().max(160).nullable().optional(),
  email: z.preprocess((value) => typeof value === "string" && !value.trim() ? null : value, z.string().trim().email().max(320).nullable().optional()),
  phone: z.string().trim().max(60).nullable().optional(),
  address: z.string().trim().max(500).nullable().optional(),
  taxNumber: z.string().trim().max(100).nullable().optional(),
  category: z.string().trim().max(120).nullable().optional(),
  notes: z.string().trim().max(2000).nullable().optional(),
  isActive: z.boolean().default(true),
});

function cleanOptional(value: string | null | undefined) {
  const cleaned = value?.trim();
  return cleaned ? cleaned : null;
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid supplier ID." }, { status: 400 });

  try {
    const body = supplierSchema.parse(await request.json());
    const db = getDb();
    const [supplier] = await db.update(suppliers).set({
      code: body.code,
      name: body.name,
      contactName: cleanOptional(body.contactName),
      email: cleanOptional(body.email),
      phone: cleanOptional(body.phone),
      address: cleanOptional(body.address),
      taxNumber: cleanOptional(body.taxNumber),
      category: cleanOptional(body.category),
      notes: cleanOptional(body.notes),
      isActive: body.isActive,
      updatedAt: new Date(),
    }).where(eq(suppliers.id, id)).returning();

    if (!supplier) return NextResponse.json({ error: "Supplier not found." }, { status: 404 });
    return NextResponse.json({ data: supplier });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid supplier data.", details: error.flatten() }, { status: 400 });
    console.error(`PUT /api/procurement/suppliers/${id} failed`, error);
    return NextResponse.json({ error: "Unable to update supplier. The supplier code may already exist." }, { status: 409 });
  }
}

export async function DELETE(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!idSchema.safeParse(id).success) return NextResponse.json({ error: "Invalid supplier ID." }, { status: 400 });

  try {
    const db = getDb();
    const [supplier] = await db.delete(suppliers).where(eq(suppliers.id, id)).returning({ id: suppliers.id });
    if (!supplier) return NextResponse.json({ error: "Supplier not found." }, { status: 404 });
    return NextResponse.json({ data: supplier });
  } catch (error) {
    console.error(`DELETE /api/procurement/suppliers/${id} failed`, error);
    return NextResponse.json({ error: "Unable to delete supplier. Suppliers referenced by purchase orders cannot be removed." }, { status: 409 });
  }
}
