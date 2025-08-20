import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { TelegramResponseSendingJob } from '../jobs/telegram-response-sending.job.js';

@Injectable()
export class WorkerProcessorService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(WorkerProcessorService.name);

  constructor(
    private readonly telegramResponseJob: TelegramResponseSendingJob
  ) {}

  async onModuleInit() {
    this.logger.log('Starting worker processors');
    await this.startWorkers();
  }

  async onModuleDestroy() {
    this.logger.log('Stopping worker processors');
    await this.stopWorkers();
  }

  private async startWorkers(): Promise<void> {
    // Start only the response sending worker - Python handles message processing
    await this.telegramResponseJob.job.turnOn();
    this.logger.log('TelegramResponseSending worker started');
  }

  private async stopWorkers(): Promise<void> {
    await this.telegramResponseJob.job.turnOff();
    this.logger.log('All workers stopped');
  }
}
