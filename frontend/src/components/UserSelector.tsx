import type { User } from '../lib/types';

export default function UserSelector({ users, currentUserId, setCurrentUserId }: { users: User[]; currentUserId: string; setCurrentUserId: (id: string) => void }) {
  return (
    <label className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-soft">
      <span className="font-semibold text-slate-500">User</span>
      <select className="bg-transparent font-bold text-slate-900 outline-none" value={currentUserId} onChange={(event) => setCurrentUserId(event.target.value)}>
        {users.map((user) => (
          <option key={user.id} value={user.id}>{user.name} — {user.role}</option>
        ))}
      </select>
    </label>
  );
}
