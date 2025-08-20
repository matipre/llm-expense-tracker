export interface AppConfig {
  port: number;
  environment: string;
  telegram: {
    botToken: string;
  };
  supabase: {
    url: string;
    anonKey: string;
    serviceKey: string;
  };
}

export default (): AppConfig => ({
  port: parseInt(process.env.PORT || '3001', 10),
  environment: process.env.NODE_ENV || 'development',
  telegram: {
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
  },
  supabase: {
    url: process.env.SUPABASE_URL || '',
    anonKey: process.env.SUPABASE_ANON_KEY || '',
    serviceKey: process.env.SUPABASE_SERVICE_KEY || '',
  },
});
