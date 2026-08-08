"use client";

import { motion } from "framer-motion";

const steps = [
  {
    n: "01",
    title: "Select a lease",
    body: "Pick one of ten sample leases or paste your own commercial lease text straight in.",
  },
  {
    n: "02",
    title: "Review the abstract",
    body: "Nine fields come back grouped the way a property manager reads a lease — parties, money, term, then the rest. Anything uncertain is flagged for review.",
  },
  {
    n: "03",
    title: "Export it",
    body: "Copy the summary, download the raw JSON, or print a clean one-page abstract to file.",
  },
];

export default function StepsSection() {
  return (
    <section className="relative overflow-hidden border-t border-border bg-background py-12 sm:py-16 md:py-20">
      <div
        className="pointer-events-none absolute top-0 left-1/2 h-px w-2/3 -translate-x-1/2 bg-gradient-to-r from-transparent via-black/10 to-transparent"
        aria-hidden="true"
      />
      <div className="relative mx-auto max-w-6xl px-4 sm:px-8 md:px-12 lg:px-16">
        <div className="mx-auto mb-8 max-w-3xl text-center sm:mb-10">
          <p className="mb-4 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground sm:text-sm">
            How it works
          </p>
          <h2 className="mb-5 text-2xl leading-tight font-semibold tracking-tight text-foreground sm:text-3xl md:text-4xl">
            From raw lease to reviewed abstract.
          </h2>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="grid gap-px border border-border bg-border md:grid-cols-3"
        >
          {steps.map((step) => (
            <div key={step.n} className="bg-background p-6 sm:p-7">
              <div className="mb-5 text-sm font-semibold text-foreground">{step.n}</div>
              <h3 className="mb-4 text-xl leading-tight font-semibold text-foreground sm:text-2xl">
                {step.title}
              </h3>
              <p className="text-sm leading-relaxed text-muted-foreground sm:text-base">
                {step.body}
              </p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
