'use client';
import { useState, useEffect, useCallback } from 'react';
import { getUsers, addPremium, removePremium, banUser, unbanUser } from '@/lib/api';

interface User {
  user_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  language_code: string;
  created_at: string;
  last_active: string;
  is_active: boolean;
  is_premium: boolean;
  subscription_tier: string | null;
}

interface UsersData {
  users: User[];
  total: number;
  page: number;
  pages: number;
}

function displayName(u: User) {
  const full = [u.first_name, u.last_name].filter(Boolean).join(' ');
  return full || u.username || `ID ${u.user_id}`;
}

export default function UsersPage() {
  const [data, setData] = useState<UsersData | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<number | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    getUsers(page, query)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page, query]);

  useEffect(() => { load(); }, [load]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setQuery(search);
  };

  const act = async (fn: () => Promise<unknown>, userId: number) => {
    setActionId(userId);
    try { await fn(); await load(); } catch { /* ignore */ }
    finally { setActionId(null); }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-white">Users</h1>
        {data && <p className="text-gray-500 text-sm">{data.total.toLocaleString()} total</p>}
      </div>

      <form onSubmit={handleSearch} className="flex gap-2 mb-5">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name, username or ID…"
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-lg transition-colors"
        >
          Search
        </button>
      </form>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <p className="text-gray-500">Loading…</p>
        </div>
      ) : (
        <>
          <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">User</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium hidden sm:table-cell">ID</th>
                  <th className="text-left px-4 py-3 text-gray-500 font-medium">Status</th>
                  <th className="text-right px-4 py-3 text-gray-500 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {data?.users.map((u) => (
                  <tr key={u.user_id} className="hover:bg-gray-800/50 transition-colors">
                    <td className="px-4 py-3">
                      <p className="text-white font-medium">{displayName(u)}</p>
                      {u.username && <p className="text-gray-500 text-xs">@{u.username}</p>}
                    </td>
                    <td className="px-4 py-3 text-gray-500 hidden sm:table-cell">{u.user_id}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-col gap-1">
                        {u.is_premium && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-yellow-900/40 text-yellow-400 text-xs w-fit">
                            ⭐ Premium
                          </span>
                        )}
                        {!u.is_active && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-900/40 text-red-400 text-xs w-fit">
                            🚫 Banned
                          </span>
                        )}
                        {u.is_active && !u.is_premium && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-800 text-gray-500 text-xs w-fit">
                            Free
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex gap-1.5 justify-end flex-wrap">
                        {u.is_premium ? (
                          <button
                            onClick={() => act(() => removePremium(u.user_id), u.user_id)}
                            disabled={actionId === u.user_id}
                            className="px-2.5 py-1 text-xs rounded-lg bg-yellow-900/30 text-yellow-400 hover:bg-yellow-900/60 disabled:opacity-50 transition-colors"
                          >
                            Remove ⭐
                          </button>
                        ) : (
                          <button
                            onClick={() => act(() => addPremium(u.user_id), u.user_id)}
                            disabled={actionId === u.user_id}
                            className="px-2.5 py-1 text-xs rounded-lg bg-indigo-900/40 text-indigo-400 hover:bg-indigo-900/70 disabled:opacity-50 transition-colors"
                          >
                            + Premium
                          </button>
                        )}
                        {u.is_active ? (
                          <button
                            onClick={() => act(() => banUser(u.user_id), u.user_id)}
                            disabled={actionId === u.user_id}
                            className="px-2.5 py-1 text-xs rounded-lg bg-red-900/30 text-red-400 hover:bg-red-900/60 disabled:opacity-50 transition-colors"
                          >
                            Ban
                          </button>
                        ) : (
                          <button
                            onClick={() => act(() => unbanUser(u.user_id), u.user_id)}
                            disabled={actionId === u.user_id}
                            className="px-2.5 py-1 text-xs rounded-lg bg-green-900/30 text-green-400 hover:bg-green-900/60 disabled:opacity-50 transition-colors"
                          >
                            Unban
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {data?.users.length === 0 && (
              <p className="text-gray-600 text-sm text-center py-8">No users found</p>
            )}
          </div>

          {data && data.pages > 1 && (
            <div className="flex items-center justify-center gap-3 mt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 text-sm rounded-lg bg-gray-800 text-gray-400 hover:text-white disabled:opacity-40 transition-colors"
              >
                ← Prev
              </button>
              <span className="text-gray-500 text-sm">
                {page} / {data.pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                disabled={page === data.pages}
                className="px-3 py-1.5 text-sm rounded-lg bg-gray-800 text-gray-400 hover:text-white disabled:opacity-40 transition-colors"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
