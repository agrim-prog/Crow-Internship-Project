"use client";

import { motion } from "framer-motion";
import ExportBar from "./ExportBar";
import FieldRow from "./FieldRow";
import PrintableAbstract from "./PrintableAbstract";
import { isFieldFlagged } from "@/lib/format";
import { FIELD_META, GROUP_LABELS, type LeaseAbstract } from "@/lib/schema";

export type RunStatus = "idle" | "loading" | "error" | "done";

const GROUPS: Array<(typeof FIELD_META)[number]["group"]> = ["parties", "money", "term"];

export default function ResultPane({
  status,
  result,
  problems,
  errorMessage,
  sourceLabel,
  fileStem,
}: {
  status: RunStatus;
  result: LeaseAbstract | null;
  problems: string[];
  errorMessage: string | null;
  sourceLabel: string;
  fileStem: string;
}) {
  if (status === "idle") {
    return (
      <div className="flex h-full min-h-[24rem] flex-col items-center justify-center border border-dashed border-border p-10 text-center">
        <p className="text-lg font-semibold text-foreground">Nothing abstracted yet</p>
        <p className="mt-2 max-w-xs text-sm text-muted-foreground">
          Select a sample or paste a lease on the left, then run it — the result
          lands here, grouped and flagged.
        </p>
      </div>
    );
  }

  if (status === "loading") {
    return (
      <div className="space-y-6" aria-live="polite" aria-busy="true">
        {GROUPS.map((g) => (
          <div key={g}>
            <div className="mb-2 h-3 w-32 animate-pulse bg-border" />
            <div className="space-y-3 border border-border p-4">
              {FIELD_META.filter((f) => f.group === g).map((f) => (
                <div key={f.key} className="h-4 w-full animate-pulse bg-border/70" />
              ))}
            </div>
          </div>
        ))}
        <p className="text-center text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">
          Reading the lease…
        </p>
      </div>
    );
  }

  if (status === "error" || !result) {
    return (
      <div className="border border-destructive/30 bg-destructive-soft p-6">
        <p className="text-lg font-semibold text-destructive">Couldn&rsquo;t abstract this lease</p>
        <p className="mt-2 text-sm text-foreground">
          {errorMessage ?? "Unknown error."}
        </p>
        {problems.length > 0 && (
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-foreground">
            {problems.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <ExportBar result={result} sourceLabel={sourceLabel} fileStem={fileStem} />
      <PrintableAbstract result={result} sourceLabel={sourceLabel} />

      {GROUPS.map((group) => (
        <div key={group}>
          <h3 className="mb-1 text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
            {GROUP_LABELS[group]}
          </h3>
          <div className="border border-border bg-card px-4">
            {FIELD_META.filter((f) => f.group === group).map((field) => (
              <FieldRow
                key={field.key}
                field={field}
                value={result[field.key]}
                flagged={isFieldFlagged(result, field.key)}
              />
            ))}
          </div>
        </div>
      ))}

      {(result.key_provisions?.length > 0 || result.uncertainty_notes) && (
        <div>
          <h3 className="mb-1 text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
            {GROUP_LABELS.other}
          </h3>
          <div className="space-y-4 border border-border bg-card p-4">
            {result.key_provisions?.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {result.key_provisions.map((item, i) => (
                  <span
                    key={i}
                    className="border border-border px-3 py-1 text-sm text-foreground"
                  >
                    {item}
                  </span>
                ))}
              </div>
            )}
            {result.uncertainty_notes && (
              <div className="border-l-2 border-primary bg-background px-4 py-3">
                <p className="text-[0.65rem] font-medium uppercase tracking-[0.1em] text-primary">
                  Uncertainty notes
                </p>
                <p className="mt-1 text-sm leading-relaxed text-foreground">
                  {result.uncertainty_notes}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {problems.length > 0 && (
        <div className="border border-border bg-muted p-4">
          <p className="text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">
            Validation issues
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-foreground">
            {problems.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}
