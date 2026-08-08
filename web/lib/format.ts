import { FIELD_META, GROUP_LABELS, type LeaseAbstract } from "./schema";

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

export function isFieldFlagged(result: LeaseAbstract, key: keyof LeaseAbstract): boolean {
  const flags = result.review_flags ?? ({} as LeaseAbstract["review_flags"]);
  const direct = Boolean((flags as unknown as Record<string, boolean>)[`${key}_unclear`]);
  const dateConflict =
    (key === "lease_start" || key === "lease_end") && Boolean(flags?.date_conflict);
  return direct || dateConflict;
}

export function formatSummaryText(result: LeaseAbstract, sourceLabel: string): string {
  const lines: string[] = [];
  lines.push(`LEASE ABSTRACT — ${sourceLabel}`);
  lines.push("=".repeat(48));

  let currentGroup: string | null = null;
  for (const field of FIELD_META) {
    if (field.group !== currentGroup) {
      currentGroup = field.group;
      lines.push("");
      lines.push(GROUP_LABELS[field.group].toUpperCase());
    }
    const value = result[field.key];
    const flagged = isFieldFlagged(result, field.key);
    let rendered: string;
    if (value === null || value === undefined) {
      rendered = "Not found in document";
    } else if (field.key === "monthly_rent") {
      rendered = formatCurrency(value as number);
    } else {
      rendered = String(value);
    }
    lines.push(`  ${field.label.padEnd(16)} ${rendered}${flagged ? "  [NEEDS REVIEW]" : ""}`);
  }

  if (result.key_provisions?.length) {
    lines.push("");
    lines.push("KEY PROVISIONS");
    for (const item of result.key_provisions) lines.push(`  - ${item}`);
  }

  if (result.uncertainty_notes) {
    lines.push("");
    lines.push("NOTES");
    lines.push(`  ${result.uncertainty_notes}`);
  }

  return lines.join("\n");
}
