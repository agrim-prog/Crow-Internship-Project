"use client";

import { useState } from "react";
import { formatSummaryText } from "@/lib/format";
import type { LeaseAbstract } from "@/lib/schema";

export default function ExportBar({
  result,
  sourceLabel,
  fileStem,
}: {
  result: LeaseAbstract;
  sourceLabel: string;
  fileStem: string;
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(formatSummaryText(result, sourceLabel));
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  function handleDownload() {
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${fileStem}_abstract.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handlePrint() {
    window.print();
  }

  return (
    <div className="no-print flex flex-wrap items-center gap-2 border-b border-border pb-4">
      <button
        type="button"
        onClick={handleCopy}
        className="inline-flex items-center gap-1.5 border border-border px-3.5 py-1.5 text-xs font-medium uppercase tracking-[0.06em] text-foreground transition-colors hover:border-foreground"
      >
        {copied ? "Copied" : "Copy summary"}
      </button>
      <button
        type="button"
        onClick={handleDownload}
        className="inline-flex items-center gap-1.5 border border-border px-3.5 py-1.5 text-xs font-medium uppercase tracking-[0.06em] text-foreground transition-colors hover:border-foreground"
      >
        Download JSON
      </button>
      <button
        type="button"
        onClick={handlePrint}
        className="inline-flex items-center gap-1.5 border border-border px-3.5 py-1.5 text-xs font-medium uppercase tracking-[0.06em] text-foreground transition-colors hover:border-foreground"
      >
        Print / Save PDF
      </button>
    </div>
  );
}
