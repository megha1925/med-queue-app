"""Equity & Access Adjustment Agent.
This agent identifies rural/Indigenous/underserved status and returns adjustment weight.
"""
from typing import Dict

async def compute_equity_adjustment(patient_info: Dict) -> Dict:
    # Placeholder: real logic uses geography_utils + patient demographics
    return {"equity_adjustment": 0.0, "reason": None}
