import { formatCurrency } from "@/lib/format";
import type { FieldMeta, LeaseAbstract } from "@/lib/schema";

type State = "missing" | "flagged" | "clear";

export default function FieldRow({
  field,
  value,
  flagged,
}: {
  field: FieldMeta;
  value: LeaseAbstract[FieldMeta["key"]];
  flagged: boolean;
}) {
  const missing = value === null || value === undefined || value === "";
  const state: State = missing ? "missing" : flagged ? "flagged" : "clear";

  const stripeClass = {
    missing: "bg-border",
    flagged: "bg-destructive",
    clear: "bg-primary",
  }[state];

  const display = missing
    ? "Not found in document"
    : field.key === "monthly_rent"
    ? formatCurrency(value as number)
    : String(value);

  return (
    <div className="flex items-stretch gap-4 border-b border-border py-3 last:border-b-0">
      <span className={`w-[3px] shrink-0 ${stripeClass}`} aria-hidden="true" />
      <div className="flex flex-1 flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between">
        <span className="text-xs font-medium uppercase tracking-[0.08em] text-muted-foreground">
          {field.label}
        </span>
        <span
          className={`text-sm ${missing ? "italic text-muted-foreground" : "text-foreground"} ${
            field.key === "monthly_rent" ? "tabular-nums" : ""
          }`}
        >
          {display}
        </span>
      </div>
      {state === "flagged" && (
        <span className="flex shrink-0 items-center gap-1 self-start bg-destructive-soft px-2 py-0.5 text-[0.65rem] font-medium uppercase tracking-[0.06em] text-destructive">
          Needs review
        </span>
      )}
    </div>
  );
}
