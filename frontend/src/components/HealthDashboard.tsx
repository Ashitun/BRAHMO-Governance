import { Activity, Clock3 } from 'lucide-react';
import type { HealthScore } from '../lib/types';

function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function Bar({ label, value }: { label: string; value: number }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm font-medium text-slate-700">
        <span>{label}</span>
        <span>{percent(value)}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-slate-900" style={{ width: percent(value) }} />
      </div>
    </div>
  );
}

export default function HealthDashboard({ current, projected, pending }: { current: HealthScore | null; projected: HealthScore | null; pending: boolean }) {
  const score = pending && projected ? projected : current;
  if (!score) return null;
  const currentOverall = current ? percent(current.overall) : '—';
  const shownOverall = percent(score.overall);

  return (
    <section className="card p-5">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
            <Activity size={16} /> Knowledge Health Score
          </div>
          <h2 className="mt-2 text-4xl font-black tracking-tight text-slate-950">{shownOverall}</h2>
          <p className="mt-1 text-sm text-slate-500">
            Department: <span className="font-semibold text-slate-700">{score.department}</span>
          </p>
        </div>
        {pending ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
            <div className="flex items-center gap-2 font-bold"><Clock3 size={16} /> Deferred recompute pending</div>
            <p className="mt-1">Current stored score is {currentOverall}. Projected score is shown until the first review or admin recompute.</p>
          </div>
        ) : (
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
            <div className="font-bold">Health score is current</div>
            <p className="mt-1">Last computed: {new Date(score.computed_at).toLocaleString()}</p>
          </div>
        )}
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <Bar label="Coverage" value={score.coverage} />
        <Bar label="Freshness" value={score.freshness} />
        <Bar label="Balance" value={score.balance} />
        <Bar label="Consistency" value={score.consistency} />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
        <div className="rounded-xl bg-slate-50 p-3"><div className="font-bold">Active</div><div>{String(score.counts.active ?? '—')}</div></div>
        <div className="rounded-xl bg-slate-50 p-3"><div className="font-bold">Review</div><div>{String(score.counts.review_required ?? '—')}</div></div>
        <div className="rounded-xl bg-slate-50 p-3"><div className="font-bold">Fresh active</div><div>{String(score.counts.fresh_active ?? '—')}</div></div>
        <div className="rounded-xl bg-slate-50 p-3"><div className="font-bold">Levels</div><div>{String(score.counts.populated_active_levels ?? '—')} / {String(score.counts.total_levels ?? '—')}</div></div>
      </div>
    </section>
  );
}
