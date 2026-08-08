// Client-safe: types and static field metadata only. No SDK, no secrets.
// Keep this split from pipeline.ts, which is server-only — importing a plain
// value (FIELD_META, GROUP_LABELS) from a "server-only"-guarded module drags
// the Anthropic SDK into the browser bundle even for a type-only need.

export interface ReviewFlags {
  cam_unclear: boolean;
  renewal_option_unclear: boolean;
  date_conflict: boolean;
}

export interface LeaseAbstract {
  tenant_name: string | null;
  property_address: string | null;
  monthly_rent: number | null;
  lease_start: string | null;
  lease_end: string | null;
  escalation: string | null;
  cam: string | null;
  renewal_option: string | null;
  key_provisions: string[];
  review_flags: ReviewFlags;
  uncertainty_notes: string | null;
}

export const LEASE_ABSTRACT_SCHEMA = {
  tenant_name: "string or null",
  property_address: "string or null",
  monthly_rent: "number or null - no dollar sign, no commas",
  lease_start: "YYYY-MM-DD or null",
  lease_end: "YYYY-MM-DD or null",
  escalation: "string or null",
  cam: "string or null",
  renewal_option: "string or null",
  key_provisions: ["list of other notable clauses or restrictions"],
  review_flags: {
    cam_unclear: "boolean",
    renewal_option_unclear: "boolean",
    date_conflict: "boolean",
  },
  uncertainty_notes: "string or null - anything ambiguous a human should check",
};

export const REQUIRED_FIELDS = Object.keys(LEASE_ABSTRACT_SCHEMA) as Array<
  keyof LeaseAbstract
>;

export type ExpectedKind = "string" | "number" | "array" | "object";

export const FIELD_TYPES: Record<keyof LeaseAbstract, ExpectedKind> = {
  tenant_name: "string",
  property_address: "string",
  monthly_rent: "number",
  lease_start: "string",
  lease_end: "string",
  escalation: "string",
  cam: "string",
  renewal_option: "string",
  key_provisions: "array",
  review_flags: "object",
  uncertainty_notes: "string",
};

export interface FieldMeta {
  key: keyof LeaseAbstract;
  label: string;
  group: "parties" | "money" | "term" | "other";
}

// Order = the way a property manager reads a lease: who and where, then the
// money, then the term, then everything else worth a second look.
export const FIELD_META: FieldMeta[] = [
  { key: "tenant_name", label: "Tenant", group: "parties" },
  { key: "property_address", label: "Address", group: "parties" },
  { key: "monthly_rent", label: "Monthly rent", group: "money" },
  { key: "escalation", label: "Escalation", group: "money" },
  { key: "cam", label: "CAM", group: "money" },
  { key: "lease_start", label: "Lease start", group: "term" },
  { key: "lease_end", label: "Lease end", group: "term" },
  { key: "renewal_option", label: "Renewal option", group: "term" },
];

export const GROUP_LABELS: Record<FieldMeta["group"], string> = {
  parties: "Parties & property",
  money: "Money",
  term: "Term",
  other: "Other",
};
