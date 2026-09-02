import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { asc, eq } from "drizzle-orm";

import { getDb } from "../../../../db";
import { suppliers } from "../../../../db/schema";

export const runtime = "nodejs";

const supplierSchema = z.object({
  code: z.string().trim().min(1).max(50),
  name: z.string().trim().min(1).max(200),
  contactName: z.string().trim().max(160).nullable().optional(),
  email: z.string().trim().email().max(320).nullable().optional(),
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

export async function GET() {
  try {
    const db = getDb();
    const data = await db.select().from(suppliers).orderBy(asc(suppliers.name));
    return NextResponse.json({ data });
  } catch (error) {
    console.error("GET /api/procurement/suppliers failed", error);
    return NextResponse.json({ error: "Database unavailable. Configure DATABASE_URL and ensure the procurement tables exist." }, { status: 503 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = supplierSchema.parse(await request.json());
    const db = getDb();
    const [supplier] = await db.insert(suppliers).values({
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
    }).returning();
    return NextResponse.json({ data: supplier }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: "Invalid supplier data.", details: error.flatten() }, { status: 400 });
    }
    console.error("POST /api/procurement/suppliers failed", error);
    return NextResponse.json({ error: "Unable to create supplier. The supplier code may already exist." }, { status: 409 });
  }
}
