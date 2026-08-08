import { NextRequest, NextResponse } from "next/server";
import { callAndParsePipeline } from "@/lib/pipeline";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const text = (body as { text?: unknown })?.text;
  if (typeof text !== "string" || !text.trim()) {
    return NextResponse.json({ error: "Field 'text' is required" }, { status: 400 });
  }

  const { result, problems } = await callAndParsePipeline(text);
  return NextResponse.json({ result, problems });
}
