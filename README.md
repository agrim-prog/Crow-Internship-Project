# Crow Internship Project — Lease Abstractor

Reads a commercial lease and pulls out its key terms (tenant, rent, dates,
escalation, CAM, renewal option) into clean structured JSON, so a property
team doesn't have to read the whole document by hand.

## Repo structure

- `/data` — sample lease documents and their answer keys (fake, varied —
  never real tenant/financial data)
- `/code` — the call-and-parse pipeline, the prompt experiment script, and
  the results/scoring scripts
- `/outputs` — saved JSON and CSV results from running the pipeline on our
  samples

## How to run it

1. Get an Anthropic API key. If the program hasn't issued one yet, ask
   your PM.
2. Set it as an environment variable — **never commit this key to GitHub**:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```
3. Install the one dependency:
   ```bash
   pip install anthropic
   ```
4. Run the main pipeline on all sample leases:
   ```bash
   python code/call_and_parse.py
   ```
5. Score the results against the answer keys and get the results table:
   ```bash
   python code/results_log.py
   ```

## Rules

- The API key is never committed to this repo. It lives only in each
  person's local environment variable.
- Never use real tenant, owner, or financial data — sample/fictional data only.
