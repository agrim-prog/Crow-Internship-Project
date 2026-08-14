# The whole flow: read a lease, ask Claude to abstract it, clean up the reply,
# parse it, sanity-check it, and print/save the result.

import os
import json
import difflib
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-sonnet-4-5"

LEASE_ABSTRACT_SCHEMA = {
    "tenant_name": "string or null",
    "property_address": "string or null",
    "monthly_rent": "number or null - no dollar sign, no commas",
    "lease_start": "YYYY-MM-DD or null",
    "lease_end": "YYYY-MM-DD or null",
    "escalation": "string or null",
    "cam": "string or null",
    "renewal_option": "string or null",
    "key_provisions": ["list of other notable clauses or restrictions"],
    "review_flags": {
        "cam_unclear": "boolean",
        "renewal_option_unclear": "boolean",
        "date_conflict": "boolean",
    },
    "uncertainty_notes": "string or null - anything ambiguous a human should check",
}

REQUIRED_FIELDS = list(LEASE_ABSTRACT_SCHEMA.keys())

# What each field should look like once we've parsed the JSON back.
FIELD_TYPES = {
    "tenant_name": str,
    "property_address": str,
    "monthly_rent": (int, float),
    "lease_start": str,
    "lease_end": str,
    "escalation": str,
    "cam": str,
    "renewal_option": str,
    "key_provisions": list,
    "review_flags": dict,
    "uncertainty_notes": str,
}


SYSTEM_PROMPT = """You are an expert commercial real estate analyst specializing in lease abstraction.

Return ONLY valid JSON matching the schema. No other text, no markdown fences, no explanation.

Field rules:
- monthly_rent: a NUMBER, not a string. Amounts may be written in words
  ("Two Thousand Seven Hundred Seventy-Five and 00/100 Dollars") - convert to 2775.00.
- lease_start / lease_end: format YYYY-MM-DD. If the lease states an explicit
  calendar date (e.g. "expiring on December 31, 2028"), extract that date even
  if a duration is also mentioned in the same sentence ("a term of twenty-four
  months, expiring on December 31, 2028" -> the stated date, not a calculation).
  Only return null when no explicit date is given at all - just a bare duration
  with nothing to read a date from, or a term set out in an attachment or
  schedule not included in the text. Do NOT calculate or infer a date yourself
  from a stated duration when no explicit date is given.
- key_provisions: an array of short strings. Empty array if none stand out.

Missing vs unclear are DIFFERENT states and must not be collapsed:
- A field genuinely not stated anywhere -> null, and leave its review flag false.
- A field that IS present but worded so vaguely you are not confident ->
  give your best reading AND set its review flag true.
- A field the lease acknowledges but defers to a separate attachment, exhibit,
  or operating agreement not included in the text -> that deferral IS the
  answer. Capture it as the value (e.g. "Addressed in a separate operating
  agreement not attached") rather than returning null - null means the lease
  never brings the topic up at all, not that the details live elsewhere.

Date conflicts: if the document states two different values for the same
date (e.g. two different expiration dates in different sections), do NOT
silently pick one. Set lease_start and/or lease_end to null (whichever is
contradicted), set review_flags.date_conflict to true, and explain the
exact conflict — quoting or citing both sections — in uncertainty_notes.

Never invent a value. Never infer one from an unrelated clause."""

def build_prompt(raw_lease_text: str) -> str:
    return (
        f"Abstract this lease:\n\n<lease_text>\n{raw_lease_text}\n</lease_text>\n\n"
        f"Target schema:\n{json.dumps(LEASE_ABSTRACT_SCHEMA, indent=2)}"
    )


def validate(parsed: dict) -> list:
    """
    Look over the parsed object and collect anything that's off. We return a
    list instead of raising so one broken field doesn't hide the other ten.
    """
    problems = []

    for field in REQUIRED_FIELDS:
        if field not in parsed:
            problems.append(f"missing field: {field}")
            continue

        value = parsed[field]
        if value is None:
            continue  # null is fine for most fields, so leave it alone

        expected = FIELD_TYPES[field]
        if not isinstance(value, expected):
            got = type(value).__name__
            problems.append(f"{field}: expected {expected}, got {got} ({value!r})")

    # Dates should be YYYY-MM-DD - quick shape check, nothing fancy.
    for date_field in ("lease_start", "lease_end"):
        value = parsed.get(date_field)
        if isinstance(value, str):
            parts = value.split("-")
            if len(value) != 10 or len(parts) != 3 or not all(p.isdigit() for p in parts):
                problems.append(f"{date_field}: expected YYYY-MM-DD, got {value!r}")

    # Both review flags need to be there and actually booleans.
    # All review flags need to be there and actually booleans.
    flags = parsed.get("review_flags")
    if isinstance(flags, dict):
        for flag in ("cam_unclear", "renewal_option_unclear", "date_conflict"):
            if flag not in flags:
                problems.append(f"review_flags missing: {flag}")
            elif not isinstance(flags[flag], bool):
                problems.append(f"review_flags.{flag}: expected boolean, got {flags[flag]!r}")

    return problems


