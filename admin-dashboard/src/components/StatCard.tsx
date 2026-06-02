'use client';

interface Props {
  label: string;
  value: number | string;
  icon: string;
  sub?: string;
}

export default function StatCard({ label, value, icon, sub }: Props) {
  return (
    <div className="bg-gray-800 rounded-xl p-5 border border-gray-700 flex items-start gap-4">
      <span className="text-3xl">{icon}</span>
      <div>
        <p className="text-gray-400 text-sm">{label}</p>
        <p className="text-2xl font-bold text-white mt-0.5">{value.toLocaleString()}</p>
        {sub && <p className="text-xs text-gray-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}
