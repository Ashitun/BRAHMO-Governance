import { useEffect, useMemo, useState } from 'react';
import { RefreshCw, Sparkles } from 'lucide-react';
import AuditTimeline from './components/AuditTimeline';
import CascadeTree from './components/CascadeTree';
import HealthDashboard from './components/HealthDashboard';
import NodeStatusActions from './components/NodeStatusActions';
import PulseAlerts from './components/PulseAlerts';
import ReviewFlow from './components/ReviewFlow';
import UserSelector from './components/UserSelector';
import { API_URL, getState, resetDemo, review, supersede, transition } from './lib/api';
import type { AppState } from './lib/types';

function ErrorBanner({ message, onClose }: { message: string | null; onClose: () => void }) {
  if (!message) return null;
  return (
    <div className="fixed left-1/2 top-4 z-50 w-[min(92vw,720px)] -translate-x-1/2 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-900 shadow-soft">
      <div className="flex items-start justify-between gap-3">
        <span>{message}</span>
        <button onClick={onClose} className="font-black">×</button>
      </div>
    </div>
  );
}

export default function App() {
  const [state, setState] = useState<AppState | null>(null);
  const [currentUserId, setCurrentUserId] = useState('U-MEERA');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setLoading(true);
      setState(await getState());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load state');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const currentUser = useMemo(() => state?.users.find((user) => user.id === currentUserId), [state, currentUserId]);

  async function runAction(action: () => Promise<{ state: AppState } | AppState>) {
    try {
      setLoading(true);
      const result = await action();
      setState('state' in result ? result.state : result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Action failed');
    } finally {
      setLoading(false);
    }
  }

  if (!state) {
    return (
      <main className="flex min-h-screen items-center justify-center p-8">
        <div className="card p-8 text-center">
          <RefreshCw className="mx-auto animate-spin" />
          <h1 className="mt-4 text-2xl font-black">Loading BRAHMO Governance</h1>
          <p className="mt-2 text-sm text-slate-500">API: {API_URL}</p>
          {error && <p className="mt-3 text-sm font-semibold text-rose-700">{error}</p>}
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 md:px-8">
      <ErrorBanner message={error} onClose={() => setError(null)} />
      <header className="mx-auto mb-6 max-w-7xl">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm font-black uppercase tracking-[0.22em] text-slate-500"><Sparkles size={16} /> BRAHMO</div>
            <h1 className="mt-1 text-3xl font-black tracking-tight text-slate-950 md:text-5xl">Governance Engine</h1>
            <p className="mt-2 max-w-3xl text-slate-600">Cascade invalidation, deferred health score recomputation, pulse alerts, review workflow, and auditable status transitions.</p>
          </div>
          <div className="flex flex-col gap-2 md:items-end">
            <UserSelector users={state.users} currentUserId={currentUserId} setCurrentUserId={setCurrentUserId} />
            <div className="text-xs text-slate-500">Demo time: {new Date(state.demo_now).toLocaleString()}</div>
          </div>
        </div>
      </header>

      <section className="mx-auto mb-6 grid max-w-7xl gap-3 md:grid-cols-4">
        <button
          className="btn-primary"
          disabled={loading}
          onClick={() => runAction(() => supersede({ node_id: 'N-M08', actor_id: currentUserId, new_id: 'N-M08-V3', new_title: 'Sepsis Protocol v3 (2026)', new_content: 'Supra Sepsis Bundle v3 (2026): blood cultures before antibiotics, lactate within 1 HOUR, 30mL/kg crystalloid for hypotension, and escalation review within 30 minutes.', cascade: true }))}
        >
          Supersede Sepsis v2 → v3
        </button>
        <button
          className="btn-secondary"
          disabled={loading}
          onClick={() => runAction(() => supersede({ node_id: 'N-O01', actor_id: currentUserId, new_id: 'N-O01-V2', new_title: 'DVT Prophylaxis Protocol v2', new_content: 'Updated ortho DVT prophylaxis protocol with risk-stratified anticoagulation and extended THR monitoring.', cascade: true }))}
        >
          Surprise: Ortho cascade
        </button>
        <button className="btn-secondary" disabled={loading} onClick={() => runAction(() => resetDemo())}>Reset demo</button>
        <button className="btn-secondary" disabled={loading} onClick={() => load()}>Refresh</button>
      </section>

      <div className="mx-auto grid max-w-7xl gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <div className="space-y-6">
          <HealthDashboard current={state.current_health_score} projected={state.projected_health_score} pending={state.health_pending} />
          <CascadeTree state={state} />
          <ReviewFlow
            nodes={state.knowledge_nodes}
            currentUser={currentUser}
            onReview={(nodeId, decision) => runAction(() => review({ node_id: nodeId, actor_id: currentUserId, decision }))}
          />
        </div>
        <div className="space-y-6">
          <PulseAlerts alerts={state.pulse_alerts} users={state.users} currentUserId={currentUserId} />
          <NodeStatusActions
            nodes={state.knowledge_nodes}
            currentUser={currentUser}
            onTransition={(nodeId, newStatus) => runAction(() => transition({ node_id: nodeId, actor_id: currentUserId, new_status: newStatus, reason: 'Manual dashboard transition' }))}
          />
          <AuditTimeline entries={state.audit_log} users={state.users} />
        </div>
      </div>
    </main>
  );
}
