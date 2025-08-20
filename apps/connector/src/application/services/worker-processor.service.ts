import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { Job } from 'src/domain/interfaces/job-factory.interface.js';

@Injectable()
export class WorkerProcessorService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(WorkerProcessorService.name);

  constructor(
    private readonly jobs: Job[]
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
    for (const job of this.jobs) {
      await job.turnOn();
    }
    this.logger.log('TelegramResponseSending worker started');
  }

  private async stopWorkers(): Promise<void> {
    for (const job of this.jobs) {
      await job.turnOff();
    }
    this.logger.log('All workers stopped');
  }
}
