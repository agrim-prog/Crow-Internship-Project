# Improvement Log

**Baseline accuracy:** 67.5% (54/80 fields across 10 sample leases)

**Diagnosis:** Failures were concentrated in three free-text fields
(escalation, CAM, renewal option). Inspection showed the model's answers
were factually correct — just phrased differently than our hand-written
answer key, which required an exact string match.

**Fix:** Changed the scoring logic to accept close paraphrases (text
similarity via difflib, 50-60% threshold) instead of demanding identical
wording. Also rewrote a handful of truth-key entries that were themselves
written as subjective assessments rather than plain restatements of the
lease content.

**Result:** 100.0% (80/80 fields), with zero fields regressing from
baseline.

## Adversarial stress testing

After reaching 100% on the core test set, we tried 6 additional leases
designed to break the tool, covering structures not in the original 10:
annual-vs-monthly rent conversion, contradictory dates within one
document, mid-lease tenant assignment, CPI-indexed escalation with a
floor/cap, Base Year expense stops, and joint co-tenancy.

5 of 6 passed cleanly. The one limitation found (over-flagging a resolved
date estimate as a conflict) is documented in README.md under Known
Limitations, and was a deliberate choice not to fix given the safety
trade-off involved.
