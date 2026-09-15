import Link from 'next/link';
import { 
  Bot, 
  Sparkles, 
  Terminal, 
  Cpu, 
  ShieldCheck, 
  Check, 
  ArrowRight,
  ChevronRight,
  Database,
  Layers
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-white">
      {/* Navigation */}
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/75 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400 ring-1 ring-cyan-500/30">
              <Bot className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold tracking-tight text-white">AgentFlow AI</span>
          </div>

          <nav className="hidden items-center gap-8 text-sm font-medium text-slate-400 md:flex">
            <a href="#features" className="transition hover:text-cyan-400">Features</a>
            <a href="#workflow" className="transition hover:text-cyan-400">Architecture</a>
            <a href="#pricing" className="transition hover:text-cyan-400">Pricing</a>
            <a href="#faq" className="transition hover:text-cyan-400">FAQ</a>
          </nav>

          <div className="flex items-center gap-4">
            <Link 
              href="/login" 
              className="text-sm font-medium text-slate-300 transition hover:text-white"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow-sm transition hover:bg-cyan-400"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 pt-24 pb-20 text-center md:pt-32">
        <div className="mx-auto max-w-4xl space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3.5 py-1 text-xs font-medium text-cyan-400">
            <Sparkles className="h-3.5 w-3.5" /> Autonomous Task Execution
          </div>

          <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl sm:leading-tight">
            Deploy Autonomous AI Agents <br />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
              With Verified Tool Execution
            </span>
          </h1>

          <p className="mx-auto max-w-2xl text-base text-slate-400 sm:text-lg">
            AgentFlow AI orchestrates goals, executes allowlisted backend tools, and persists deterministic output records directly to PostgreSQL.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/signup"
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 sm:w-auto"
            >
              Start Free Workspace <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-800 bg-slate-900/60 px-6 py-3 text-sm font-semibold text-slate-300 transition hover:bg-slate-800 sm:w-auto"
            >
              Access Dashboard
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}