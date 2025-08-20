import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import configuration from './config/configuration.js';
import { HealthController } from './presentation/controllers/health.controller.js';
import { TelegramController } from './presentation/controllers/telegram.controller.js';
import { MessageProcessorService } from './application/services/message-processor.service.js';
import { SupabaseQueueService } from './infrastructure/services/supabase-queue.service.js';
import { TelegramService } from './infrastructure/services/telegram.service.js';
import { TelegramPollingService } from './infrastructure/services/telegram-polling.service.js';
import { supabaseProvider } from './infrastructure/providers/supabase.provider.js';
import { telegramHttpClientProvider } from './infrastructure/providers/telegram-http-client.provider.js';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
  ],
  controllers: [HealthController, TelegramController],
  providers: [
    supabaseProvider,
    telegramHttpClientProvider,
    MessageProcessorService,
    TelegramPollingService,
    {
      provide: 'IQueueService',
      useClass: SupabaseQueueService,
    },
    {
      provide: 'ITelegramService',
      useClass: TelegramService,
    },
  ],
})
export class AppModule {}