def call_and_parse_pipeline(raw_lease_text: str, on_first_token=None):
    """
    Give it raw lease text, get back (parsed_dict, problems).

    parsed_dict comes back None only when we couldn't parse the response at all.
    That's a different thing from a lease where every field just happens to be blank.

    on_first_token, if given, is called once when the first token of the reply
    lands. The request is streamed so that boundary exists at all: everything
    before it is the model reading the lease, everything after is it writing the
    abstract. The UI draws its two progress phases from that split.
    """
    try:
        chunks = []
        with client.messages.stream(
            model=MODEL,
            max_tokens=2000,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(raw_lease_text)}],
        ) as stream:
            for text in stream.text_stream:
                if not chunks and on_first_token is not None:
                    on_first_token()
                chunks.append(text)
    except Exception as e:
        print(f"[Error] API call failed: {e}")
        return None, [f"API call failed: {e}"]

    raw_output = "".join(chunks)

    # Models sometimes wrap the JSON in chatter, so just grab everything
    # between the first { and the last }.
    start = raw_output.find("{")
    end = raw_output.rfind("}")
    if start == -1 or end == -1 or end < start:
        print("[Error] No JSON object in the response.")
        print(f"        Raw response: {raw_output[:300]}")
        return None, ["parse failed: no JSON object found"]

    try:
        parsed = json.loads(raw_output[start:end + 1])
    except json.JSONDecodeError as e:
        print(f"[Error] JSON decode failed: {e}")
        print(f"        Raw response: {raw_output[:300]}")
        return None, [f"parse failed: {e}"]

    return parsed, validate(parsed)


LABELS = {
    "tenant_name": "Tenant",
    "property_address": "Address",
    "monthly_rent": "Monthly rent",
    "lease_start": "Lease start",
    "lease_end": "Lease end",
    "escalation": "Escalation",
    "cam": "CAM",
    "renewal_option": "Renewal option",
}


def print_readable_preview(parsed: dict, problems: list):
    """Print a tidy labeled summary so you can eyeball the result in the terminal."""
    print("\n" + "=" * 52)
    print("            LEASE ABSTRACT")
    print("=" * 52)

    for key, label in LABELS.items():
        value = parsed.get(key)
        if value is None:
            print(f"  {label:<16}  -  not stated in lease")
        elif key == "monthly_rent":
            print(f"  {label:<16}  ${value:,.2f}")
        else:
            print(f"  {label:<16}  {value}")

    provisions = parsed.get("key_provisions") or []
    if provisions:
        print("\n  Key provisions:")
        for item in provisions:
            print(f"    - {item}")

    flags = parsed.get("review_flags") or {}
    raised = [name.replace("_unclear", "") for name, on in flags.items() if on]
    if raised:
        print(f"\n  NEEDS HUMAN REVIEW: {', '.join(raised)}")

    notes = parsed.get("uncertainty_notes")
    if notes:
        print(f"  Notes: {notes}")

    if problems:
        print("\n  VALIDATION PROBLEMS:")
        for problem in problems:
            print(f"    - {problem}")

    print("=" * 52 + "\n")


def run_accuracy_check(model_output: dict, ground_truth: dict):
    """
    Compare the model's output to a hand-written answer key, one field at a time.

    We only score the fields that actually show up in the answer key, so you can
    start with the easy structured fields and fill in the prose ones later.
    """
    print("--- Accuracy scorecard ---")
    matches = 0

    for key, true_val in ground_truth.items():
        pred_val = model_output.get(key)

        # For strings, allow a close paraphrase instead of demanding an
        # identical sentence for information that's actually correct.
        if isinstance(true_val, str) and isinstance(pred_val, str):
            t = true_val.strip().lower()
            p = pred_val.strip().lower()
            similarity = difflib.SequenceMatcher(None, t, p).ratio()
            is_match = (t == p) or (similarity >= 0.5)
        else:
            is_match = pred_val == true_val

        if is_match:
            matches += 1
            print(f"  [PASS] {key}")
        else:
            print(f"  [FAIL] {key}  expected: {true_val!r}  got: {pred_val!r}")

    score = (matches / len(ground_truth)) * 100
    print(f"  Accuracy: {score:.1f}%  ({matches}/{len(ground_truth)} fields)\n")
    return score


if __name__ == "__main__":
    for folder in ("data", "outputs", "examples"):
        os.makedirs(folder, exist_ok=True)

    sample_files = sorted(f for f in os.listdir("data") if f.endswith(".txt"))

    if not sample_files:
        print("No .txt files in /data. Add your Week 1 sample leases there.")
        raise SystemExit(1)

    scores = []

    for filename in sample_files:
        print(f"\nProcessing {filename}...")

        with open(os.path.join("data", filename)) as f:
            lease_text = f.read()

        result, problems = call_and_parse_pipeline(lease_text)

        if result is None:
            print(f"  Skipped {filename} - could not parse response.\n")
            continue

        print_readable_preview(result, problems)

        stem = filename.replace(".txt", "")

        with open(os.path.join("outputs", f"{stem}_abstract.json"), "w") as out_f:
            json.dump(result, out_f, indent=2)

        # Stash the input/output pair so we can reuse good ones as examples later.
        # We leave verified=False until a human has actually looked it over - if you
        # feed unchecked output back as a few-shot example, you're just teaching the
        # model to repeat its own mistakes.
        pair = {
            "input_text": lease_text,
            "model_output": result,
            "verified": False,
            "validation_problems": problems,
        }
        with open(os.path.join("examples", f"{stem}_pair.json"), "w") as ex_f:
            json.dump(pair, ex_f, indent=2)

        # If there's an answer key sitting next to the lease, score against it.
        truth_path = os.path.join("data", f"{stem}_truth.json")
        if os.path.exists(truth_path):
            with open(truth_path) as gt_f:
                scores.append(run_accuracy_check(result, json.load(gt_f)))
        else:
            print(f"  (no answer key at {truth_path} - skipping accuracy check)\n")

    if scores:
        print(f"Overall accuracy across {len(scores)} scored leases: {sum(scores) / len(scores):.1f}%")
