from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.agents.referral_parser_agent import parse_referral
from app.agents.clinical_rules_agent import ClinicalRules
from app.agents.urgency_classifier_agent import classify_urgency
from app.agents.provincial_capacity_agent import get_capacity_intel
from app.agents.equity_adjustment_agent import compute_equity_adjustment
from app.agents.ranking_agent import compute_priority_score
from app.agents.explainability_agent import explain

router = APIRouter(prefix="/api")


class ReferralRequest(BaseModel):
    referral_text: str
    province: str
    patient_id: Optional[str] = None
    patient_postal: Optional[str] = None


@router.post("/process_referral")
async def process_referral(req: ReferralRequest):
    try:
        # 1) Parse referral (LLM or heuristic)
        parsed = await parse_referral(req.referral_text)

        # 2) Apply clinical rules (province-configurable)
        rules = ClinicalRules(req.province)
        rules_eval = rules.evaluate(parsed)

        # 3) Classify urgency (ML/rules hybrid)
        urgency = await classify_urgency(parsed, req.province)

        # 4) Provincial capacity & wait-time intelligence
        capacity = await get_capacity_intel(req.province)

        # 5) Equity adjustment (does not modify clinical urgency)
        equity = await compute_equity_adjustment({"patient_id": req.patient_id, "postal": req.patient_postal})

        # 6) Ranking & scoring
        urgency_score = float(urgency.get("urgency_score", 0.0))
        wait_days = capacity.get("current_wait_days") or 0.0
        capacity_avail = 0.0
        equity_adj = float(equity.get("equity_adjustment", 0.0))

        priority_score = compute_priority_score(urgency_score, float(wait_days), float(capacity_avail), equity_adj)

        # 7) Explainability
        decision = {
            "parsed": parsed,
            "rules_eval": rules_eval,
            "urgency": urgency,
            "capacity": capacity,
            "equity": equity,
            "priority_score": priority_score
        }
        explanation = await explain(decision)

        # Return structured response
        return {
            "ok": True,
            "province": req.province,
            "parsed": parsed,
            "rules_eval": rules_eval,
            "urgency": urgency,
            "capacity": capacity,
            "equity": equity,
            "priority_score": priority_score,
            "explanation": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
