'use client';
import { useState, FormEvent } from 'react';
import { broadcast } from '@/lib/api';

interface Result {
  sent: number;
  failed: number;
  total: number;
}

export default function BroadcastPage() {
  const [message, setMessage] = useState('');
  const [target, setTarget] = useState<'all' | 'premium'>('all');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    setLoading(true);
    setResult(null);
    setError('');
    try {
      const r = await broadcast(message, target);
      setResult(r);
      setMessage('');
    } catch {
      setError('Failed to send broadcast. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-xl font-bold text-white mb-6">Broadcast Message</h1>

      <div className="max-w-xl">
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Target audience</label>
              <div className="flex gap-3">
                {(['all', 'premium'] as const).map((t) => (
                  <label
                    key={t}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-colors ${
                      target === t
                        ? 'border-indigo-500 bg-indigo-950 text-indigo-300'
                        : 'border-gray-700 text-gray-500 hover:border-gray-600'
                    }`}
                  >
                    <input
                      type="radio"
                      name="target"
                      value={t}
                      checked={target === t}
                      onChange={() => setTarget(t)}
                      className="hidden"
                    />
                    {t === 'all' ? '👥 All users' : '⭐ Premium only'}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Message <span className="text-gray-600">(HTML supported)</span>
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={6}
                required
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 resize-none"
                placeholder="Hello! We have exciting news for you…"
              />
              <p className="text-xs text-gray-600 mt-1">{message.length} characters</p>
            </div>

            {error && (
              <div className="p-3 bg-red-900/30 border border-red-800 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {result && (
              <div className="p-4 bg-green-900/20 border border-green-800 rounded-lg">
                <p className="text-green-400 font-medium mb-1">✓ Broadcast sent!</p>
                <p className="text-sm text-gray-400">
                  Sent: <span className="text-white">{result.sent}</span> &nbsp;·&nbsp;
                  Failed: <span className={result.failed > 0 ? 'text-red-400' : 'text-white'}>{result.failed}</span> &nbsp;·&nbsp;
                  Total: <span className="text-white">{result.total}</span>
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !message.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900 disabled:text-indigo-700 text-white py-2.5 rounded-lg font-medium transition-colors"
            >
              {loading ? 'Sending…' : `Send to ${target === 'all' ? 'all users' : 'premium users'}`}
            </button>
          </form>
        </div>

        <div className="mt-4 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
          <p className="text-xs text-gray-500">
            <span className="text-gray-400 font-medium">Note:</span> Broadcast sends to all active users.
            Users who have blocked the bot will automatically be marked as failed.
            Use HTML tags like <code className="text-indigo-400">&lt;b&gt;</code>,{' '}
            <code className="text-indigo-400">&lt;i&gt;</code>,{' '}
            <code className="text-indigo-400">&lt;a href=&quot;...&quot;&gt;</code> for formatting.
          </p>
        </div>
      </div>
    </div>
  );
}
