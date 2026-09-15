import Link from 'next/link';
import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import { LayoutDashboard, History, Settings, LogOut, Sparkles } from 'lucide-react';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect('/login');
  }

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-slate-800 bg-slate-950/60">
        <div className="flex h-16 items-center gap-2 border-b border-slate-800 px-6 font-bold text-cyan-400">
          <Sparkles className="h-5 w-5" />
          AgentFlow AI
        </div>

        <nav className="flex-1 space-y-1 p-4">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-800"
          >
            <LayoutDashboard className="h-4 w-4 text-cyan-400" /> Overview
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition hover:bg-slate-800 hover:text-slate-200"
          >
            <History className="h-4 w-4" /> Task History
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition hover:bg-slate-800 hover:text-slate-200"
          >
            <Settings className="h-4 w-4" /> Settings
          </Link>
        </nav>

        {/* User Info & Sign Out */}
        <div className="border-t border-slate-800 p-4">
          <div className="mb-3 truncate px-2 text-xs text-slate-400">
            {user.email}
          </div>
          <form action="/api/auth/logout" method="POST">
            <button
              type="submit"
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition hover:bg-rose-950/40 hover:text-rose-400"
            >
              <LogOut className="h-4 w-4" /> Sign Out
            </button>
          </form>
        </div>
      </aside>

      {/* Main Workspace Area */}
      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 z-10 flex h-16 items-center border-b border-slate-800 bg-slate-950/50 px-8 backdrop-blur-sm">
          <span className="text-sm font-medium text-slate-400">Workspace / Overview</span>
        </header>
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}