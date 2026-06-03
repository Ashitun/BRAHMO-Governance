from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

IST = timezone(timedelta(hours=5, minutes=30))
DEMO_NOW = datetime(2026, 6, 2, 9, 0, 0, tzinfo=IST)


def now_iso() -> str:
    return DEMO_NOW.isoformat()


class GovernanceStore:
    """Tiny deterministic repository used for the local demo.

    The shape mirrors the Supabase tables in /supabase/schema.sql so the
    governance engines can be moved to Supabase/Postgres without changing
    their public behavior.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.organizations: Dict[str, Dict[str, Any]] = {
            "supra": {
                "id": "supra",
                "name": "Supra Multi-Specialty Hospital",
                "config": {
                    "cascade_max_depth": 3,
                    "health_score_weights": {
                        "coverage": 0.25,
                        "freshness": 0.30,
                        "balance": 0.20,
                        "consistency": 0.25,
                    },
                },
            }
        }

        self.hierarchy_levels: Dict[str, Dict[str, Any]] = {
            "HL-01": {"id": "HL-01", "org_id": "supra", "level_number": 1, "level_name": "Hospital", "department": None},
            "HL-03": {"id": "HL-03", "org_id": "supra", "level_number": 3, "level_name": "Clinical Division", "department": None},
            "HL-05-MED": {"id": "HL-05-MED", "org_id": "supra", "level_number": 5, "level_name": "Gen Medicine Dept", "department": "medicine"},
            "HL-05-ORTHO": {"id": "HL-05-ORTHO", "org_id": "supra", "level_number": 5, "level_name": "Orthopaedics Dept", "department": "ortho"},
            "HL-08-MED": {"id": "HL-08-MED", "org_id": "supra", "level_number": 8, "level_name": "Medicine General", "department": "medicine"},
            "HL-08-ORTHO": {"id": "HL-08-ORTHO", "org_id": "supra", "level_number": 8, "level_name": "Ortho General", "department": "ortho"},
            "HL-10-MED": {"id": "HL-10-MED", "org_id": "supra", "level_number": 10, "level_name": "Medicine Ward", "department": "medicine"},
            "HL-10-ORTHO": {"id": "HL-10-ORTHO", "org_id": "supra", "level_number": 10, "level_name": "Ortho Ward", "department": "ortho"},
        }

        self.users: Dict[str, Dict[str, Any]] = {
            "U-MEERA": {"id": "U-MEERA", "org_id": "supra", "name": "Dr. Meera (HOD Medicine)", "role": "HOD", "department": "medicine"},
            "U-ANANYA": {"id": "U-ANANYA", "org_id": "supra", "name": "Dr. Ananya (Junior)", "role": "EDITOR", "department": "medicine"},
            "U-VIKRAM": {"id": "U-VIKRAM", "org_id": "supra", "name": "Dr. Vikram (HOD Ortho)", "role": "HOD", "department": "ortho"},
            "U-PRIYA": {"id": "U-PRIYA", "org_id": "supra", "name": "Nurse Priya", "role": "VIEWER", "department": "ortho"},
            "U-SURESH": {"id": "U-SURESH", "org_id": "supra", "name": "Admin Suresh", "role": "ADMIN", "department": "admin"},
        }

        def node(
            id: str,
            level: str,
            type_: str,
            title: str,
            content: str,
            importance: float,
            status: str,
            department: str,
            created_by: str,
            created_at: str,
            valid_until: Optional[str] = None,
        ) -> Dict[str, Any]:
            return {
                "id": id,
                "org_id": "supra",
                "hierarchy_level_id": level,
                "type": type_,
                "title": title,
                "content": content,
                "importance": importance,
                "status": status,
                "superseded_by": None,
                "department": department,
                "valid_until": valid_until,
                "created_by": created_by,
                "created_at": created_at,
                "hold_previous_status": None,
            }

        self.knowledge_nodes: Dict[str, Dict[str, Any]] = {
            # Source node for the main demo. valid_until is intentionally stale so
            # the freshness dimension has a visible before/after movement.
            "N-M08": node(
                "N-M08",
                "HL-05-MED",
                "DECISION",
                "Sepsis Protocol v2 (2024)",
                "Supra Sepsis Bundle v2 (2024): blood cultures before antibiotics, lactate within 3 HOURS, 30mL/kg crystalloid for hypotension.",
                0.95,
                "ACTIVE",
                "medicine",
                "U-MEERA",
                "2024-03-01T10:00:00+05:30",
                "2026-01-01T00:00:00+05:30",
            ),
            "N-DRV-01": node("N-DRV-01", "HL-08-MED", "DECISION", "Lactate Monitoring Schedule", "Lactate levels monitored per Sepsis v2 protocol: every 3 hours for suspected sepsis patients. ICU escalation if lactate > 4 mmol/L.", 0.78, "ACTIVE", "medicine", "U-ANANYA", "2024-05-10T11:00:00+05:30"),
            "N-DRV-02": node("N-DRV-02", "HL-08-MED", "DECISION", "Night Shift Sepsis Screening", "Night shift nurses screen for sepsis using qSOFA (based on Sepsis v2 parameters): altered mentation, RR >= 22, SBP <= 100.", 0.75, "ACTIVE", "medicine", "U-MEERA", "2024-06-20T08:00:00+05:30"),
            "N-DRV-03": node("N-DRV-03", "HL-08-MED", "DECISION", "Empiric Antibiotic Selection", "Based on Sepsis v2 bundle: Piperacillin-Tazobactam 4.5g IV within 3-hour window. Culture-guided de-escalation at 72 hours.", 0.82, "ACTIVE", "medicine", "U-MEERA", "2024-07-05T15:00:00+05:30"),
            "N-DRV-04": node("N-DRV-04", "HL-05-MED", "DECISION", "ICU Admission from Sepsis Screening", "Patients meeting 2/3 qSOFA criteria with lactate > 2 mmol/L: assess for ICU admission within 1 hour.", 0.80, "ACTIVE", "medicine", "U-ANANYA", "2024-08-12T10:00:00+05:30"),
            "N-DRV-05": node("N-DRV-05", "HL-05-MED", "FACT", "Sepsis Mortality Tracking", "Supra sepsis mortality Q3 2024: 18% (national average 22%). Improvement attributed to v2 bundle compliance reaching 78%.", 0.60, "ACTIVE", "medicine", "U-MEERA", "2024-10-01T09:00:00+05:30"),
            "N-DRV-06": node("N-DRV-06", "HL-10-MED", "DECISION", "Pharmacy Pre-Auth for IV Antibiotics", "Per Sepsis v2 timing: pharmacy pre-authorizes Pip-Tazo for suspected sepsis. No approval delay within 3-hour window.", 0.72, "ACTIVE", "medicine", "U-ANANYA", "2024-11-15T14:00:00+05:30"),
            "N-DRV-04-A": node("N-DRV-04-A", "HL-08-MED", "DECISION", "ICU Bed Reservation Protocol", "Based on ICU admission criteria (N-DRV-04): reserve 2 ICU beds per shift for suspected sepsis admissions.", 0.65, "ACTIVE", "medicine", "U-ANANYA", "2025-01-20T10:00:00+05:30"),
            "N-DRV-04-B": node("N-DRV-04-B", "HL-10-MED", "FACT", "ICU Occupancy from Sepsis Admissions", "ICU sepsis admissions average 3 per week (2024). Peak: 7 in monsoon season (water-borne infections).", 0.55, "ACTIVE", "medicine", "U-MEERA", "2025-02-15T09:00:00+05:30"),
            "N-DRV-02-A": node("N-DRV-02-A", "HL-10-MED", "DECISION", "Night Shift Escalation Timing", "Night shift sepsis screening positive: call duty doctor within 15 minutes. If no response: escalate to HOD within 30 minutes.", 0.70, "ACTIVE", "medicine", "U-ANANYA", "2025-03-01T08:00:00+05:30"),
            "N-HELD": node("N-HELD", "HL-08-MED", "DECISION", "Sepsis Bundle Compliance Audit Data", "Compliance data under medico-legal review: v2 bundle adherence was 78% in Q3 2024. Two adverse outcomes under investigation.", 0.75, "LEGAL_HOLD", "medicine", "U-MEERA", "2024-09-01T10:00:00+05:30"),
            "N-M01": node("N-M01", "HL-05-MED", "CONSTRAINT", "Diabetic Fasting Protocol", "Fasting diabetic patients: adjust insulin timing not dose. Skip Glimepiride on fast days.", 0.90, "ACTIVE", "medicine", "U-MEERA", "2025-06-01T09:00:00+05:30"),
            "N-M03": node("N-M03", "HL-05-MED", "ANTI_PATTERN", "Insulin Sliding Scale Alone", "Do NOT use sliding scale as sole glycemic management. Always include basal insulin.", 0.87, "ACTIVE", "medicine", "U-ANANYA", "2025-07-15T14:00:00+05:30"),
            # Two unrelated active anchors keep coverage stable after the Sepsis
            # cascade moves most depth-8/depth-10 medicine nodes to review.
            "N-M02": node("N-M02", "HL-08-MED", "CONSTRAINT", "Renal Dose Adjustment Review", "Medicine prescriptions for eGFR < 30 require renal dose review before first maintenance dose.", 0.84, "ACTIVE", "medicine", "U-MEERA", "2025-08-01T09:00:00+05:30"),
            "N-M04": node("N-M04", "HL-10-MED", "ANTI_PATTERN", "Delayed Critical Lab Escalation", "Do not wait for routine rounds when critical lactate, potassium, or ABG values are flagged by the lab.", 0.79, "ACTIVE", "medicine", "U-ANANYA", "2025-08-15T10:30:00+05:30"),
            "N-O01": node("N-O01", "HL-05-ORTHO", "CONSTRAINT", "DVT Prophylaxis Protocol", "ALL ortho surgical patients: Enoxaparin 40mg SC daily. TKR 14d, THR 28d.", 0.93, "ACTIVE", "ortho", "U-VIKRAM", "2025-04-01T10:00:00+05:30"),
            "N-O02": node("N-O02", "HL-08-ORTHO", "DECISION", "Paracetamol First-Line Post-TKR", "Paracetamol 650mg QDS first-line. Tramadol if VAS > 6. No NSAIDs.", 0.88, "ACTIVE", "ortho", "U-VIKRAM", "2025-01-20T11:00:00+05:30"),
            "N-O03": node("N-O03", "HL-08-ORTHO", "DECISION", "PT Within 24 Hours Post-TKR", "Physiotherapy must begin within 24 hours of TKR. Day 1: ankle pumps.", 0.90, "ACTIVE", "ortho", "U-VIKRAM", "2025-03-10T08:00:00+05:30"),
            "N-O04": node("N-O04", "HL-10-ORTHO", "FACT", "Ortho Ward Capacity", "Ortho Ward: 45 beds. 85-90% occupancy. Overflow to Medicine in winter.", 0.50, "ACTIVE", "ortho", "U-VIKRAM", "2025-05-01T09:00:00+05:30"),
            "N-EXP": node("N-EXP", "HL-05-MED", "FACT", "Antibiotic Sensitivity Report Q2 2024", "E. coli sensitivity to Pip-Tazo: 89%. K. pneumoniae: 72%. Based on 2024 Q2 data.", 0.55, "EXPIRED", "medicine", "U-MEERA", "2024-07-01T09:00:00+05:30", "2025-01-01T00:00:00+05:30"),
        }

        self.edges: Dict[str, Dict[str, Any]] = {}

        def edge(source: str, target: str, edge_type: str) -> None:
            edge_id = str(uuid4())
            self.edges[edge_id] = {
                "id": edge_id,
                "source_id": source,
                "target_id": target,
                "edge_type": edge_type,
                "created_at": now_iso(),
            }

        for source in ["N-DRV-01", "N-DRV-02", "N-DRV-03", "N-DRV-04", "N-DRV-05", "N-DRV-06", "N-HELD"]:
            edge(source, "N-M08", "DERIVED_FROM")
        edge("N-DRV-04-A", "N-DRV-04", "DERIVED_FROM")
        edge("N-DRV-04-B", "N-DRV-04", "DERIVED_FROM")
        edge("N-DRV-02-A", "N-DRV-02", "DERIVED_FROM")
        edge("N-M01", "N-DRV-01", "SUPPORTS")
        edge("N-O01", "N-O02", "SUPPORTS")
        edge("N-O02", "N-O01", "DERIVED_FROM")
        edge("N-O03", "N-O01", "DERIVED_FROM")

        self.audit_log: List[Dict[str, Any]] = []
        self.pulse_alerts: Dict[str, Dict[str, Any]] = {}
        self.last_cascade: Optional[Dict[str, Any]] = None
        self.health_pending: bool = False
        self.health_pending_reason: Optional[str] = None
        self.current_health_score: Optional[Dict[str, Any]] = None
        self.projected_health_score: Optional[Dict[str, Any]] = None

    def snapshot(self) -> Dict[str, Any]:
        return {
            "organizations": deepcopy(list(self.organizations.values())),
            "hierarchy_levels": deepcopy(list(self.hierarchy_levels.values())),
            "knowledge_nodes": deepcopy(list(self.knowledge_nodes.values())),
            "edges": deepcopy(list(self.edges.values())),
            "users": deepcopy(list(self.users.values())),
            "audit_log": deepcopy(sorted(self.audit_log, key=lambda row: row["timestamp"], reverse=True)),
            "pulse_alerts": deepcopy(sorted(self.pulse_alerts.values(), key=lambda row: row["created_at"], reverse=True)),
            "last_cascade": deepcopy(self.last_cascade),
            "health_pending": self.health_pending,
            "health_pending_reason": self.health_pending_reason,
            "current_health_score": deepcopy(self.current_health_score),
            "projected_health_score": deepcopy(self.projected_health_score),
            "demo_now": now_iso(),
        }

    def get_actor(self, actor_id: str) -> Dict[str, Any]:
        actor = self.users.get(actor_id)
        if not actor:
            raise KeyError(f"Unknown actor_id: {actor_id}")
        return actor

    def add_audit(
        self,
        *,
        node_id: Optional[str],
        action: str,
        actor_id: str,
        org_id: str = "supra",
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        entry = {
            "id": str(uuid4()),
            "node_id": node_id,
            "action": action,
            "old_value": old_value,
            "new_value": new_value,
            "actor_id": actor_id,
            "org_id": org_id,
            "reason": reason,
            "metadata": metadata or {},
            "timestamp": now_iso(),
        }
        self.audit_log.append(entry)
        return entry

    def add_alert(
        self,
        *,
        user_id: str,
        alert_type: str,
        severity: str,
        title: str,
        body: str,
        link: Optional[str],
        org_id: str = "supra",
    ) -> Dict[str, Any]:
        alert_id = str(uuid4())
        alert = {
            "id": alert_id,
            "org_id": org_id,
            "user_id": user_id,
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "body": body,
            "link": link,
            "is_read": False,
            "created_at": now_iso(),
        }
        self.pulse_alerts[alert_id] = alert
        return alert

    def add_edge(self, source_id: str, target_id: str, edge_type: str) -> Dict[str, Any]:
        edge_id = str(uuid4())
        edge = {
            "id": edge_id,
            "source_id": source_id,
            "target_id": target_id,
            "edge_type": edge_type,
            "created_at": now_iso(),
        }
        self.edges[edge_id] = edge
        return edge

    def derived_children(self, target_id: str) -> List[Dict[str, Any]]:
        children = [edge for edge in self.edges.values() if edge["target_id"] == target_id and edge["edge_type"] == "DERIVED_FROM"]
        return sorted(children, key=lambda row: row["source_id"])


STORE = GovernanceStore()
