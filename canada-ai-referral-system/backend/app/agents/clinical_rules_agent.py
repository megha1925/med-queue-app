"""Clinical Safety & Guidelines Agent (province-configurable rules)."""
import json
from pathlib import Path
from typing import Dict

RULES_DIR = Path(__file__).parent.parent / "rules"

class ClinicalRules:
    def __init__(self, province: str):
        self.province = province.lower()
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict:
        fname = RULES_DIR / f"{self.province}.json"
        if not fname.exists():
            return {}
        with open(fname, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate(self, parsed_referral: Dict) -> Dict:
        # Apply rule set to parsed referral; return safety flags and suggested urgency
        return {"safety_flags": [], "suggested_urgency": None}
