import { ListChecks } from 'lucide-react';
import type { AuditLogEntry, User } from '../lib/types';

export default function AuditTimeline({ entries, users }: { entries: AuditLogEntry[]; users: User[] }) {
  const usersById = new Map(users.map((user) => [user.id, user]));
  const visible = entries.slice(0, 18);
  return (
    <section className="card p-5">
      <div className="mb-4">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500"><ListChecks size={16} /> Audit Trail</div>
        <h2 className="text-xl font-black text-slate-950">Append-only event log</h2>
      </div>
      {visible.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 p-5 text-sm text-slate-500">No audit entries yet.</div>
      ) : (
        <div className="space-y-3">
          {visible.map((entry) => (
            <article key={entry.id} className="rounded-2xl border border-slate-200 p-4 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-slate-900 px-2 py-1 text-[10px] font-black text-white">{entry.action}</span>
                {entry.node_id && <span className="font-black text-slate-900">{entry.node_id}</span>}
                <span className="text-xs text-slate-500">{new Date(entry.timestamp).toLocaleString()}</span>
              </div>
              <div className="mt-2 text-slate-700">{entry.reason}</div>
              <div className="mt-1 text-xs text-slate-500">
                Actor: {usersById.get(entry.actor_id)?.name ?? entry.actor_id}
                {entry.old_value || entry.new_value ? ` | ${entry.old_value ?? '—'} → ${entry.new_value ?? '—'}` : ''}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
