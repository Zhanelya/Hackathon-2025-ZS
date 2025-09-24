from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class SecurityRule(BaseModel):
    code: str
    description: str
    restriction: str  # e.g., "prohibited" | "restricted"


class BaggageAllowance(BaseModel):
    max_weight_kg: Optional[float]
    max_linear_cm: Optional[int]
    personal_item_allowed: Optional[bool] = True


class VisaRequirement(BaseModel):
    required: bool
    notes: List[str] = []


class DocumentsChecklist(BaseModel):
    items: List[str]
