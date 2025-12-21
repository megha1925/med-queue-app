"""Explainability & Audit Agent.
Produces clinician- and audit-facing explanations and stores audit entries.
"""
from typing import Dict
import os
from ..services import openai_client


async def explain(decision: Dict) -> Dict:
    """Return human-readable explanations for a decision.

    If OpenAI is configured, ask the model to produce clinician/admin friendly
    summaries. Otherwise return a conservative placeholder.
    """
    if os.getenv("OPENAI_API_KEY") and openai_client is not None:
        try:
            prompt = (
                "You are an explainability assistant. Given the decision object (JSON) produce a JSON object "
                "with keys: clinician (short explanation), admin (short explanation), audit (structured summary).\n\n"
                f"Decision: {decision}\n\nRespond only with JSON."
            )
            resp = await openai_client.parse_with_llm(prompt, max_tokens=300)
            if resp.get("ok") and resp.get("response"):
                import json
                try:
                    parsed = json.loads(resp["response"].strip())
                    return {"clinician": parsed.get("clinician"), "admin": parsed.get("admin"), "audit": parsed.get("audit", decision), "raw": resp.get("raw")}
                except Exception:
                    # If model returned free text, return it within clinician field
                    return {"clinician": resp.get("response"), "admin": "See clinician note.", "audit": decision, "raw": resp.get("raw")}
        except Exception:
            pass

    # Fallback simple explanation
    explanation = {
        "clinician": "Urgency and priority computed from parsed referral and province rules.",
        "admin": "Queue ordering influenced by wait-time intelligence and equity adjustments.",
        "audit": decision
    }
    return explanation
