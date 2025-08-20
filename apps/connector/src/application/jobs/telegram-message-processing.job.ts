import { Inject, Injectable } from '@nestjs/common';
import type { Job, JobFactory } from '../../domain/interfaces/job-factory.interface.js';

export interface TelegramMessageJobData {
  chatId: number;
  messageText: string;
  telegramUserId: number;
  timestamp: string;
  messageId: number;
}

@Injectable()
export class TelegramMessageProcessingJob {
  public readonly job: Job;

  constructor(@Inject('JobFactory') jobFactory: JobFactory) {
    this.job = jobFactory.createJob({
      name: 'telegram_received_messages'
    });
  }

  async scheduleMessageProcessing(chatId: number, messageText: string, telegramUserId: number, timestamp: string, messageId: number) {
    await this.job.scheduleTask({
      chatId,
      messageText,
      telegramUserId,
      timestamp,
      messageId
    });
  }
}
