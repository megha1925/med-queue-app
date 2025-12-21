from fastapi import APIRouter, HTTPException
from fastapi import Query
import json
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


@router.get("/dashboard/trends")
async def dashboard_trends():
    # Derive simple trend counts from the sample patients dataset
    try:
        from app.data.sample_patients import patients
    except Exception:
        patients = []
    counts = {}
    for p in patients:
        d = p.get('disease') or 'Unknown'
        counts[d] = counts.get(d, 0) + 1
    trends = [{'disease': k, 'count': v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]
    return {"ok": True, "trends": trends}


@router.get("/dashboard/patients")
async def dashboard_patients(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=50)):
    # Return the sample patients (paginated) for the frontend
    # Accept query params: page (1-based) and per_page (default 10)
    try:
        from app.data.sample_patients import patients
    except Exception:
        patients = []
    total = len(patients)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = patients[start:end]
    total_pages = (total + per_page - 1) // per_page if per_page else 1
    return {"ok": True, "patients": page_items, "meta": {"total": total, "page": page, "per_page": per_page, "total_pages": total_pages}}


@router.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    # Return detailed patient info for modal — use detail_map from sample data
    try:
        from app.data.sample_patients import detail_map
    except Exception:
        detail_map = {}
    patient = detail_map.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"ok": True, "patient": patient}


@router.get("/dashboard/report")
async def dashboard_report(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=50)):
    """Generate a short report for the patients on the requested page using OpenAI when available.

    Returns a simple text report and (optionally) raw model output.
    """
    try:
        from app.data.sample_patients import patients
    except Exception:
        patients = []

    total = len(patients)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = patients[start:end]

    # If OpenAI available, ask model to summarise the provided patients list
    try:
        from ..services import openai_client
    except Exception:
        openai_client = None

    report_text = None
    raw = None
    if openai_client is not None and openai_client.openai is not None and (openai_client.OPENAI_API_KEY):
        try:
            prompt = (
                "You are a clinical analytics assistant. Given a small list of patient records (JSON), produce a concise report "
                "highlighting: 1) the most common diseases in this page, 2) counts by priority, and 3) any notable observations. "
                "Return plain text only.\n\n"
                f"Patients: {json.dumps(page_items)}\n\nReport:" 
            )
            resp = await openai_client.parse_with_llm(prompt, max_tokens=250)
            if resp.get("ok") and resp.get("response"):
                report_text = resp.get("response")
                raw = resp.get("raw")
        except Exception:
            report_text = None

    # Fallback simple programmatic report
    if not report_text:
        counts_by_disease = {}
        counts_by_priority = {}
        for p in page_items:
            counts_by_disease[p.get('disease', 'Unknown')] = counts_by_disease.get(p.get('disease', 'Unknown'), 0) + 1
            counts_by_priority[p.get('priority', 'Low')] = counts_by_priority.get(p.get('priority', 'Low'), 0) + 1
        top_diseases = sorted(counts_by_disease.items(), key=lambda x: -x[1])[:3]
        report_lines = [f"Patients on page {page} (showing {len(page_items)} of {total}):"]
        report_lines.append("Top diseases:")
        for d, c in top_diseases:
            report_lines.append(f" - {d}: {c}")
        report_lines.append("Priority counts:")
        for k, v in counts_by_priority.items():
            report_lines.append(f" - {k}: {v}")
        report_text = "\n".join(report_lines)

    return {"ok": True, "report": report_text, "raw": raw}
