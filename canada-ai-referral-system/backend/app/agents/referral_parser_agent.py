"""Referral Parsing Agent: extract clinical entities.

This file contains a lightweight placeholder implementation and an optional
integration point with an LLM via `backend.app.services.openai_client`.
If `OPENAI_API_KEY` is not set the function will return a simple structured
placeholder so the rest of the pipeline can run without external dependencies.
"""

from typing import Dict
import os
import json
from ..services import openai_client


async def parse_referral(text: str) -> Dict:
    """Parse the referral text.

    If an OpenAI API key is configured, send the referral to the LLM for structured extraction
    (the LLM should return JSON). Otherwise return a conservative placeholder.
    """
    # If OpenAI configured, ask LLM to extract structured fields
    if os.getenv("OPENAI_API_KEY"):
        prompt = (
            "Extract the following fields from the clinical referral text and return valid JSON:\n"
            "fields: chief_complaint, history, symptoms[], red_flags[], recommended_urgency\n\n"
            f"Referral:\n{text}\n\nRespond only with JSON."
        )
        result = await openai_client.parse_with_llm(prompt)
        if result.get("ok") and result.get("response"):
            # try to parse JSON out of the response
            content = result["response"].strip()
            try:
                # Attempt direct JSON parse
                parsed = json.loads(content)
                return {"text": text, "entities": parsed}
            except Exception:
                # If the model returned text around the JSON, try to extract the first JSON object
                try:
                    start = content.index("{")
                    end = content.rindex("}") + 1
                    parsed = json.loads(content[start:end])
                    return {"text": text, "entities": parsed}
                except Exception:
                    # fallback to returning raw string
                    return {"text": text, "entities": {"model_output": content}}

    # Fallback simple heuristic placeholder
    lower = text.lower()
    flags = []
    if "stroke" in lower or "facial droop" in lower or "sudden weakness" in lower:
        flags.append("possible_stroke")
    if "cancer" in lower or "mass" in lower:
        flags.append("cancer_suspected")

    return {
        "text": text,
        "entities": {
            "chief_complaint": text.split("\n")[0] if text else "",
            "symptoms": [],
            "flags": flags
        }
    }
