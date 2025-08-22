import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import configuration from './config/configuration.js';
import { HealthController } from './presentation/controllers/health.controller.js';
import { TelegramController } from './presentation/controllers/telegram.controller.js';
import { MessageProcessorService } from './application/services/message-processor.service.js';
import { WorkerProcessorService } from './application/services/worker-processor.service.js';
import { TelegramMessageProcessingJob } from './application/jobs/telegram-message-processing.job.js';
import { TelegramResponseSendingJob } from './application/jobs/telegram-response-sending.job.js';
import { RabbitMQJobFactory } from './infrastructure/services/rabbitmq-job-factory.service.js';
import { TelegramService } from './infrastructure/services/telegram.service.js';
import { TelegramPollingService } from './infrastructure/services/telegram-polling.service.js';
import { rabbitmqProvider } from './infrastructure/providers/rabbitmq.provider.js';
import { telegramHttpClientProvider } from './infrastructure/providers/telegram-http-client.provider.js';
import { IS_POLLING_ENABLED } from './infrastructure/constants/injection-tokens.js';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
  ],
  controllers: [HealthController, TelegramController],
  providers: [
    {
      provide: IS_POLLING_ENABLED,
      useFactory: (configService: ConfigService) => configService.get<boolean>('telegram.isPollingEnabled'),
      inject: [ConfigService],
    },
    rabbitmqProvider,
    telegramHttpClientProvider,
    MessageProcessorService,
    {
      provide: WorkerProcessorService,
      useFactory: (responseSendingJob: TelegramResponseSendingJob) => new WorkerProcessorService([responseSendingJob.job]),
      inject: [TelegramResponseSendingJob],
    },
    TelegramPollingService,
    RabbitMQJobFactory,
    TelegramMessageProcessingJob,
    TelegramResponseSendingJob,
    {
      provide: 'JobFactory',
      useClass: RabbitMQJobFactory,
    },
    {
      provide: 'ITelegramService',
      useClass: TelegramService,
    },
  ],
})
export class AppModule { }
