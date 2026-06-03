import { GitBranch } from 'lucide-react';
import type { AppState, KnowledgeNode } from '../lib/types';
import StatusBadge from './StatusBadge';

function TypeBadge({ type }: { type: string }) {
  return <span className="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-black uppercase tracking-wide text-slate-500">{type}</span>;
}

function TreeNode({ node, childrenMap, nodesById, depth = 0, skipped }: { node: KnowledgeNode; childrenMap: Map<string, string[]>; nodesById: Map<string, KnowledgeNode>; depth?: number; skipped: Set<string> }) {
  const children = childrenMap.get(node.id) ?? [];
  const isSkipped = skipped.has(node.id);

  return (
    <div className="relative">
      <div className="rounded-2xl border border-slate-200 bg-white p-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-black text-slate-900">{node.id}</span>
          <StatusBadge status={node.status} />
          <TypeBadge type={node.type} />
          {depth > 0 && <span className="rounded-full bg-slate-900 px-2 py-1 text-[10px] font-black text-white">depth {depth}</span>}
          {isSkipped && <span className="rounded-full bg-indigo-100 px-2 py-1 text-[10px] font-black text-indigo-700">CASCADE_SKIP</span>}
        </div>
        <div className="mt-2 text-sm font-semibold text-slate-700">{node.title}</div>
        {node.superseded_by && <div className="mt-1 text-xs text-slate-500">Superseded by {node.superseded_by}</div>}
      </div>
      {children.length > 0 && (
        <div className="ml-5 mt-3 space-y-3 border-l border-dashed border-slate-300 pl-5">
          {children.map((childId) => {
            const child = nodesById.get(childId);
            return child ? <TreeNode key={childId} node={child} childrenMap={childrenMap} nodesById={nodesById} depth={depth + 1} skipped={skipped} /> : null;
          })}
        </div>
      )}
    </div>
  );
}

export default function CascadeTree({ state }: { state: AppState }) {
  const nodesById = new Map(state.knowledge_nodes.map((node) => [node.id, node]));
  const childrenMap = new Map<string, string[]>();
  state.edges.filter((edge) => edge.edge_type === 'DERIVED_FROM').forEach((edge) => {
    const children = childrenMap.get(edge.target_id) ?? [];
    children.push(edge.source_id);
    childrenMap.set(edge.target_id, children.sort());
  });
  const rootId = state.last_cascade?.source_node_id ?? 'N-M08';
  const root = nodesById.get(rootId);
  const skipped = new Set(state.last_cascade?.skipped_nodes.map((row) => row.node_id) ?? []);

  return (
    <section className="card p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500"><GitBranch size={16} /> Cascade Visualization</div>
          <h2 className="text-xl font-black text-slate-950">DERIVED_FROM tree</h2>
        </div>
        {state.last_cascade && (
          <div className="rounded-2xl bg-slate-50 p-3 text-right text-sm">
            <div><span className="font-black">{state.last_cascade.affected_count}</span> affected</div>
            <div><span className="font-black">{state.last_cascade.skipped_count}</span> skipped</div>
          </div>
        )}
      </div>
      {root ? <TreeNode node={root} childrenMap={childrenMap} nodesById={nodesById} skipped={skipped} /> : <p>Root node not found.</p>}
    </section>
  );
}
