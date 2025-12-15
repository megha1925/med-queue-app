from pydantic import BaseModel
from typing import Optional

class Referral(BaseModel):
    referral_text: str
    province: str
    patient_id: Optional[str] = None
    patient_postal: Optional[str] = None
    dob: Optional[str] = None
