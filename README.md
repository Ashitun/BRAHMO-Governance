# BRAHMO Governance Engine Web App

A runnable full-stack demo for **Cascade Invalidation + Health Score Recomputation + Pulse Alerts**.

This project implements the assessment flow:

- Supersede Sepsis Protocol v2 with Sepsis Protocol v3.
- Run bounded BFS over `DERIVED_FROM` edges only.
- Move affected child/grandchild nodes to `REVIEW_REQUIRED`.
- Skip `LEGAL_HOLD` and `SUPERSEDED` nodes with audit entries.
- Defer health score recomputation until first review/admin recompute/24-hour scheduler.
- Route Pulse notifications only to affected HOD/EDITOR users in the affected department.
- Provide review actions: confirm, supersede, expire.
- Enforce status transition rules, including terminal `SUPERSEDED` and admin-only `LEGAL_HOLD`.

## Stack

- Backend: FastAPI + deterministic in-memory repository for zero-config local demo
- Frontend: React + TypeScript + Vite + Tailwind CSS
- Database assets: Supabase-compatible `schema.sql` and `seed.sql`

The local backend repository mirrors the Supabase table shapes, so the governance engines can be swapped to a Supabase repository later without changing the API or UI.

## Project structure

```text
brahmo-governance/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── governance/
│   │   ├── cascade_engine.py
│   │   ├── data_store.py
│   │   ├── health_score.py
│   │   ├── pulse_router.py
│   │   ├── review_handler.py
│   │   └── status_machine.py
│   └── models/api.py
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       ├── components/
│       └── lib/
├── docs/architecture.md
└── supabase/
    ├── schema.sql
    └── seed.sql
```

## Run locally

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open API docs at `http://localhost:8000/docs`.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Demo script

1. Keep user as **Dr. Meera**.
2. Click **Supersede Sepsis v2 → v3**.
3. Watch the cascade tree:
   - `N-M08` becomes `SUPERSEDED`.
   - 9 descendants become `REVIEW_REQUIRED`.
   - `N-HELD` stays `LEGAL_HOLD` and gets `CASCADE_SKIP` audit.
4. Open Pulse alerts as **Dr. Meera** and **Dr. Ananya**: both receive Medicine alerts.
5. Switch to **Dr. Vikram**, **Nurse Priya**, or **Admin Suresh**: they do not receive Medicine cascade alerts.
6. Complete one review in the review queue; the health score recomputes immediately.
7. Click **Surprise: Ortho cascade** to prove the cascade is not hardcoded to Medicine.

## Supabase setup

Run these files in Supabase SQL Editor:

```text
supabase/schema.sql
supabase/seed.sql
```

The seed includes 20 knowledge nodes, users, hierarchy levels, and DERIVED_FROM edges for the Sepsis and Ortho cascade demos.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/state` | Full demo state for the dashboard |
| `POST` | `/api/reset` | Reset seed data |
| `POST` | `/api/supersede` | Create replacement node, mark old SUPERSEDED, optionally cascade |
| `POST` | `/api/review` | Confirm, supersede, or expire a REVIEW_REQUIRED node |
| `POST` | `/api/transition` | Manual state-machine-validated status transition |
| `GET` | `/api/health-score` | Compute deterministic health score |
| `POST` | `/api/recompute-health` | Admin/first-review recompute |

## Notes

The assessment seed document states both "20 nodes" and a sample SQL block that enumerates fewer than 20 nodes. This implementation keeps the expected cascade behavior and includes two unrelated active anchor nodes so coverage remains stable after the Sepsis cascade while the total seed count reaches 20.
