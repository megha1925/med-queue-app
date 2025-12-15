"""Referral Parsing Agent: extract clinical entities (skeleton).
This module should be replaced with an NLP pipeline (clinical NER, sections extraction).
"""

from typing import Dict

async def parse_referral(text: str) -> Dict:
    # Minimal placeholder implementation
    return {
        "text": text,
        "entities": [],
        "symptoms": [],
        "flags": []
    }
