import { NextResponse } from "next/server";
import { z } from "zod";
import { eq } from "drizzle-orm";

import { getDb } from "@/db";
import { suppliers } from "@/db/schema";

export const runtime = "nodejs";

const schema = z.object({
  code: z.string().trim().min(1).max(50),
  name: z.string().trim().min(1).max(250),
  contactName: z.string().trim().max(150).nullable().optional(),
  email: z.string().trim().email().max(250).nullable().optional(),
  phone: z.string().trim().max(80).nullable().optional(),
  address: z.string().trim().max(500).nullable().optional(),
  taxNumber: z.string().trim().max(100).nullable().optional(),
  category: z.string().trim().max(120).nullable().optional(),
  notes: z.string().trim().max(4000).nullable().optional(),
  isActive: z.boolean(),
});

function validId(id: string) { return z.string().uuid().safeParse(id).success; }

export async function PUT(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid supplier ID." }, { status: 400 });
  try {
    const body = schema.parse(await request.json());
    const db = getDb();
    const [supplier] = await db.update(suppliers).set({
      ...body,
      contactName: body.contactName || null,
      email: body.email || null,
      phone: body.phone || null,
      address: body.address || null,
      taxNumber: body.taxNumber || null,
      category: body.category || null,
      notes: body.notes || null,
      updatedAt: new Date(),
    }).where(eq(suppliers.id, id)).returning();
    if (!supplier) return NextResponse.json({ error: "Supplier not found." }, { status: 404 });
    return NextResponse.json({ data: supplier });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid supplier data.", details: error.flatten() }, { status: 400 });
    return NextResponse.json({ error: "Unable to update supplier." }, { status: 409 });
  }
}

export async function DELETE(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!validId(id)) return NextResponse.json({ error: "Invalid supplier ID." }, { status: 400 });
  try {
    const db = getDb();
    const [supplier] = await db.delete(suppliers).where(eq(suppliers.id, id)).returning({ id: suppliers.id });
    if (!supplier) return NextResponse.json({ error: "Supplier not found." }, { status: 404 });
    return NextResponse.json({ data: supplier });
  } catch {
    return NextResponse.json({ error: "Unable to delete supplier. The supplier may be referenced by a purchase order." }, { status: 409 });
  }
}
