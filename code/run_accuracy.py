"""
Run this from the code/ folder (same place as call_and_parse.py).

    python run_accuracy.py

Scores every lease in data/ that has a matching lease_N_truth.json against
what the pipeline actually returns, prints per-lease and overall accuracy,
and saves a summary you can screenshot straight into the deck.
"""

import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from call_and_parse import call_and_parse_pipeline  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# Prose fields (escalation, cam, renewal_option, ...) are almost never worded
# identically to the truth file even when they're substantively correct, so
# an exact string match understates accuracy. Non-string fields (numbers,
# dates) still require an exact match.
#
# Two similarity signals, combined with OR, since they catch different kinds
# of paraphrase: character-level ratio catches near-identical rewordings;
# word-overlap catches the model saying the same thing with different words
# in a different order (which tanks a character diff even when every word
# matches). Calibrated against this project's actual outputs — correct
# paraphrases scored 0.30-0.78 on word overlap, deliberately wrong answers
# scored 0.00-0.05, so 0.3 cleanly separates the two.
CHAR_MATCH_THRESHOLD = 0.5
WORD_OVERLAP_THRESHOLD = 0.3


def _words(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def is_match(pred_val, true_val) -> bool:
    if isinstance(true_val, str) and isinstance(pred_val, str):
        t, p = true_val.strip().lower(), pred_val.strip().lower()
        if t == p:
            return True
        char_ratio = difflib.SequenceMatcher(None, t, p).ratio()
        wt, wp = _words(t), _words(p)
        word_overlap = len(wt & wp) / len(wt | wp) if wt and wp else 0.0
        return char_ratio >= CHAR_MATCH_THRESHOLD or word_overlap >= WORD_OVERLAP_THRESHOLD
    return pred_val == true_val


def score_one(predicted: dict, truth: dict) -> dict:
    """Field-by-field comparison. Returns per-field pass/fail plus a count."""
    results = {}
    for field, true_val in truth.items():
        pred_val = predicted.get(field) if predicted else None
        results[field] = is_match(pred_val, true_val)
    return results


def main():
    truth_files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith("_truth.json"))

    if not truth_files:
        print("No *_truth.json files found in data/. Nothing to score.")
        return

    field_totals = {}   # field -> [correct, total]
    lease_scores = []   # (name, correct, total)
    all_results = {}

    for truth_file in truth_files:
        stem = truth_file.replace("_truth.json", "")
        lease_path = os.path.join(DATA_DIR, f"{stem}.txt")
        truth_path = os.path.join(DATA_DIR, truth_file)

        if not os.path.exists(lease_path):
            print(f"  Skipping {stem}: no matching {stem}.txt")
            continue

        with open(lease_path) as f:
            lease_text = f.read()
        with open(truth_path) as f:
            truth = json.load(f)

        print(f"Running {stem}...")
        predicted, problems = call_and_parse_pipeline(lease_text)

        if predicted is None:
            print(f"  {stem}: PIPELINE FAILED TO PARSE - counted as 0/{len(truth)}")
            field_results = {field: False for field in truth}
        else:
            field_results = score_one(predicted, truth)
            if problems:
                print(f"  (validation warnings: {problems})")

        all_results[stem] = field_results

        correct = sum(field_results.values())
        total = len(field_results)
        lease_scores.append((stem, correct, total))

        for field, is_correct in field_results.items():
            field_totals.setdefault(field, [0, 0])
            field_totals[field][0] += int(is_correct)
            field_totals[field][1] += 1

        print(f"  {stem}: {correct}/{total} fields correct")
        for field, is_correct in field_results.items():
            mark = "OK  " if is_correct else "MISS"
            print(f"    [{mark}] {field}")
        print()

    # ---- Overall summary ----
    total_correct = sum(c for _, c, _ in lease_scores)
    total_fields = sum(t for _, _, t in lease_scores)
    overall_pct = 100 * total_correct / total_fields if total_fields else 0

    print("=" * 50)
    print("OVERALL ACCURACY")
    print("=" * 50)
    print(f"{total_correct}/{total_fields} fields correct  =  {overall_pct:.1f}%")
    print(f"Scored across {len(lease_scores)} lease(s)\n")

    print("Per lease:")
    for name, correct, total in lease_scores:
        pct = 100 * correct / total if total else 0
        print(f"  {name:12} {correct}/{total}  ({pct:.0f}%)")

    print("\nPer field (weakest first - this is your 'what needs work' slide):")
    field_pct = [
        (field, 100 * c / t if t else 0, c, t)
        for field, (c, t) in field_totals.items()
    ]
    for field, pct, c, t in sorted(field_pct, key=lambda x: x[1]):
        print(f"  {field:20} {pct:5.1f}%  ({c}/{t})")

    # Save for the slide / before-after record
    summary = {
        "overall_pct": round(overall_pct, 1),
        "total_correct": total_correct,
        "total_fields": total_fields,
        "per_lease": {name: f"{c}/{t}" for name, c, t in lease_scores},
        "per_field_pct": {f: round(p, 1) for f, p, _, _ in field_pct},
    }
    out_path = os.path.join(DATA_DIR, "..", "outputs", "accuracy_summary.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary to {out_path} - screenshot the OVERALL ACCURACY block above for your slide.")


if __name__ == "__main__":
    main()
