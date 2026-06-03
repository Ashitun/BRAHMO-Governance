from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SupersedeRequest(BaseModel):
    node_id: str = Field(default="N-M08")
    actor_id: str = Field(default="U-MEERA")
    new_id: Optional[str] = None
    new_title: Optional[str] = Field(default="Sepsis Protocol v3 (2026)")
    new_content: Optional[str] = Field(
        default="Supra Sepsis Bundle v3 (2026): blood cultures before antibiotics, lactate within 1 HOUR, and 30mL/kg crystalloid for hypotension."
    )
    cascade: bool = True
    max_depth: Optional[int] = None


class ReviewRequest(BaseModel):
    node_id: str
    actor_id: str = Field(default="U-ANANYA")
    decision: str = Field(description="confirm, supersede, or expire")
    new_title: Optional[str] = None
    new_content: Optional[str] = None


class TransitionRequest(BaseModel):
    node_id: str
    actor_id: str
    new_status: str
    reason: str = "Manual governance transition"


class RecomputeRequest(BaseModel):
    org_id: str = "supra"
    department: Optional[str] = None


class AlertReadRequest(BaseModel):
    user_id: Optional[str] = None
