# Runs every sample through call_and_parse, checks it against the answer
# key if one exists, and writes one row per sample: sample name, all

import os
import sys
import json
import csv

sys.path.insert(0, os.path.dirname(__file__))
from call_and_parse import call_and_parse_pipeline, REQUIRED_FIELDS


def score_against_truth(result, truth):
    matches = 0
    for key, true_val in truth.items():
        pred_val = result.get(key)
        if isinstance(true_val, str) and isinstance(pred_val, str):
            is_match = true_val.strip().lower() == pred_val.strip().lower()
        else:
            is_match = pred_val == true_val
        matches += is_match
    return matches, len(truth)


if __name__ == "__main__":
    rows = []

    for filename in sorted(f for f in os.listdir("data") if f.endswith(".txt")):
        stem = filename.replace(".txt", "")
        lease_text = open(os.path.join("data", filename)).read()

        result, problems = call_and_parse_pipeline(lease_text)

        if result is None:
            rows.append([stem, "no", "0/0", "failed to parse response"])
            continue

        all_present = all(f in result for f in REQUIRED_FIELDS)

        truth_path = os.path.join("data", f"{stem}_truth.json")
        if os.path.exists(truth_path):
            truth = json.load(open(truth_path))
            matches, total = score_against_truth(result, truth)
            fields_correct = f"{matches}/{total}"
        else:
            fields_correct = "no answer key"

        notes = "; ".join(problems) if problems else "clean"
        rows.append([stem, "yes" if all_present else "no", fields_correct, notes])

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_name", "all_fields_present", "fields_correct", "notes"])
        writer.writerows(rows)

    print(f"{'sample':<12} {'all present':<13} {'correct':<10} notes")
    for row in rows:
        print(f"{row[0]:<12} {row[1]:<13} {row[2]:<10} {row[3]}")

    print("\nSaved to outputs/results_log.csv")
