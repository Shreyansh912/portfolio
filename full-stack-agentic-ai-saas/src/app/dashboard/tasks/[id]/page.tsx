'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Play, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Wrench, 
  Terminal, 
  Sparkles,
  Copy,
  Check,
  Trash2,
  RefreshCw,
  Hash
} from 'lucide-react';

interface AuditLog {
  role: string;
  content?: string | null;
  tool_calls?: any[];
  tool_name?: string;
  tool_result?: string;
}

interface TaskDetail {
  id: string;
  title: string;
  prompt: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: {
    output?: string;
    audit_logs?: AuditLog[];
    iterations?: number;
  };
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export default function TaskDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTask = async () => {
    try {
      const res = await fetch(`/api/tasks/${id}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch task');
      setTask(data.task);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTask();
  }, [id]);

  const handleExecute = async () => {
    setRunning(true);
    setError(null);

    try {
      const res = await fetch(`/api/tasks/${id}/run`, {
        method: 'POST',
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Agent execution failed');
      setTask(data.task);
    } catch (err: any) {
      setError(err.message);
      await fetchTask();
    } finally {
      setRunning(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      return;
    }

    setDeleting(true);
    try {
      const res = await fetch(`/api/tasks/${id}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Failed to delete task');
      router.push('/dashboard/tasks');
      router.refresh();
    } catch (err: any) {
      setError(err.message);
      setDeleting(false);
    }
  };

  const handleCopyOutput = () => {
    if (!task?.result?.output) return;
    navigator.clipboard.writeText(task.result.output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-slate-400">
        <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  if (error && !task) {
    return (
      <div className="rounded-xl border border-rose-500/20 bg-rose-500/10 p-6 text-rose-400">
        <p className="font-semibold">{error}</p>
        <Link
          href="/dashboard/tasks"
          className="mt-4 inline-flex items-center gap-2 text-sm text-cyan-400 hover:underline"
        >
          <ArrowLeft className="h-4 w-4" /> Return to Tasks
        </Link>
      </div>
    );
  }

  if (!task) return null;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Top Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/tasks"
            className="rounded-lg border border-slate-800 p-2 text-slate-400 hover:bg-slate-900 hover:text-white transition"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h2 className="text-xl font-bold text-white">{task.title}</h2>
            <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
              <span>Created {new Date(task.created_at).toLocaleString()}</span>
              {task.completed_at && (
                <>
                  <span>•</span>
                  <span>Finished {new Date(task.completed_at).toLocaleTimeString()}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Status Badge */}
          <span
            className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
              task.status === 'completed'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : task.status === 'failed'
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                : task.status === 'running'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}
          >
            {task.status === 'completed' && <CheckCircle2 className="h-3.5 w-3.5" />}
            {task.status === 'failed' && <AlertCircle className="h-3.5 w-3.5" />}
            {task.status === 'running' && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            {task.status === 'pending' && <Clock className="h-3.5 w-3.5" />}
            {task.status.toUpperCase()}
          </span>

          {/* Delete Button */}
          <button
            onClick={handleDelete}
            disabled={deleting || running}
            title="Delete task"
            className="rounded-lg border border-slate-800 p-2 text-slate-400 hover:bg-rose-950/30 hover:border-rose-900 hover:text-rose-400 transition disabled:opacity-50"
          >
            {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
          </button>

          {/* Execute / Re-run Button */}
          <button
            onClick={handleExecute}
            disabled={running || task.status === 'running'}
            className="flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:opacity-50"
          >
            {running ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Running Agent...
              </>
            ) : task.status === 'completed' ? (
              <>
                <RefreshCw className="h-4 w-4" /> Re-run Agent
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-current" /> Run Agent
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-400 flex items-center justify-between">
          <span>{error}</span>
        </div>
      )}

      {/* Task Objective Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
          User Objective / Instructions
        </h3>
        <p className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">{task.prompt}</p>
      </div>

      {/* Agent Final Output */}
      {task.result?.output && (
        <div className="rounded-xl border border-cyan-500/30 bg-slate-900/60 p-6 shadow-lg shadow-cyan-950/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-cyan-400">
              <Sparkles className="h-4 w-4" />
              <h3 className="text-sm font-semibold uppercase tracking-wider">Final Agent Output</h3>
            </div>
            <button
              onClick={handleCopyOutput}
              className="flex items-center gap-1.5 rounded border border-slate-800 bg-slate-950/80 px-2.5 py-1 text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-400" /> Copied!
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" /> Copy Output
                </>
              )}
            </button>
          </div>
          <div className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed font-sans bg-slate-950/80 p-4 rounded-lg border border-slate-800">
            {task.result.output}
          </div>
        </div>
      )}

      {/* Audit Logs & Tool Execution History */}
      {task.result?.audit_logs && task.result.audit_logs.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-6 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300">
              <Terminal className="h-4 w-4 text-cyan-400" />
              <h3 className="text-sm font-semibold">Execution Audit Trail</h3>
            </div>
            {task.result.iterations && (
              <span className="flex items-center gap-1 text-xs text-slate-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                <Hash className="h-3 w-3 text-cyan-400" /> Iterations: {task.result.iterations}
              </span>
            )}
          </div>

          <div className="space-y-2 mt-4">
            {task.result.audit_logs.map((log, index) => (
              <div
                key={index}
                className="rounded-lg border border-slate-800/80 bg-slate-950/60 p-3 text-xs font-mono"
              >
                {log.role === 'tool' ? (
                  <div className="space-y-1">
                    <span className="inline-flex items-center gap-1.5 text-cyan-400 font-semibold">
                      <Wrench className="h-3 w-3" /> Tool Executed: {log.tool_name}
                    </span>
                    <pre className="text-slate-300 whitespace-pre-wrap mt-1 bg-slate-900/60 p-2 rounded border border-slate-800/50 overflow-x-auto">
                      {log.tool_result}
                    </pre>
                  </div>
                ) : (
                  <div className="text-slate-400">
                    <span className="text-cyan-500 font-semibold uppercase">{log.role}:</span>{' '}
                    {log.content || (
                      <span className="italic text-slate-500">
                        Dispatched function call: {log.tool_calls?.[0]?.function?.name || 'tool'}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}