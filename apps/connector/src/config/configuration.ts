export interface AppConfig {
  port: number;
  environment: string;
  telegram: {
    botToken: string;
  };
  database: {
    url: string;
  };
  rabbitmq: {
    url: string;
  };
  queue: {
    telegramMessageQueue: string;
    botResponseQueue: string;
    visibilityTimeout: number;
    pollInterval: number;
    maxRetries: number;
  };
}

export default (): AppConfig => ({
  port: parseInt(process.env.CONNECTOR_SERVICE_PORT || '3001', 10),
  environment: process.env.NODE_ENV || 'development',
  telegram: {
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
  },
  database: {
    url: process.env.DATABASE_URL || '',
  },
  rabbitmq: {
    url: process.env.RABBITMQ_URL || '',
  },
  queue: {
    telegramMessageQueue: process.env.TELEGRAM_MESSAGE_QUEUE || 'telegram_received_messages',
    botResponseQueue: process.env.BOT_RESPONSE_QUEUE || 'telegram_bot_responses',
    visibilityTimeout: parseInt(process.env.QUEUE_VISIBILITY_TIMEOUT || '30', 10),
    pollInterval: parseInt(process.env.QUEUE_POLL_INTERVAL || '200', 10),
    maxRetries: parseInt(process.env.QUEUE_MAX_RETRIES || '3', 10),
  },
});
