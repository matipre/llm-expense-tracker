import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import configuration from './config/configuration.js';
import { HealthController } from './presentation/controllers/health.controller.js';
import { TelegramController } from './presentation/controllers/telegram.controller.js';
import { MessageProcessorService } from './application/services/message-processor.service.js';
import { WorkerProcessorService } from './application/services/worker-processor.service.js';
import { TelegramMessageProcessingJob } from './application/jobs/telegram-message-processing.job.js';
import { TelegramResponseSendingJob } from './application/jobs/telegram-response-sending.job.js';
import { SupabaseJobFactory } from './infrastructure/services/supabase-job-factory.service.js';
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
    WorkerProcessorService,
    TelegramPollingService,
    SupabaseJobFactory,
    TelegramMessageProcessingJob,
    TelegramResponseSendingJob,
    {
      provide: 'JobFactory',
      useClass: SupabaseJobFactory,
    },
    {
      provide: 'ITelegramService',
      useClass: TelegramService,
    },
  ],
})
export class AppModule {}
