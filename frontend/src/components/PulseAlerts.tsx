import { Bell } from 'lucide-react';
import type { PulseAlert, User } from '../lib/types';

const severityIcon = {
  URGENT: '⛔',
  WARNING: '⚠️',
  INFO: 'ℹ️',
};

const severityStyle = {
  URGENT: 'border-rose-200 bg-rose-50 text-rose-900',
  WARNING: 'border-amber-200 bg-amber-50 text-amber-900',
  INFO: 'border-sky-200 bg-sky-50 text-sky-900',
};

export default function PulseAlerts({ alerts, users, currentUserId }: { alerts: PulseAlert[]; users: User[]; currentUserId: string }) {
  const visible = alerts.filter((alert) => alert.user_id === currentUserId);
  const currentUser = users.find((user) => user.id === currentUserId);

  return (
    <section className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500"><Bell size={16} /> Pulse Alerts</div>
          <h2 className="text-xl font-black text-slate-950">{currentUser?.name ?? 'Current user'}</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">{visible.length} alert(s)</span>
      </div>

      {visible.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 p-5 text-sm text-slate-500">No alerts for this user. After the Medicine cascade, Meera and Ananya receive alerts, while Ortho and Viewer users do not.</div>
      ) : (
        <div className="space-y-3">
          {visible.map((alert) => (
            <article key={alert.id} className={`rounded-2xl border p-4 ${severityStyle[alert.severity]}`}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-black uppercase tracking-wide">{severityIcon[alert.severity]} {alert.severity}</div>
                  <h3 className="mt-1 font-black">{alert.title}</h3>
                </div>
                {alert.is_read ? <span className="text-xs font-bold opacity-70">read</span> : <span className="text-xs font-bold">new</span>}
              </div>
              <p className="mt-2 text-sm leading-6">{alert.body}</p>
              {alert.link && <div className="mt-3 text-xs font-bold">Link: {alert.link}</div>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
