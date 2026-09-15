import { SupabaseClient } from '@supabase/supabase-js';

export async function checkUserQuota(supabase: SupabaseClient, userId: string) {
  // Fetch active subscription
  const { data: sub } = await supabase
    .from('subscriptions')
    .select('plan, status')
    .eq('user_id', userId)
    .single();

  const isPro = sub?.plan === 'pro' && sub?.status === 'active';
  if (isPro) {
    return { allowed: true, currentUsage: 0, limit: Infinity, plan: 'pro' };
  }

  // Calculate start of current UTC month
  const startOfMonth = new Date();
  startOfMonth.setUTCDate(1);
  startOfMonth.setUTCHours(0, 0, 0, 0);

  const { count } = await supabase
    .from('usage_events')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', userId)
    .gte('created_at', startOfMonth.toISOString());

  const currentUsage = count ?? 0;
  const freeLimit = 10;

  return {
    allowed: currentUsage < freeLimit,
    currentUsage,
    limit: freeLimit,
    plan: 'free',
  };
}