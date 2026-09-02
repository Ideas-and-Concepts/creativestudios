import { NextResponse } from "next/server";
import { z } from "zod";
import { desc } from "drizzle-orm";

import { getDb } from "@/db";
import { suppliers } from "@/db/schema";

export const runtime = "nodejs";

const supplierSchema = z.object({
  code: z.string().trim().min(1).max(50),
  name: z.string().trim().min(1).max(250),
  contactName: z.string().trim().max(150).nullable().optional(),
  email: z.string().trim().email().max(250).nullable().optional(),
  phone: z.string().trim().max(80).nullable().optional(),
  address: z.string().trim().max(500).nullable().optional(),
  taxNumber: z.string().trim().max(100).nullable().optional(),
  category: z.string().trim().max(120).nullable().optional(),
  notes: z.string().trim().max(4000).nullable().optional(),
  isActive: z.boolean().default(true),
});

export async function GET() {
  try {
    const db = getDb();
    const data = await db.select().from(suppliers).orderBy(desc(suppliers.createdAt));
    return NextResponse.json({ data });
  } catch {
    return NextResponse.json({ error: "Database unavailable." }, { status: 503 });
  }
}

export async function POST(request: Request) {
  try {
    const body = supplierSchema.parse(await request.json());
    const db = getDb();
    const [supplier] = await db.insert(suppliers).values({
      ...body,
      contactName: body.contactName || null,
      email: body.email || null,
      phone: body.phone || null,
      address: body.address || null,
      taxNumber: body.taxNumber || null,
      category: body.category || null,
      notes: body.notes || null,
    }).returning();
    return NextResponse.json({ data: supplier }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) return NextResponse.json({ error: "Invalid supplier data.", details: error.flatten() }, { status: 400 });
    return NextResponse.json({ error: "Unable to create supplier. The supplier code may already exist." }, { status: 409 });
  }
}
