export interface AppConfig {
  port: number;
  environment: string;
  telegram: {
    botToken: string;
  };
  rabbitmq: {
    url: string;
    exchange: string;
    dlxExchange: string;
    connectionRetries: number;
    connectionRetryDelay: number;
  };
  queue: {
    telegramMessageQueue: string;
    botResponseQueue: string;
    maxRetries: number;
    prefetchCount: number;
  };
}

export default (): AppConfig => ({
  port: parseInt(process.env.CONNECTOR_SERVICE_PORT || '3001', 10),
  environment: process.env.NODE_ENV || 'development',
  telegram: {
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
  },
  rabbitmq: {
    url: process.env.RABBITMQ_URL || 'amqp://expensio_user:expensio_password@localhost:5672',
    exchange: process.env.RABBITMQ_EXCHANGE || 'telegram_exchange',
    dlxExchange: process.env.RABBITMQ_DLX_EXCHANGE || 'telegram_dlx_exchange',
    connectionRetries: parseInt(process.env.RABBITMQ_CONNECTION_RETRIES || '5', 10),
    connectionRetryDelay: parseInt(process.env.RABBITMQ_CONNECTION_RETRY_DELAY || '5000', 10),
  },
  queue: {
    telegramMessageQueue: process.env.TELEGRAM_MESSAGE_QUEUE || 'telegram_received_messages',
    botResponseQueue: process.env.BOT_RESPONSE_QUEUE || 'telegram_bot_responses',
    maxRetries: parseInt(process.env.QUEUE_MAX_RETRIES || '3', 10),
    prefetchCount: parseInt(process.env.QUEUE_PREFETCH_COUNT || '10', 10),
  },
});
