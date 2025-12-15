"""Simple OpenAI client wrapper for backend agents.

Usage:
  - Set environment variable `OPENAI_API_KEY` before starting the backend.
  - Call `parse_with_llm(prompt)` to run a chat-style request.

This wrapper is intentionally small and defensive so the repo can run without an API key.
"""
import os
import logging
from typing import Optional, Dict, Any

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger("openai_client")

if OPENAI_API_KEY:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
    except Exception as e:
        logger.warning("OpenAI package is not available: %s", e)
        openai = None
else:
    openai = None


async def parse_with_llm(prompt: str, model: Optional[str] = None, max_tokens: int = 512) -> Dict[str, Any]:
    """Send prompt to OpenAI and return the model response.

    If no API key/package is available returns an empty result.
    """
    if openai is None:
        logger.debug("OpenAI client not configured; skipping LLM call.")
        return {"ok": False, "error": "openai_not_configured"}

    try:
        # Build chat message payload (simple system + user)
        messages = [
            {"role": "system", "content": "You are a clinical assistant extracting structured information from referral text. Respond with JSON."},
            {"role": "user", "content": prompt}
        ]

        kwargs = {"messages": messages, "max_tokens": max_tokens}
        if model:
            kwargs["model"] = model

        # Use ChatCompletion API where available
        resp = openai.ChatCompletion.create(**kwargs)
        # Extract textual content
        choice = resp.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content") or choice.get("text")
        return {"ok": True, "response": content, "raw": resp}
    except Exception as e:
        logger.exception("OpenAI call failed: %s", e)
        return {"ok": False, "error": str(e)}
