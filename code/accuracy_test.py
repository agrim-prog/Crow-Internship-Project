  
import json
import csv
import time
import traceback
from pathlib import Path
 

# 1. PLUG IN YOUR REAL EXTRACTION FUNCTION HERE

# Replace this import with your actual Week 3 function. It should take raw
# text and return a dict, e.g.:
#
#   from lease_extractor import extract_lease_data as EXTRACT_FUNCTION
#
# For now this is a placeholder so the script runs standalone -- delete it
# once your import is wired up.
 
def EXTRACT_FUNCTION(raw_text: str) -> dict:
    raise NotImplementedError(
        "Swap this out -- import your real extraction function at the top "
        "of accuracy_test.py instead of using this placeholder."
    )
 

SAMPLES_DIR = Path("samples")
GROUND_TRUTH_DIR = Path("ground_truth")
RESULTS_CSV = Path("results_log.csv")
 
# If True, string comparisons ignore case and surrounding whitespace.
# Dates/numbers are still compared for exact value equality after light
# normalization (see normalize_value below).
CASE_INSENSITIVE = True
 
# Values that should all be treated as the same "missing" answer. Add your
# our actual convention here if it isn't already covered.
MISSING_VALUES = {None, "null", "none", "not found", "n/a", "na", ""}
 
 

# 3. COMPARISON LOGIC

def normalize_value(value):
    """Make two equivalent values compare equal even if formatted slightly
    differently (extra whitespace, case, trailing .0 on numbers, etc.)."""
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        if CASE_INSENSITIVE:
            v = v.lower()
        if v in MISSING_VALUES:
            return None
        return v
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [normalize_value(v) for v in value]
    return value
 
 
def fields_match(expected, actual) -> bool:
    return normalize_value(expected) == normalize_value(actual)
 
 

# 4. CORE TEST LOOP

def run_accuracy_test():
    sample_files = sorted(SAMPLES_DIR.glob("*.txt"))
    if not sample_files:
        print(f"No sample .txt files found in {SAMPLES_DIR}/. "
              f"Add raw lease text files there first.")
        return
 
    rows = []
    field_correct_counts = {}   # field_name -> number of samples it was correct on
    field_total_counts = {}     # field_name -> number of samples it appeared in
    total_fields_correct = 0
    total_fields_checked = 0
    samples_fully_correct = 0
 
    for sample_path in sample_files:
        name = sample_path.stem
        truth_path = GROUND_TRUTH_DIR / f"{name}.json"
 
        if not truth_path.exists():
            print(f"[SKIP] {name}: no matching ground_truth/{name}.json found")
            continue
 
        raw_text = sample_path.read_text(encoding="utf-8")
        expected = json.loads(truth_path.read_text(encoding="utf-8"))
 
        #  run extraction, but never let one bad sample kill the run 
        try:
            start = time.time()
            actual = EXTRACT_FUNCTION(raw_text)
            elapsed = round(time.time() - start, 2)
            error_note = ""
        except Exception as e:
            actual = {}
            elapsed = None
            error_note = f"EXTRACTION ERROR: {e}"
            print(f"[FAIL] {name}: {e}")
            traceback.print_exc()
 
        #  required-field presence check 
        missing_fields = [f for f in expected if f not in actual]
        all_present = len(missing_fields) == 0
 
        #  field-by-field correctness 
        mismatches = []
        correct_count = 0
        for field, expected_value in expected.items():
            actual_value = actual.get(field, "<MISSING>")
            field_total_counts[field] = field_total_counts.get(field, 0) + 1
            if field in actual and fields_match(expected_value, actual_value):
                correct_count += 1
                field_correct_counts[field] = field_correct_counts.get(field, 0) + 1
            else:
                mismatches.append(f"{field}: expected={expected_value!r} got={actual_value!r}")
 
        total_fields = len(expected)
        total_fields_correct += correct_count
        total_fields_checked += total_fields
        fully_correct = (correct_count == total_fields) and not error_note
        if fully_correct:
            samples_fully_correct += 1
 
        notes_parts = []
        if error_note:
            notes_parts.append(error_note)
        if missing_fields:
            notes_parts.append(f"missing fields: {', '.join(missing_fields)}")
        if mismatches:
            notes_parts.append("; ".join(mismatches))
        notes = " | ".join(notes_parts) if notes_parts else "all correct"
 
        rows.append({
            "sample_name": name,
            "all_fields_present": all_present,
            "fields_correct": f"{correct_count}/{total_fields}",
            "fully_correct": fully_correct,
            "time_sec": elapsed,
            "notes": notes,
        })
 
        status = "PASS" if fully_correct else ("FLAGGED" if not error_note else "FAILED")
        print(f"[{status}] {name}: {correct_count}/{total_fields} fields correct")
 
    if not rows:
        print("No samples were tested (missing ground_truth files?). Nothing to report.")
        return
 
    #  write results_log.csv, matching the packet's log format 
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sample_name", "all_fields_present", "fields_correct",
            "fully_correct", "time_sec", "notes"
        ])
        writer.writeheader()
        writer.writerows(rows)
 
    #  summary report 
    print("\n" + "=" * 60)
    print("ACCURACY SUMMARY")
    print("=" * 60)
    print(f"Samples tested:            {len(rows)}")
    print(f"Samples fully correct:     {samples_fully_correct}/{len(rows)} "
          f"({100 * samples_fully_correct / len(rows):.1f}%)")
    print(f"Overall field accuracy:    {total_fields_correct}/{total_fields_checked} "
          f"({100 * total_fields_correct / max(total_fields_checked, 1):.1f}%)")
 
    print("\nPer-field accuracy (fix the weakest ones first):")
    for field in sorted(field_total_counts, key=lambda f: field_correct_counts.get(f, 0) / field_total_counts[f]):
        correct = field_correct_counts.get(field, 0)
        total = field_total_counts[field]
        pct = 100 * correct / total
        flag = "  <-- weakest" if pct < 70 else ""
        print(f"  {field:<25} {correct}/{total}  ({pct:.0f}%){flag}")
 
    print(f"\nFull results saved to {RESULTS_CSV}")
 
 
if __name__ == "__main__":
    run_accuracy_test()