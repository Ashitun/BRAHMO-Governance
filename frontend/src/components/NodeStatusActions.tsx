import { ShieldCheck } from 'lucide-react';
import type { KnowledgeNode, User } from '../lib/types';
import StatusBadge from './StatusBadge';

export default function NodeStatusActions({ nodes, currentUser, onTransition }: { nodes: KnowledgeNode[]; currentUser: User | undefined; onTransition: (nodeId: string, newStatus: string) => void }) {
  const featured = ['N-M08', 'N-HELD', 'N-O01'].map((id) => nodes.find((node) => node.id === id)).filter(Boolean) as KnowledgeNode[];
  return (
    <section className="card p-5">
      <div className="mb-4">
        <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500"><ShieldCheck size={16} /> Status State Machine</div>
        <h2 className="text-xl font-black text-slate-950">Manual transition checks</h2>
      </div>
      <div className="space-y-3">
        {featured.map((node) => (
          <article key={node.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-black">{node.id}</span>
              <StatusBadge status={node.status} />
            </div>
            <div className="mt-2 text-sm font-semibold text-slate-700">{node.title}</div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button className="btn-secondary" disabled={!currentUser || node.status === 'SUPERSEDED'} onClick={() => onTransition(node.id, 'LEGAL_HOLD')}>ADMIN legal hold</button>
              <button className="btn-secondary" disabled={!currentUser || node.status === 'SUPERSEDED'} onClick={() => onTransition(node.id, 'ACTIVE')}>Release / activate</button>
              <button className="btn-secondary" disabled={!currentUser || node.status === 'SUPERSEDED'} onClick={() => onTransition(node.id, 'REVIEW_REQUIRED')}>Manual review</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
