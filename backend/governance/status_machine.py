from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .data_store import GovernanceStore

TERMINAL = "SUPERSEDED"

VALID_TRANSITIONS: Dict[str, set[str]] = {
    "ACTIVE": {"SUPERSEDED", "REVIEW_REQUIRED", "EXPIRED", "LEGAL_HOLD"},
    "REVIEW_REQUIRED": {"ACTIVE", "SUPERSEDED", "EXPIRED", "LEGAL_HOLD"},
    "EXPIRED": {"ACTIVE", "LEGAL_HOLD"},
    "LEGAL_HOLD": set(),  # release handled separately because it restores previous status
    "SUPERSEDED": set(),
}


@dataclass
class TransitionResult:
    node_id: str
    old_status: str
    new_status: str
    accepted: bool
    reason: str


class TransitionError(ValueError):
    pass


def validate_transition(
    *,
    current_status: str,
    new_status: str,
    actor_role: str,
    previous_status: Optional[str] = None,
) -> None:
    if current_status == new_status:
        raise TransitionError(f"Node is already {new_status}.")

    if current_status == TERMINAL:
        raise TransitionError("SUPERSEDED is terminal and cannot transition to another status.")

    if new_status == "LEGAL_HOLD" and actor_role != "ADMIN":
        raise TransitionError("Only ADMIN users can place a node on LEGAL_HOLD.")

    if current_status == "LEGAL_HOLD":
        if actor_role != "ADMIN":
            raise TransitionError("Only ADMIN users can release a LEGAL_HOLD node.")
        if previous_status and new_status != previous_status:
            raise TransitionError(f"LEGAL_HOLD release must restore previous status: {previous_status}.")
        if not previous_status and new_status not in {"ACTIVE", "REVIEW_REQUIRED", "EXPIRED"}:
            raise TransitionError("LEGAL_HOLD release must restore a non-terminal previous status.")
        return

    if new_status not in VALID_TRANSITIONS.get(current_status, set()):
        raise TransitionError(f"Invalid transition: {current_status} -> {new_status}.")


def apply_transition(
    store: GovernanceStore,
    *,
    node_id: str,
    new_status: str,
    actor_id: str,
    reason: str,
    action: str = "STATUS_CHANGE",
    metadata: Optional[dict] = None,
) -> TransitionResult:
    node = store.knowledge_nodes.get(node_id)
    if not node:
        raise KeyError(f"Unknown node_id: {node_id}")
    actor = store.get_actor(actor_id)
    old_status = node["status"]
    validate_transition(
        current_status=old_status,
        new_status=new_status,
        actor_role=actor["role"],
        previous_status=node.get("hold_previous_status"),
    )

    if new_status == "LEGAL_HOLD":
        node["hold_previous_status"] = old_status
    if old_status == "LEGAL_HOLD":
        node["hold_previous_status"] = None

    node["status"] = new_status
    store.add_audit(
        node_id=node_id,
        action=action,
        old_value=old_status,
        new_value=new_status,
        actor_id=actor_id,
        org_id=node["org_id"],
        reason=reason,
        metadata=metadata,
    )
    return TransitionResult(
        node_id=node_id,
        old_status=old_status,
        new_status=new_status,
        accepted=True,
        reason=reason,
    )
