import { NextResponse } from 'next/server';
import { checkUserQuota } from '@/lib/quota';
import { createClient } from '@/lib/supabase/server';
import { runAgentExecutionLoop } from '@/lib/agent/runner';

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function POST(request: Request, { params }: RouteParams) {
  const { id } = await params;
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // 1. Verify monthly usage quota first
  const quota = await checkUserQuota(supabase, user.id);
  if (!quota.allowed) {
    return NextResponse.json(
      {
        error: `Monthly quota exceeded (${quota.currentUsage}/${quota.limit} tasks). Please upgrade to Pro to continue executing agents.`,
      },
      { status: 403 }
    );
  }

  // 2. Fetch the task and verify ownership
  const { data: task, error: taskError } = await supabase
    .from('agent_tasks')
    .select('*')
    .eq('id', id)
    .eq('user_id', user.id)
    .single();

  if (taskError || !task) {
    return NextResponse.json({ error: 'Task not found' }, { status: 404 });
  }

  // 3. Mark task as running
  await supabase
    .from('agent_tasks')
    .update({ status: 'running' })
    .eq('id', id);

  // 4. Initialize a run record in agent_runs
  const { data: runRecord } = await supabase
    .from('agent_runs')
    .insert({
      task_id: task.id,
      user_id: user.id,
      status: 'running',
    })
    .select()
    .single();

  try {
    const execution = await runAgentExecutionLoop({
      prompt: task.prompt,
    });

    const completedAt = new Date().toISOString();

    // 5. Update the run record
    if (runRecord) {
      await supabase
        .from('agent_runs')
        .update({
          status: 'completed',
          completed_at: completedAt,
          metadata: { logs: execution.logs, iterations: execution.iterations },
        })
        .eq('id', runRecord.id);
    }

    // 6. Update task with final structured output
    const { data: updatedTask } = await supabase
      .from('agent_tasks')
      .update({
        status: 'completed',
        completed_at: completedAt,
        result: {
          output: execution.finalResponse,
          audit_logs: execution.logs,
          iterations: execution.iterations,
        },
      })
      .eq('id', task.id)
      .select()
      .single();

    // 7. Record usage event
    await supabase.from('usage_events').insert({
      user_id: user.id,
      task_id: task.id,
      event_type: 'task_execution',
      usage_amount: 1,
    });

    return NextResponse.json({ success: true, task: updatedTask });
  } catch (err: any) {
    const failedAt = new Date().toISOString();

    if (runRecord) {
      await supabase
        .from('agent_runs')
        .update({
          status: 'failed',
          completed_at: failedAt,
          metadata: { error: err.message },
        })
        .eq('id', runRecord.id);
    }

    await supabase
      .from('agent_tasks')
      .update({
        status: 'failed',
        error_message: err.message,
      })
      .eq('id', task.id);

    return NextResponse.json(
      { error: err.message || 'Execution failed' },
      { status: 500 }
    );
  }
}