import { NextResponse } from "next/server";
import { z } from "zod";
import { recalculateActivityProgress } from "@/lib/construction-progress";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const schema = z.object({ activityId: z.string().uuid() });

export async function POST(request: Request) {
  const parsed = schema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "A valid activityId is required." }, { status: 400 });
  try {
    const activity = await recalculateActivityProgress(parsed.data.activityId);
    return NextResponse.json({ data: activity });
  } catch (error) {
    console.error("POST /api/construction/progress/recalculate failed", error);
    return NextResponse.json({ error: "Unable to recalculate activity progress." }, { status: 500 });
  }
}
