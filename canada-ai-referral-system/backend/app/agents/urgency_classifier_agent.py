"""Urgency Classification Agent (ML / rules hybrid placeholder).

If an OpenAI API key is configured this will call the LLM to produce a
recommended urgency label and a rough score. Otherwise falls back to a
deterministic placeholder so the service remains testable offline.
"""

from typing import Dict
import os
from ..services import openai_client


async def classify_urgency(parsed: Dict, province: str) -> Dict:
    # Use LLM when available to generate a suggested urgency label & score
    if os.getenv("OPENAI_API_KEY") and openai_client is not None:
        try:
            prompt = (
                "You are a clinical triage assistant. Given the parsed referral entities and province, "
                "return a JSON object with keys: urgency_label (High|Medium|Low), urgency_score (0.0-1.0), reason (string).\n\n"
                f"Parsed: {parsed}\nProvince: {province}\n\nRespond only with JSON."
            )
            resp = await openai_client.parse_with_llm(prompt, max_tokens=150)
            if resp.get("ok") and resp.get("response"):
                content = resp["response"].strip()
                import json
                try:
                    parsed_out = json.loads(content)
                    # Ensure presence of expected keys with safe defaults
                    return {
                        "urgency_score": float(parsed_out.get("urgency_score", 0.5)),
                        "label": parsed_out.get("urgency_label", parsed_out.get("label", "Routine")),
                        "reason": parsed_out.get("reason", parsed_out.get("explanation", "")),
                        "raw": resp.get("raw")
                    }
                except Exception:
                    # model returned free text; fallback to conservative mapping
                    text = content.lower()
                    if "urgent" in text or "high" in text:
                        return {"urgency_score": 0.9, "label": "High", "reason": content, "raw": resp.get("raw")}
                    if "medium" in text:
                        return {"urgency_score": 0.5, "label": "Medium", "reason": content, "raw": resp.get("raw")}
                    return {"urgency_score": 0.2, "label": "Low", "reason": content, "raw": resp.get("raw")}
        except Exception:
            # Fallthrough to heuristic below
            pass

    # Fallback placeholder deterministic rule: look for red-flag words
    lower = str(parsed).lower()
    score = 0.2
    label = "Low"
    if any(k in lower for k in ["severe", "unstable", "sudden", "acute", "loss of consciousness", "chest pain"]):
        score = 0.9
        label = "High"
    elif any(k in lower for k in ["progressive", "worsening", "moderate"]):
        score = 0.5
        label = "Medium"
    return {"urgency_score": score, "label": label}
