"use client";

import { motion } from "framer-motion";

export default function Hero() {
  return (
    <section id="top" className="relative overflow-hidden bg-background pt-32 pb-16 sm:pt-40 sm:pb-20">
      {/* Same radial glow usecrow.ai uses behind its hero copy, pulled from their shipped CSS. */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(ellipse at center, rgba(16,185,129,.08) 0%, rgba(16,185,129,.03) 40%, transparent 70%)",
        }}
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute top-20 left-1/2 h-px w-2/3 -translate-x-1/2 bg-gradient-to-r from-transparent via-black/10 to-transparent"
        aria-hidden="true"
      />

      <div className="relative mx-auto max-w-3xl px-4 text-center sm:px-8 lg:px-16">
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-4 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground sm:text-sm"
        >
          Lease abstraction
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl leading-tight font-semibold tracking-tight text-foreground text-balance sm:text-5xl md:text-6xl"
        >
          Every lease, read once.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg"
        >
          Paste a commercial lease and get tenant, rent, dates, escalation, and
          CAM back as a clean abstract — every field that&rsquo;s uncertain
          flagged for review, not buried in a footnote.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 flex items-center justify-center"
        >
          <a
            href="#workbench"
            className="inline-flex items-center gap-2 bg-foreground px-6 py-3 text-sm font-medium text-background transition-colors hover:bg-foreground/85"
          >
            Open the workbench
          </a>
        </motion.div>
      </div>
    </section>
  );
}
