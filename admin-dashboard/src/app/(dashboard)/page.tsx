'use client';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { getStats, getGrowth } from '@/lib/api';
import StatCard from '@/components/StatCard';

const GrowthChart = dynamic(() => import('@/components/GrowthChart'), { ssr: false });

interface Stats {
  total_users: number;
  active_today: number;
  premium_users: number;
  total_messages: number;
  new_today: number;
  friend_profiles: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [growth, setGrowth] = useState<{ date: string; users: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getStats(), getGrowth()])
      .then(([s, g]) => {
        setStats(s);
        setGrowth(g.data || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Loading…</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <StatCard label="Total Users" value={stats?.total_users ?? 0} icon="👥" />
        <StatCard label="Active Today" value={stats?.active_today ?? 0} icon="⚡" />
        <StatCard label="Premium" value={stats?.premium_users ?? 0} icon="⭐" />
        <StatCard label="New Today" value={stats?.new_today ?? 0} icon="🆕" />
        <StatCard label="AI Messages" value={stats?.total_messages ?? 0} icon="💬" sub="all time" />
        <StatCard label="Friend Profiles" value={stats?.friend_profiles ?? 0} icon="🤝" />
      </div>

      <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <h2 className="text-sm font-semibold text-gray-400 mb-4">New Users — Last 30 Days</h2>
        {growth.length > 0 ? (
          <GrowthChart data={growth} />
        ) : (
          <p className="text-gray-600 text-sm text-center py-8">No data yet</p>
        )}
      </div>
    </div>
  );
}
