"""Explainability & Audit Agent.
Produces clinician- and audit-facing explanations and stores audit entries.
"""
from typing import Dict

async def explain(decision: Dict) -> Dict:
    # Build human-readable rationale (placeholder)
    explanation = {
        "clinician": "Refer to clinical notes; urgency based on parsed features.",
        "admin": "Queue ordering influenced by provincial wait benchmarks and equity adjustments.",
        "audit": decision
    }
    return explanation
