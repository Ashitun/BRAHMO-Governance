from __future__ import annotations

from typing import Any, Dict, Optional

from .cascade_engine import run_cascade
from .data_store import GovernanceStore, now_iso
from .health_score import mark_recompute_pending, recompute_now
from .pulse_router import create_cascade_alerts, create_review_completed_alerts
from .status_machine import apply_transition


def _next_version_id(store: GovernanceStore, node_id: str) -> str:
    base = f"{node_id}-V"
    versions = [key for key in store.knowledge_nodes if key.startswith(base)]
    return f"{base}{len(versions) + 3}" if node_id == "N-M08" and not versions else f"{base}{len(versions) + 2}"


def supersede_node(
    store: GovernanceStore,
    *,
    node_id: str,
    actor_id: str,
    new_title: Optional[str] = None,
    new_content: Optional[str] = None,
    new_id: Optional[str] = None,
    cascade: bool = True,
    max_depth: Optional[int] = None,
) -> Dict[str, Any]:
    old_node = store.knowledge_nodes.get(node_id)
    if not old_node:
        raise KeyError(f"Unknown node_id: {node_id}")
    if old_node["status"] == "SUPERSEDED":
        raise ValueError("Node is already SUPERSEDED.")
    if old_node["status"] == "LEGAL_HOLD":
        raise ValueError("LEGAL_HOLD node cannot be superseded until an ADMIN releases the hold.")

    actor = store.get_actor(actor_id)
    version_id = new_id or _next_version_id(store, node_id)
    if version_id in store.knowledge_nodes:
        raise ValueError(f"New node id already exists: {version_id}")

    replacement = {
        **old_node,
        "id": version_id,
        "title": new_title or f"{old_node['title']} — replacement",
        "content": new_content or old_node["content"],
        "status": "ACTIVE",
        "superseded_by": None,
        "valid_until": None,
        "created_by": actor_id,
        "created_at": now_iso(),
        "hold_previous_status": None,
    }
    store.knowledge_nodes[version_id] = replacement
    store.add_edge(version_id, node_id, "SUPERSEDES")

    previous_status = old_node["status"]
    old_node["status"] = "SUPERSEDED"
    old_node["superseded_by"] = version_id
    store.add_audit(
        node_id=node_id,
        action="SUPERSEDE",
        old_value=previous_status,
        new_value="SUPERSEDED",
        actor_id=actor_id,
        org_id=old_node["org_id"],
        reason=f"{actor['name']} created replacement {version_id}.",
        metadata={
            "new_node_id": version_id,
            "old_snapshot": {"title": old_node["title"], "content": old_node["content"]},
            "new_snapshot": {"title": replacement["title"], "content": replacement["content"]},
        },
    )

    cascade_result = None
    alerts = []
    projected_health = None
    if cascade:
        cascade_result = run_cascade(store, superseded_node_id=node_id, actor_id=actor_id, max_depth=max_depth)
        projected_health = mark_recompute_pending(
            store,
            reason="Deferred after cascade. Recompute after first review, admin request, or 24-hour scheduler.",
            org_id=old_node["org_id"],
            department=None,
        )
        alerts = create_cascade_alerts(
            store,
            cascade_result=cascade_result,
            actor_id=actor_id,
            projected_health=projected_health,
        )

    return {
        "old_node_id": node_id,
        "new_node_id": version_id,
        "new_node": replacement,
        "cascade": cascade_result,
        "projected_health": projected_health,
        "alerts_created": alerts,
    }


def review_node(
    store: GovernanceStore,
    *,
    node_id: str,
    actor_id: str,
    decision: str,
    new_title: Optional[str] = None,
    new_content: Optional[str] = None,
) -> Dict[str, Any]:
    node = store.knowledge_nodes.get(node_id)
    if not node:
        raise KeyError(f"Unknown node_id: {node_id}")
    if node["status"] != "REVIEW_REQUIRED":
        raise ValueError("Only REVIEW_REQUIRED nodes can be completed through the review flow.")

    if decision == "confirm":
        transition = apply_transition(
            store,
            node_id=node_id,
            new_status="ACTIVE",
            actor_id=actor_id,
            action="REVIEW_CONFIRMED",
            reason="Human review confirmed the node is still valid.",
            metadata={"review_decision": decision},
        )
        score = recompute_now(store, org_id=node["org_id"], department=None)
        alerts = create_review_completed_alerts(store, node_id=node_id, actor_id=actor_id, action_label="ACTIVE")
        return {"decision": decision, "transition": transition.__dict__, "health_score": score, "alerts_created": alerts}

    if decision == "expire":
        transition = apply_transition(
            store,
            node_id=node_id,
            new_status="EXPIRED",
            actor_id=actor_id,
            reason="Human review marked the node no longer relevant.",
            metadata={"review_decision": decision},
        )
        score = recompute_now(store, org_id=node["org_id"], department=None)
        alerts = create_review_completed_alerts(store, node_id=node_id, actor_id=actor_id, action_label="EXPIRED")
        return {"decision": decision, "transition": transition.__dict__, "health_score": score, "alerts_created": alerts}

    if decision == "supersede":
        # Innovation guard: a review of a DECISION does not automatically recurse
        # another cascade. Only CONSTRAINT supersession may cascade again.
        should_cascade = node["type"] == "CONSTRAINT"
        result = supersede_node(
            store,
            node_id=node_id,
            actor_id=actor_id,
            new_title=new_title or f"{node['title']} — reviewed replacement",
            new_content=new_content or node["content"],
            cascade=should_cascade,
        )
        score = recompute_now(store, org_id=node["org_id"], department=None)
        alerts = create_review_completed_alerts(store, node_id=node_id, actor_id=actor_id, action_label="SUPERSEDED")
        result["health_score"] = score
        result["review_alerts_created"] = alerts
        result["recursive_cascade_policy"] = "CONSTRAINT-only" if should_cascade else "No nested cascade for non-CONSTRAINT review supersession"
        return result

    raise ValueError("decision must be one of: confirm, supersede, expire")
