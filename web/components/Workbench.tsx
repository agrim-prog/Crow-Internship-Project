"use client";

import { useEffect, useState } from "react";
import DocumentPane from "./DocumentPane";
import ResultPane, { type RunStatus } from "./ResultPane";
import type { SampleMeta } from "@/lib/samples";
import type { LeaseAbstract } from "@/lib/schema";

export default function Workbench() {
  const [samples, setSamples] = useState<SampleMeta[]>([]);
  const [mode, setMode] = useState<"sample" | "paste">("sample");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [documentText, setDocumentText] = useState("");
  const [pastedText, setPastedText] = useState("");
  const [loadingSample, setLoadingSample] = useState(false);

  const [status, setStatus] = useState<RunStatus>("idle");
  const [result, setResult] = useState<LeaseAbstract | null>(null);
  const [problems, setProblems] = useState<string[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/samples")
      .then((r) => r.json())
      .then((data: { samples: SampleMeta[] }) => {
        if (cancelled) return;
        setSamples(data.samples);
        if (data.samples.length > 0) {
          void selectSample(data.samples[0].id);
        }
      })
      .catch(() => {
        if (!cancelled) setSamples([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function selectSample(id: string) {
    setMode("sample");
    setSelectedId(id);
    setLoadingSample(true);
    setStatus("idle");
    try {
      const res = await fetch(`/api/samples/${id}`);
      const data = await res.json();
      setDocumentText(data.text ?? "");
    } finally {
      setLoadingSample(false);
    }
  }

  function selectPaste() {
    setMode("paste");
    setSelectedId(null);
    setDocumentText(pastedText);
    setStatus("idle");
  }

  function handleTextChange(value: string) {
    setPastedText(value);
    setDocumentText(value);
  }

  async function runAbstraction() {
    if (!documentText.trim()) return;
    setStatus("loading");
    setErrorMessage(null);
    try {
      const res = await fetch("/api/abstract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: documentText }),
      });
      const data = await res.json();
      if (!res.ok) {
        setStatus("error");
        setErrorMessage(data.error ?? "Request failed.");
        setProblems([]);
        return;
      }
      if (!data.result) {
        setStatus("error");
        setErrorMessage("The model's response couldn't be parsed as a lease abstract.");
        setProblems(data.problems ?? []);
        return;
      }
      setResult(data.result);
      setProblems(data.problems ?? []);
      setStatus("done");
    } catch (e) {
      setStatus("error");
      setErrorMessage(e instanceof Error ? e.message : "Network error.");
    }
  }

  const sourceLabel =
    mode === "sample"
      ? samples.find((s) => s.id === selectedId)?.label ?? "Pasted lease"
      : "Pasted lease";
  const fileStem = mode === "sample" && selectedId ? selectedId : "lease";

  return (
    <section id="workbench" className="mx-auto max-w-6xl px-4 py-20 sm:px-8 lg:px-16">
      <div className="mb-10 max-w-xl">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground sm:text-sm">
          The workbench
        </p>
        <h2 className="mt-3 text-2xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Run a lease, see what needs a second look
        </h2>
      </div>

      <div className="grid gap-10 lg:grid-cols-2 lg:gap-12">
        <DocumentPane
          samples={samples}
          mode={mode}
          selectedId={selectedId}
          documentText={documentText}
          loadingSample={loadingSample}
          loadingRun={status === "loading"}
          onSelectSample={selectSample}
          onSelectPaste={selectPaste}
          onTextChange={handleTextChange}
          onRun={runAbstraction}
        />
        <ResultPane
          status={status}
          result={result}
          problems={problems}
          errorMessage={errorMessage}
          sourceLabel={sourceLabel}
          fileStem={fileStem}
        />
      </div>
    </section>
  );
}
