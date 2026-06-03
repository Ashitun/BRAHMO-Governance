from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Set

from .data_store import GovernanceStore

NOTIFIABLE_ROLES = {"HOD", "EDITOR"}
SEVERITY_RANK = {"URGENT": 0, "WARNING": 1, "INFO": 2}


def create_cascade_alerts(
    store: GovernanceStore,
    *,
    cascade_result: Dict[str, Any],
    actor_id: str,
    projected_health: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    affected = cascade_result.get("affected_nodes", [])
    if not affected:
        return []

    source_node = store.knowledge_nodes[cascade_result["source_node_id"]]
    affected_by_department: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in affected:
        affected_by_department[row["department"]].append(row)

    created: List[Dict[str, Any]] = []
    for department, rows in affected_by_department.items():
        users = [
            user
            for user in store.users.values()
            if user["org_id"] == source_node["org_id"]
            and user["department"] == department
            and user["role"] in NOTIFIABLE_ROLES
        ]
        first_node_id = rows[0]["node_id"]
        for user in users:
            created.append(
                store.add_alert(
                    user_id=user["id"],
                    alert_type="CASCADE",
                    severity="URGENT",
                    title=f"Cascade review needed: {len(rows)} {department} node(s)",
                    body=f"{source_node['title']} was superseded. {len(rows)} derived node(s) moved to REVIEW_REQUIRED. LEGAL_HOLD nodes were skipped and audited.",
                    link=f"/nodes/{first_node_id}",
                    org_id=user["org_id"],
                )
            )

            if projected_health and projected_health.get("overall", 1) < 0.70:
                created.append(
                    store.add_alert(
                        user_id=user["id"],
                        alert_type="HEALTH_DROP",
                        severity="WARNING",
                        title="Knowledge health score needs attention",
                        body=f"Projected score is {int(projected_health['overall'] * 100)}%. Freshness and consistency are lower until reviews complete.",
                        link="/health",
                        org_id=user["org_id"],
                    )
                )
    return created


def create_review_completed_alerts(
    store: GovernanceStore,
    *,
    node_id: str,
    actor_id: str,
    action_label: str,
) -> List[Dict[str, Any]]:
    node = store.knowledge_nodes[node_id]
    actor = store.users[actor_id]
    created: List[Dict[str, Any]] = []
    users = [
        user
        for user in store.users.values()
        if user["org_id"] == node["org_id"]
        and user["department"] == node["department"]
        and user["role"] in NOTIFIABLE_ROLES
        and user["id"] != actor_id
    ]
    for user in users:
        created.append(
            store.add_alert(
                user_id=user["id"],
                alert_type="REVIEW_COMPLETED",
                severity="INFO",
                title=f"Review completed: {node_id}",
                body=f"{actor['name']} marked {node['title']} as {action_label}.",
                link=f"/nodes/{node_id}",
                org_id=user["org_id"],
            )
        )
    return created


def sorted_alerts_for_user(store: GovernanceStore, user_id: str) -> List[Dict[str, Any]]:
    alerts = [alert for alert in store.pulse_alerts.values() if alert["user_id"] == user_id]
    return sorted(alerts, key=lambda row: (SEVERITY_RANK.get(row["severity"], 9), row["created_at"]), reverse=False)
