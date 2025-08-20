import { Provider } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

export const SUPABASE_CLIENT = 'SUPABASE_CLIENT';

export const supabaseProvider: Provider = {
  provide: SUPABASE_CLIENT,
  useFactory: (configService: ConfigService): SupabaseClient => {
    const supabaseUrl = configService.get<string>('supabase.url');
    const supabaseKey = configService.get<string>('supabase.serviceKey');
    
    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Supabase configuration missing: SUPABASE_URL and SUPABASE_ANON_KEY/SUPABASE_SERVICE_KEY required');
    }
    
    return createClient(supabaseUrl, supabaseKey);
  },
  inject: [ConfigService],
};
