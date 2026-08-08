import os
import logging

import anthropic
import google.generativeai as genai

logger = logging.getLogger(__name__)


class ServiceUnavailable(Exception):
    """Raised when every configured provider failed to answer. Callers
    should catch this and show the friendly message below — never the raw
    provider error."""


def _call_anthropic(system_prompt: str, user_prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name, system_instruction=system_prompt)
    response = model.generate_content(user_prompt)
    return response.text


# Order = priority. Each entry: (name, env var that must be set, call fn).
PROVIDERS = [
    ("anthropic", "ANTHROPIC_API_KEY", _call_anthropic),
    ("gemini", "GEMINI_API_KEY", _call_gemini),
]


def call_with_fallback(system_prompt: str, user_prompt: str) -> tuple[str, str]:
    """Try each provider in order and return (provider_name, raw_text) from
    whichever one succeeds first. Raises ServiceUnavailable if all fail."""
    last_errors = []

    for name, env_var, call_fn in PROVIDERS:
        if not os.environ.get(env_var):
            logger.info("Skipping %s: %s not set", name, env_var)
            continue

        try:
            text = call_fn(system_prompt, user_prompt)
            if name != PROVIDERS[0][0]:
                logger.warning("Primary provider(s) failed — served by fallback: %s", name)
            return name, text
        except Exception as e:
            logger.warning("%s failed: %s", name, e)
            last_errors.append(f"{name}: {e}")

    logger.error("All providers failed: %s", "; ".join(last_errors))
    raise ServiceUnavailable(
        "This service is unavailable at this time. Please try again later."
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        provider, text = call_with_fallback(
            system_prompt="You are a helpful assistant.",
            user_prompt="Reply with the single word: ok",
        )
        print(f"[{provider}] {text}")
    except ServiceUnavailable as e:
        print(e)
