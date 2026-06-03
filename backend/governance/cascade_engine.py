from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from .data_store import GovernanceStore


def run_cascade(
    store: GovernanceStore,
    *,
    superseded_node_id: str,
    actor_id: str,
    max_depth: Optional[int] = None,
) -> Dict[str, Any]:
    """Bounded BFS over DERIVED_FROM edges.

    Each reached ACTIVE node becomes REVIEW_REQUIRED. LEGAL_HOLD and
    SUPERSEDED nodes are skipped with explicit audit entries. The queue keeps
    a visited set so multi-parent nodes cannot be reprocessed or loop forever.
    """
    source_node = store.knowledge_nodes.get(superseded_node_id)
    if not source_node:
        raise KeyError(f"Unknown superseded_node_id: {superseded_node_id}")

    configured_depth = store.organizations[source_node["org_id"]]["config"].get("cascade_max_depth", 3)
    depth_limit = max_depth if max_depth is not None else configured_depth
    cascade_id = str(uuid4())

    affected: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    visited: Set[str] = set()
    queue: deque[Tuple[str, int]] = deque([(superseded_node_id, 0)])

    store.add_audit(
        node_id=superseded_node_id,
        action="CASCADE_TRIGGER",
        old_value=None,
        new_value="STARTED",
        actor_id=actor_id,
        org_id=source_node["org_id"],
        reason=f"Cascade started from {superseded_node_id}",
        metadata={"cascade_id": cascade_id, "max_depth": depth_limit},
    )

    while queue:
        current_id, depth = queue.popleft()
        if current_id in visited:
            continue
        visited.add(current_id)

        if depth >= depth_limit:
            continue

        for edge in store.derived_children(current_id):
            child_id = edge["source_id"]
            child_depth = depth + 1
            child = store.knowledge_nodes.get(child_id)
            if not child:
                skipped.append({"node_id": child_id, "depth": child_depth, "reason": "MISSING_NODE"})
                continue

            if child_id in visited:
                skipped.append({"node_id": child_id, "depth": child_depth, "reason": "ALREADY_VISITED"})
                continue

            if child_depth > depth_limit:
                skipped.append({"node_id": child_id, "depth": child_depth, "reason": "MAX_DEPTH_EXCEEDED"})
                store.add_audit(
                    node_id=child_id,
                    action="CASCADE_SKIP",
                    actor_id=actor_id,
                    org_id=child["org_id"],
                    reason=f"Cascade skipped because depth {child_depth} exceeds max_depth {depth_limit}.",
                    metadata={"cascade_id": cascade_id, "depth": child_depth},
                )
                continue

            old_status = child["status"]
            if old_status == "LEGAL_HOLD":
                skipped.append({"node_id": child_id, "title": child["title"], "depth": child_depth, "reason": "LEGAL_HOLD"})
                store.add_audit(
                    node_id=child_id,
                    action="CASCADE_SKIP",
                    old_value=old_status,
                    new_value=old_status,
                    actor_id=actor_id,
                    org_id=child["org_id"],
                    reason="LEGAL_HOLD prevents status change during cascade.",
                    metadata={"cascade_id": cascade_id, "depth": child_depth},
                )
                continue

            if old_status == "SUPERSEDED":
                skipped.append({"node_id": child_id, "title": child["title"], "depth": child_depth, "reason": "ALREADY_SUPERSEDED"})
                store.add_audit(
                    node_id=child_id,
                    action="CASCADE_SKIP",
                    old_value=old_status,
                    new_value=old_status,
                    actor_id=actor_id,
                    org_id=child["org_id"],
                    reason="SUPERSEDED node already replaced; no cascade status change needed.",
                    metadata={"cascade_id": cascade_id, "depth": child_depth},
                )
                continue

            if old_status == "EXPIRED":
                skipped.append({"node_id": child_id, "title": child["title"], "depth": child_depth, "reason": "EXPIRED"})
                store.add_audit(
                    node_id=child_id,
                    action="CASCADE_SKIP",
                    old_value=old_status,
                    new_value=old_status,
                    actor_id=actor_id,
                    org_id=child["org_id"],
                    reason="EXPIRED node is not revived during cascade.",
                    metadata={"cascade_id": cascade_id, "depth": child_depth},
                )
                continue

            if old_status == "REVIEW_REQUIRED":
                skipped.append({"node_id": child_id, "title": child["title"], "depth": child_depth, "reason": "ALREADY_REVIEW_REQUIRED"})
                queue.append((child_id, child_depth))
                continue

            child["status"] = "REVIEW_REQUIRED"
            row = {
                "node_id": child_id,
                "title": child["title"],
                "department": child["department"],
                "depth": child_depth,
                "old_status": old_status,
                "new_status": "REVIEW_REQUIRED",
            }
            affected.append(row)
            store.add_audit(
                node_id=child_id,
                action="STATUS_CHANGE",
                old_value=old_status,
                new_value="REVIEW_REQUIRED",
                actor_id=actor_id,
                org_id=child["org_id"],
                reason=f"Cascade from {superseded_node_id} at depth {child_depth}.",
                metadata={"cascade_id": cascade_id, "depth": child_depth, "source_node_id": superseded_node_id},
            )
            queue.append((child_id, child_depth))

    result = {
        "cascade_id": cascade_id,
        "source_node_id": superseded_node_id,
        "source_title": source_node["title"],
        "affected_nodes": affected,
        "skipped_nodes": skipped,
        "affected_count": len(affected),
        "skipped_count": len(skipped),
        "max_depth_reached": max([row["depth"] for row in affected], default=0),
        "max_depth_configured": depth_limit,
        "visited_count": len(visited),
    }
    store.last_cascade = result
    return result
