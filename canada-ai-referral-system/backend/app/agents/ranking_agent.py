"""Ranking & Scoring Agent.
Priority Score = (0.45 × Clinical Urgency)
               + (0.25 × Wait Duration)
               - (0.15 × Capacity Availability)
               + (0.15 × Equity Adjustment)
Weights are configurable per province.
"""

from typing import Dict

def compute_priority_score(urgency: float, wait_days: float, capacity_avail: float, equity_adj: float, weights: Dict=None) -> float:
    if weights is None:
        weights = {"urgency":0.45, "wait":0.25, "capacity":0.15, "equity":0.15}
    score = (weights["urgency"] * urgency)
    score += (weights["wait"] * wait_days)
    score -= (weights["capacity"] * capacity_avail)
    score += (weights["equity"] * equity_adj)
    return score
