from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api")

class ReferralRequest(BaseModel):
    referral_text: str
    province: str
    patient_id: str = None

@router.post("/process_referral")
async def process_referral(req: ReferralRequest):
    # Placeholder: orchestrate agents here
    return {
        "message": "received",
        "province": req.province,
        "summary": "Processing pipeline not yet implemented"
    }
