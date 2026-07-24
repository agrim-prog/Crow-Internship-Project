# Reads what the other two scripts already produced and turns it into the
# two write-ups Week 2 still needs: the phrasing reflection and the list
# of fields the model gets wrong, for the Week 3 plan.

import os
import json
from collections import Counter


def load_examples():
    pairs = []
    for filename in sorted(os.listdir("examples")):
        if filename.endswith("_pair.json"):
            with open(os.path.join("examples", filename)) as f:
                pairs.append(json.load(f))
    return pairs


def summarize_problem_fields(pairs):
    counts = Counter()
    for pair in pairs:
        for problem in pair["validation_problems"]:
            field = problem.split(":")[0].replace("missing field", "").strip()
            counts[field] += 1
    return counts


def summarize_prompt_experiment():
    path = "outputs/prompt_experiment_log.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    pairs = load_examples()
    if not pairs:
        print("No examples yet. Run lease_abstractor.py first.")
        raise SystemExit(1)

    print(f"Looked at {len(pairs)} leases.\n")

    problem_counts = summarize_problem_fields(pairs)
    print("Fields that came back with problems:")
    if problem_counts:
        for field, count in problem_counts.most_common():
            print(f"  {field}: wrong or missing in {count}/{len(pairs)} leases")
    else:
        print("  none - every field validated cleanly")

    experiments = summarize_prompt_experiment()
    print("\nPrompt phrasing comparison:")
    if experiments:
        for result in experiments:
            print(f"  {result['variant']} ({result['seconds']}s): {result['output'][:120]}")
    else:
        print("  run prompt_experiments.py first")

    with open("outputs/week2_summary.json", "w") as f:
        json.dump({
            "leases_checked": len(pairs),
            "problem_fields": dict(problem_counts),
            "prompt_experiments": experiments,
        }, f, indent=2)

    print("\nSaved to outputs/week2_summary.json - use the problem_fields list")
    print("as your Week 3 plan's 'fields the model currently gets wrong'.")
