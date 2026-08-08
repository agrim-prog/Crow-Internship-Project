// Server-only. Ported 1:1 from code/call_and_parse.py so extraction behavior
// (schema, system prompt, validation rules) stays identical to the Python pipeline.
import "server-only";
import Anthropic from "@anthropic-ai/sdk";
import {
  FIELD_TYPES,
  LEASE_ABSTRACT_SCHEMA,
  REQUIRED_FIELDS,
  type ExpectedKind,
  type LeaseAbstract,
} from "./schema";

const MODEL = "claude-sonnet-4-5";

const SYSTEM_PROMPT = `You are an expert commercial real estate analyst specializing in lease abstraction.

Return ONLY valid JSON matching the schema. No other text, no markdown fences, no explanation.

Field rules:
- monthly_rent: a NUMBER, not a string. Amounts may be written in words
  ("Two Thousand Seven Hundred Seventy-Five and 00/100 Dollars") - convert to 2775.00.
- lease_start / lease_end: format YYYY-MM-DD. If the lease refers to a term set out
  in an attachment or schedule not included in the text, return null.
  Do NOT calculate or infer dates from a stated duration.
- key_provisions: an array of short strings. Empty array if none stand out.

Missing vs unclear are DIFFERENT states and must not be collapsed:
- A field genuinely not stated anywhere -> null, and leave its review flag false.
- A field that IS present but worded so vaguely you are not confident ->
  give your best reading AND set its review flag true.

Date conflicts: if the document states two different values for the same
date (e.g. two different expiration dates in different sections), do NOT
silently pick one. Set lease_start and/or lease_end to null (whichever is
contradicted), set review_flags.date_conflict to true, and explain the
exact conflict — quoting or citing both sections — in uncertainty_notes.

Never invent a value. Never infer one from an unrelated clause.`;

function buildPrompt(rawLeaseText: string): string {
  return `Abstract this lease:\n\n<lease_text>\n${rawLeaseText}\n</lease_text>\n\nTarget schema:\n${JSON.stringify(
    LEASE_ABSTRACT_SCHEMA,
    null,
    2
  )}`;
}

function matchesType(value: unknown, expected: ExpectedKind): boolean {
  switch (expected) {
    case "string":
      return typeof value === "string";
    case "number":
      return typeof value === "number";
    case "array":
      return Array.isArray(value);
    case "object":
      return typeof value === "object" && value !== null && !Array.isArray(value);
  }
}

export function validate(parsed: Record<string, unknown>): string[] {
  const problems: string[] = [];

  for (const field of REQUIRED_FIELDS) {
    if (!(field in parsed)) {
      problems.push(`missing field: ${field}`);
      continue;
    }

    const value = parsed[field];
    if (value === null) continue; // null is fine for most fields

    const expected = FIELD_TYPES[field];
    if (!matchesType(value, expected)) {
      problems.push(`${field}: expected ${expected}, got ${typeof value} (${JSON.stringify(value)})`);
    }
  }

  for (const dateField of ["lease_start", "lease_end"] as const) {
    const value = parsed[dateField];
    if (typeof value === "string") {
      const parts = value.split("-");
      const allDigits = parts.every((p) => p.length > 0 && [...p].every((c) => c >= "0" && c <= "9"));
      if (value.length !== 10 || parts.length !== 3 || !allDigits) {
        problems.push(`${dateField}: expected YYYY-MM-DD, got ${JSON.stringify(value)}`);
      }
    }
  }

  const flags = parsed.review_flags;
  if (typeof flags === "object" && flags !== null && !Array.isArray(flags)) {
    const flagsRecord = flags as Record<string, unknown>;
    for (const flag of ["cam_unclear", "renewal_option_unclear", "date_conflict"]) {
      if (!(flag in flagsRecord)) {
        problems.push(`review_flags missing: ${flag}`);
      } else if (typeof flagsRecord[flag] !== "boolean") {
        problems.push(`review_flags.${flag}: expected boolean, got ${JSON.stringify(flagsRecord[flag])}`);
      }
    }
  }

  return problems;
}

export async function callAndParsePipeline(
  rawLeaseText: string
): Promise<{ result: LeaseAbstract | null; problems: string[] }> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return { result: null, problems: ["ANTHROPIC_API_KEY is not set on the server"] };
  }

  const client = new Anthropic({ apiKey });

  let rawOutput: string;
  try {
    const response = await client.messages.create({
      model: MODEL,
      max_tokens: 2000,
      temperature: 0,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: buildPrompt(rawLeaseText) }],
    });
    const block = response.content[0];
    rawOutput = block.type === "text" ? block.text : "";
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return { result: null, problems: [`API call failed: ${message}`] };
  }

  const start = rawOutput.indexOf("{");
  const end = rawOutput.lastIndexOf("}");
  if (start === -1 || end === -1 || end < start) {
    return { result: null, problems: ["parse failed: no JSON object found"] };
  }

  let parsed: Record<string, unknown>;
  try {
    parsed = JSON.parse(rawOutput.slice(start, end + 1));
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return { result: null, problems: [`parse failed: ${message}`] };
  }

  return { result: parsed as unknown as LeaseAbstract, problems: validate(parsed) };
}
