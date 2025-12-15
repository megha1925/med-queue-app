"""Urgency Classification Agent (ML / rules hybrid placeholder)."""

from typing import Dict

async def classify_urgency(parsed: Dict, province: str) -> Dict:
    # Placeholder: real model would take parsed entities + province as feature
    return {"urgency_score": 0.5, "label": "Routine"}
