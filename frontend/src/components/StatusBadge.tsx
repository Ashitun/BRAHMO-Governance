import type { Status } from '../lib/types';

const label: Record<Status, string> = {
  ACTIVE: '✅ ACTIVE',
  REVIEW_REQUIRED: '⚠️ REVIEW',
  SUPERSEDED: '🔒 SUPERSEDED',
  EXPIRED: '⌛ EXPIRED',
  LEGAL_HOLD: '⚖️ LEGAL HOLD',
};

const styles: Record<Status, string> = {
  ACTIVE: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  REVIEW_REQUIRED: 'bg-amber-50 text-amber-800 border border-amber-200',
  SUPERSEDED: 'bg-slate-100 text-slate-700 border border-slate-300',
  EXPIRED: 'bg-rose-50 text-rose-700 border border-rose-200',
  LEGAL_HOLD: 'bg-indigo-50 text-indigo-700 border border-indigo-200',
};

export default function StatusBadge({ status }: { status: Status }) {
  return <span className={`badge ${styles[status]}`}>{label[status]}</span>;
}
