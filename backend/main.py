from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from governance.data_store import STORE
from governance.health_score import compute_health_score, recompute_now
from governance.review_handler import review_node, supersede_node
from governance.status_machine import TransitionError, apply_transition
from models.api import AlertReadRequest, RecomputeRequest, ReviewRequest, SupersedeRequest, TransitionRequest

app = FastAPI(
    title="BRAHMO Governance Demo",
    description="Cascade invalidation + deferred health score recomputation + pulse alerts.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    if STORE.current_health_score is None:
        recompute_now(STORE, org_id="supra", department=None)


@app.get("/")
def root():
    return {
        "service": "BRAHMO Governance Demo API",
        "docs": "/docs",
        "health": "/api/health-score",
        "state": "/api/state",
    }


@app.get("/api/state")
def get_state():
    if STORE.current_health_score is None:
        recompute_now(STORE, org_id="supra", department=None)
    return STORE.snapshot()


@app.post("/api/reset")
def reset_demo():
    STORE.reset()
    recompute_now(STORE, org_id="supra", department=None)
    return STORE.snapshot()


@app.get("/api/health-score")
def get_health_score(org_id: str = "supra", department: str | None = None):
    return compute_health_score(STORE, org_id=org_id, department=department)


@app.post("/api/recompute-health")
def recompute_health(payload: RecomputeRequest):
    return recompute_now(STORE, org_id=payload.org_id, department=payload.department)


@app.post("/api/supersede")
def supersede(payload: SupersedeRequest):
    try:
        result = supersede_node(
            STORE,
            node_id=payload.node_id,
            actor_id=payload.actor_id,
            new_id=payload.new_id,
            new_title=payload.new_title,
            new_content=payload.new_content,
            cascade=payload.cascade,
            max_depth=payload.max_depth,
        )
        return {"result": result, "state": STORE.snapshot()}
    except (KeyError, ValueError, TransitionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/review")
def review(payload: ReviewRequest):
    try:
        result = review_node(
            STORE,
            node_id=payload.node_id,
            actor_id=payload.actor_id,
            decision=payload.decision,
            new_title=payload.new_title,
            new_content=payload.new_content,
        )
        return {"result": result, "state": STORE.snapshot()}
    except (KeyError, ValueError, TransitionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/transition")
def transition(payload: TransitionRequest):
    try:
        result = apply_transition(
            STORE,
            node_id=payload.node_id,
            actor_id=payload.actor_id,
            new_status=payload.new_status,
            reason=payload.reason,
        )
        return {"result": result.__dict__, "state": STORE.snapshot()}
    except (KeyError, ValueError, TransitionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/alerts/{alert_id}/read")
def mark_alert_read(alert_id: str, payload: AlertReadRequest | None = None):
    alert = STORE.pulse_alerts.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Unknown alert_id")
    if payload and payload.user_id and alert["user_id"] != payload.user_id:
        raise HTTPException(status_code=403, detail="Alert does not belong to that user")
    alert["is_read"] = True
    return {"alert": alert, "state": STORE.snapshot()}


@app.get("/api/nodes/{node_id}")
def get_node(node_id: str):
    node = STORE.knowledge_nodes.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Unknown node_id")
    edges = [edge for edge in STORE.edges.values() if edge["source_id"] == node_id or edge["target_id"] == node_id]
    audit = [row for row in STORE.audit_log if row["node_id"] == node_id]
    return {"node": node, "edges": edges, "audit_log": audit}
