# Crow Lease Abstractor

Next.js rebuild of the lease abstraction tool. The extraction pipeline (schema,
system prompt, validation rules) is ported 1:1 from `../code/call_and_parse.py`
into [`lib/pipeline.ts`](lib/pipeline.ts) — same model (`claude-sonnet-4-5`),
same prompt, same field rules. See [`lib/schema.ts`](lib/schema.ts) for the
client-safe field metadata and [`lib/pipeline.ts`](lib/pipeline.ts) for the
server-only extraction call.

## Local development

```bash
npm install
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The key lives only in
`.env.local` (gitignored) and is read server-side by
[`app/api/abstract/route.ts`](app/api/abstract/route.ts) — it is never sent to
the browser.

## Deploying on Vercel

1. Push this repo to GitHub (or connect it directly) and import it in Vercel,
   setting the **root directory to `web/`** since the Next.js app is nested
   inside the repo, not at the repo root.
2. In the Vercel project's **Settings → Environment Variables**, add
   `ANTHROPIC_API_KEY` with your key. Do this for Production (and Preview if
   you want preview deploys to work too). Never commit the key.
3. Deploy. The three routes (`/api/abstract`, `/api/samples`,
   `/api/samples/[id]`) run as Node serverless functions; the sample lease
   `.txt` files under `data/samples/` are bundled via
   `outputFileTracingIncludes` in `next.config.ts` so they're available at
   runtime on Vercel, not just locally.

No other secrets or config are required — there's no database and no other
external service.

## What's here vs. the Python pipeline

- `code/call_and_parse.py` (repo root) is the original CLI/Streamlit pipeline
  and stays as the reference implementation / batch scoring tool
  (`run_accuracy_check`, `outputs/`, `examples/`).
- `web/` is the production-facing app: same extraction logic, a proper
  animated UI, and server-side key handling suitable for public hosting.
