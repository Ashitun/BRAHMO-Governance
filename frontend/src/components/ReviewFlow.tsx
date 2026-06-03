import { ClipboardCheck } from 'lucide-react';
import type { KnowledgeNode, User } from '../lib/types';
import StatusBadge from './StatusBadge';

export default function ReviewFlow({ nodes, currentUser, onReview }: { nodes: KnowledgeNode[]; currentUser: User | undefined; onReview: (nodeId: string, decision: 'confirm' | 'expire' | 'supersede') => void }) {
  const reviewNodes = nodes.filter((node) => node.status === 'REVIEW_REQUIRED');
  return (
    <section className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500"><ClipboardCheck size={16} /> Review Flow</div>
          <h2 className="text-xl font-black text-slate-950">Human review queue</h2>
        </div>
        <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">{reviewNodes.length} waiting</span>
      </div>

      {reviewNodes.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 p-5 text-sm text-slate-500">No REVIEW_REQUIRED nodes. Trigger the Sepsis cascade to create the review queue.</div>
      ) : (
        <div className="space-y-3">
          {reviewNodes.map((node) => (
            <article key={node.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-black text-slate-900">{node.id}</span>
                <StatusBadge status={node.status} />
                <span className="rounded-full bg-white px-2 py-1 text-xs font-bold text-slate-500">{node.department}</span>
              </div>
              <h3 className="mt-2 font-bold text-slate-900">{node.title}</h3>
              <p className="mt-1 line-clamp-2 text-sm text-slate-600">{node.content}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <button className="btn-primary" onClick={() => onReview(node.id, 'confirm')} disabled={!currentUser}>Still valid → ACTIVE</button>
                <button className="btn-warning" onClick={() => onReview(node.id, 'supersede')} disabled={!currentUser}>Needs update → SUPERSEDE</button>
                <button className="btn-danger" onClick={() => onReview(node.id, 'expire')} disabled={!currentUser}>No longer relevant → EXPIRE</button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
