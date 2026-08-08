# Crow Internship Project — Lease Abstractor

Reads a commercial lease and pulls out its key terms (tenant, rent, dates,
escalation, CAM, renewal option) into clean structured JSON, so a property
team doesn't have to read the whole document by hand.

## Repo structure

- `/data` — sample lease documents and their answer keys (fake, varied —
  never real tenant/financial data)
- `/code` — the call-and-parse pipeline, the Streamlit app, the prompt
  experiment script, and the results/scoring scripts
- `/outputs` — saved JSON and CSV results from running the pipeline on our
  samples

Two ways to use it:

- `code/app.py` — the Streamlit web app. Pick a sample lease or paste your
  own, hit a button, watch it get abstracted. This is the one to look at
  first.
- `code/call_and_parse.py` — the original command-line pipeline. The app
  calls the exact same extraction function, it just gives it a face.

## Setup

Do this once.

1. Get an Anthropic API key. If the program hasn't issued one yet, ask
   your PM.
2. Set it as an environment variable — **never commit this key to GitHub**:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```
   Put that line in your `~/.zshrc` (or `~/.bashrc`) so it survives new
   terminal windows. Alternatively, copy `.env.example` to `.env.local` and
   fill in your key there — but note that `.env.local` only works for the
   Streamlit app, not the command-line scripts (see Troubleshooting).
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the web app

```bash
streamlit run code/app.py
```

That opens http://localhost:8501 in your browser. If it doesn't open by
itself, go to that address manually.

## Running the command-line scripts

Run the pipeline on all sample leases:

```bash
python code/call_and_parse.py
```

Score the results against the answer keys and get the results table:

```bash
python code/results_log.py
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'streamlit'`** — you skipped
step 3. Run `pip install -r requirements.txt`. The old instructions in
this README said `pip install anthropic`, which isn't enough anymore.

**`KeyError: 'ANTHROPIC_API_KEY'` when running a `python code/...`
script** — the command-line scripts read the key straight from your
environment and don't load `.env.local`. Export the variable in your
shell (step 2) and run again.

**The app loads but shows "ANTHROPIC_API_KEY is not set"** — the app does
read `.env.local`, so either that file is missing/misspelled, or you
exported the key in a different terminal than the one running Streamlit.
Restart the app from a shell where `echo $ANTHROPIC_API_KEY` prints your
key.

**You don't see the app at all** — make sure you actually have the latest
code: `git pull origin main`, then confirm `code/app.py` exists.

**Port 8501 is already in use** — you have an old copy running. Either use
that browser tab, or start on another port:
`streamlit run code/app.py --server.port 8502`.

## Deploying it (so nobody has to run it locally)

The app is hosted on [Streamlit Community Cloud](https://share.streamlit.io),
which is free and runs straight off this repo. Note that it will **not**
deploy to Vercel — Streamlit needs a persistent server holding an open
WebSocket per user, and Vercel only runs short-lived serverless functions.

To deploy or redeploy:

1. Go to https://share.streamlit.io and sign in with GitHub. Because this
   repo is private, grant Streamlit private-repo access under
   *Settings → Linked accounts*.
2. Click **Create app → Deploy a public app from GitHub** and fill in:
   - Repository: `agrim-prog/Crow-Internship-Project`
   - Branch: `main`
   - Main file path: `code/app.py`
3. Open **Advanced settings** and paste this into the Secrets box, in TOML:
   ```toml
   ANTHROPIC_API_KEY = "the-key-here"
   ```
   It has to be a root-level key like that. Streamlit only exposes
   root-level secrets as environment variables, and that's what the
   pipeline reads. Nesting it under a `[section]` will break the app.
4. Deploy. Every push to `main` redeploys automatically.

Two things worth knowing:

- **You need admin access on the repo to deploy it.** Pushing isn't
  enough. If GitHub doesn't list the repo, ask the repo owner to either
  deploy it from their account or give you admin.
- The deployed app runs on whatever key you paste into Secrets, and
  anyone with the URL can spend it. Keep the app private in
  *Settings → Sharing* if that's a concern.

## Rules

- The API key is never committed to this repo. It lives only in each
  person's local environment variable or their own gitignored `.env.local`.
- Never use real tenant, owner, or financial data — sample/fictional data only.

## Known Limitations

- **Date conflict detection can be overcautious.** The tool flags any lease
  with two different dates mentioned for the same term, even when one date
  is clearly a resolved estimate and the other is an explicit legal
  override (e.g., "the date shall be deemed X, regardless of..."). In
  testing, this caused a correct, resolvable date to be flagged as
  uncertain rather than computed. We chose not to fix this: for a tool
  handling real lease obligations, a false "needs review" is a much safer
  failure than a false confident answer. A human spending 30 extra seconds
  confirming a date they'd have confirmed anyway costs far less than the
  tool silently guessing wrong on a genuine conflict.

## Accuracy

Tested against 10 sample leases (including tricky cases: missing fields,
stepped/percentage rent, vague clauses). **100.0% field accuracy** after
fixing a scoring bug that penalized correct paraphrased answers. See
IMPROVEMENT_LOG.md for the full before/after story and adversarial
testing results.
