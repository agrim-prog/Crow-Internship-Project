import { NextRequest, NextResponse } from "next/server";
import { readSample } from "@/lib/samples";

export const runtime = "nodejs";

export async function GET(
  _request: NextRequest,
  ctx: RouteContext<"/api/samples/[id]">
) {
  const { id } = await ctx.params;
  const text = await readSample(id);
  if (text === null) {
    return NextResponse.json({ error: "Sample not found" }, { status: 404 });
  }
  return NextResponse.json({ id, text });
}
