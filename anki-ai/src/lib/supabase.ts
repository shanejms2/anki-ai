import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://cgpjekmxzuztwyghpamk.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNncGpla214enV6dHd5Z2hwYW1rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5NDIxMzYsImV4cCI6MjA2ODUxODEzNn0.vYUxYNBizYMrpnbsFeTPFBSznamE_2LJnX8bxekCrQA';

export const supabase = createClient(supabaseUrl, supabaseAnonKey); 