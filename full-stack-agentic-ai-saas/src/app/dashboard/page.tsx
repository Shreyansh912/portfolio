import Link from 'next/link';
import { Bot, Plus, ArrowUpRight } from 'lucide-react';
import { createClient } from '@/lib/supabase/server';

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Query actual task count for the current user
  const { count } = await supabase
    .from('agent_tasks')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user?.id || '');

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Workspace Overview</h2>
        <p className="mt-1 text-sm text-slate-400">
          Monitor your agent activity, runs, and active subscription quota.
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Total Tasks</span>
            <Bot className="h-5 w-5 text-cyan-400" />
          </div>
          <div className="mt-4 text-3xl font-extrabold text-white">{count ?? 0}</div>
          <p className="mt-1 text-xs text-slate-500">Tasks logged in database</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Current Plan</span>
            <span className="rounded bg-cyan-500/10 px-2 py-0.5 text-xs font-semibold text-cyan-400">Free</span>
          </div>
          <div className="mt-4 text-3xl font-extrabold text-white">Starter</div>
          <p className="mt-1 text-xs text-slate-500">10 tasks/month limit</p>
        </div>
      </div>

      {/* Action / Empty State */}
      <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/20 p-12 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-cyan-400">
          <Bot className="h-6 w-6" />
        </div>
        <h3 className="mt-4 text-lg font-semibold text-white">No active agent runs</h3>
        <p className="mx-auto mt-2 max-w-md text-sm text-slate-400">
          Ready to run your first task? In the next phase, we will connect the OpenAI agent execution engine to run calculations and research.
        </p>
        <div className="mt-6 flex justify-center">
          <button
            disabled
            className="flex items-center gap-2 rounded-lg bg-cyan-500/50 px-4 py-2 text-sm font-semibold text-slate-950 cursor-not-allowed"
          >
            <Plus className="h-4 w-4" /> New AI Task (Phase 7)
          </button>
        </div>
      </div>
    </div>
  );
}