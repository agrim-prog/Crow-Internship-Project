"use client";

import type { SampleMeta } from "@/lib/samples";

export default function DocumentPane({
  samples,
  mode,
  selectedId,
  documentText,
  loadingSample,
  loadingRun,
  onSelectSample,
  onSelectPaste,
  onTextChange,
  onRun,
}: {
  samples: SampleMeta[];
  mode: "sample" | "paste";
  selectedId: string | null;
  documentText: string;
  loadingSample: boolean;
  loadingRun: boolean;
  onSelectSample: (id: string) => void;
  onSelectPaste: () => void;
  onTextChange: (value: string) => void;
  onRun: () => void;
}) {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onSelectPaste}
          className={`border px-3.5 py-1.5 text-xs font-medium uppercase tracking-[0.06em] transition-colors ${
            mode === "paste"
              ? "border-foreground bg-foreground text-background"
              : "border-border text-muted-foreground hover:border-foreground hover:text-foreground"
          }`}
        >
          Paste my own
        </button>
        {samples.map((s) => (
          <button
            key={s.id}
            type="button"
            onClick={() => onSelectSample(s.id)}
            className={`border px-3.5 py-1.5 text-xs font-medium uppercase tracking-[0.06em] transition-colors ${
              mode === "sample" && selectedId === s.id
                ? "border-foreground bg-foreground text-background"
                : "border-border text-muted-foreground hover:border-foreground hover:text-foreground"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      <div className="relative flex-1 border border-border bg-card">
        {mode === "paste" ? (
          <textarea
            value={documentText}
            onChange={(e) => onTextChange(e.target.value)}
            placeholder="Paste the full text of a commercial lease here…"
            className="h-full min-h-96 w-full resize-none bg-transparent p-5 text-sm leading-relaxed text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
        ) : loadingSample ? (
          <div className="flex h-full min-h-96 items-center justify-center">
            <p className="text-xs font-medium uppercase tracking-[0.1em] text-muted-foreground">
              Loading sample…
            </p>
          </div>
        ) : (
          <pre className="h-full min-h-96 max-h-[32rem] overflow-auto whitespace-pre-wrap p-5 text-sm leading-relaxed text-foreground">
            {documentText}
          </pre>
        )}
      </div>

      <button
        type="button"
        onClick={onRun}
        disabled={!documentText.trim() || loadingRun}
        className="mt-5 inline-flex items-center justify-center gap-2 bg-foreground px-6 py-3 text-sm font-medium text-background transition-colors hover:bg-foreground/85 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loadingRun ? "Abstracting…" : "Abstract this lease"}
      </button>
    </div>
  );
}
