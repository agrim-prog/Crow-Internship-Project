# Runs the same extraction instruction worded a few different ways on one
# lease, so we can see how much phrasing actually changes the output.

import os
import json
import time
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-5"

PROMPT_VARIANTS = {
    "plain": "Pull out the tenant name, monthly rent, and lease end date from this lease.",

    "structured": (
        "Read this lease and return the tenant name, monthly rent, and lease "
        "end date as JSON with keys tenant_name, monthly_rent, lease_end. "
        "Return ONLY valid JSON, no other text."
    ),

    "structured_with_example": (
        "Read this lease and return ONLY valid JSON, no other text, matching "
        'this shape: {"tenant_name": "", "monthly_rent": 0, "lease_end": "YYYY-MM-DD"}. '
        "monthly_rent must be a number, not a string."
    ),
}


def run_variant(label, instruction, lease_text):
    prompt = f"{instruction}\n\n<lease_text>\n{lease_text}\n</lease_text>"

    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - start

    return {
        "variant": label,
        "instruction": instruction,
        "output": response.content[0].text,
        "seconds": round(elapsed, 2),
    }


if __name__ == "__main__":
    sample_path = os.path.join("data", sorted(os.listdir("data"))[0])
    lease_text = open(sample_path).read()

    print(f"Testing on {sample_path}\n")

    results = []
    for label, instruction in PROMPT_VARIANTS.items():
        result = run_variant(label, instruction, lease_text)
        results.append(result)

        print(f"--- {label} ({result['seconds']}s) ---")
        print(result["output"])
        print()

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/prompt_experiment_log.json", "w") as f:
        json.dump(results, f, indent=2)
