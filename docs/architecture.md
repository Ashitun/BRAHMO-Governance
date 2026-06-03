# Architecture Notes

## 1. Data flow

```text
Supersede node
  -> create replacement node
  -> mark old node SUPERSEDED
  -> append SUPERSEDE audit entry
  -> bounded cascade over DERIVED_FROM edges
  -> append STATUS_CHANGE or CASCADE_SKIP audit entries
  -> mark health recomputation pending
  -> route aggregated Pulse alerts to affected HOD/EDITOR users
  -> human review triggers health recomputation
```

The implementation is deterministic. Health scores are computed from counts and distributions; no LLM is used.

## 2. Cascade invalidation

The cascade engine is a bounded breadth-first search.

Core rules:

- It follows `DERIVED_FROM` edges only.
- It does not follow `SUPPORTS`, `REQUIRES`, `CONTRADICTS`, or `SUPERSEDES` edges.
- It uses `max_depth` from organization config, defaulting to 3.
- It uses a `visited` set so multi-parent nodes are processed once.
- It moves `ACTIVE` nodes to `REVIEW_REQUIRED`.
- It skips `LEGAL_HOLD` nodes and appends `CASCADE_SKIP` audit entries.
- It skips `SUPERSEDED` nodes because they are terminal and already replaced.
- It skips `EXPIRED` nodes because a cascade should not revive stale knowledge.
- It records an audit entry for every status change and every compliance skip.

Performance is proportional to the bounded subgraph: `O(V + E)` for reachable nodes and edges up to `max_depth`. A cascade touching 85 nodes is 85 status updates plus 85 audit inserts, ideally batched in a single database transaction.

## 3. Status transition state machine

Accepted transitions:

```text
ACTIVE -> SUPERSEDED
ACTIVE -> REVIEW_REQUIRED
ACTIVE -> EXPIRED
ACTIVE -> LEGAL_HOLD       ADMIN only

REVIEW_REQUIRED -> ACTIVE
REVIEW_REQUIRED -> SUPERSEDED
REVIEW_REQUIRED -> EXPIRED
REVIEW_REQUIRED -> LEGAL_HOLD  ADMIN only

EXPIRED -> ACTIVE
EXPIRED -> LEGAL_HOLD      ADMIN only

LEGAL_HOLD -> previous status  ADMIN only
SUPERSEDED -> nothing          terminal
```

Invalid transitions return HTTP 400 with a clear reason. The frontend exposes a few manual transitions so the evaluator can see enforcement in action.

## 4. Health score

The score has four deterministic dimensions:

- **Coverage**: active hierarchy levels divided by configured levels.
- **Freshness**: active nodes not expired or past valid_until divided by live nodes (`ACTIVE + REVIEW_REQUIRED`).
- **Balance**: type distribution health across live node types.
- **Consistency**: active nodes divided by active plus review-required nodes.

Overall score uses organization weights:

```text
coverage 0.25 + freshness 0.30 + balance 0.20 + consistency 0.25
```

After a cascade, recomputation is intentionally deferred. The dashboard shows a pending indicator and a projected score, but the stored score updates only after:

1. an admin recompute,
2. the first review is confirmed, or
3. a scheduled 24-hour recompute job.

This avoids alarming leadership with a transient dip during the expected review window while still making the projected impact visible.

## 5. Pulse notification routing

Pulse routes from affected nodes to departments, then from departments to users.

```sql
SELECT DISTINCT u.id, u.name, u.role, u.department
FROM users u
JOIN knowledge_nodes n ON n.department = u.department
WHERE n.id IN (:affected_node_ids)
  AND u.role IN ('HOD', 'EDITOR')
  AND u.org_id = :org_id;
```

The demo aggregates alerts per user and department. A cascade affecting 85 nodes should not produce 85 notifications per doctor; it should produce one actionable alert such as "15 of your Medicine nodes need review."

## 6. Recursive cascade policy

A review can supersede an affected node. To prevent uncontrolled cascades, this implementation cascades recursively only when the reviewed node is a `CONSTRAINT`. A `DECISION` replacement is audited and health is recomputed, but it does not automatically trigger a second cascade.

## 7. Surprise-test readiness

No logic is hardcoded to Sepsis or Medicine. The Ortho button supersedes `N-O01` and uses the same cascade engine, state machine, health scoring, and pulse routing path.
