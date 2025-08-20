import { Injectable, Inject } from '@nestjs/common';
import type { JobFactory, Job } from '../../domain/interfaces/job-factory.interface.js';
import type { ITelegramService } from '../../domain/interfaces/telegram.interface.js';
import { createSuccessResult, createErrorResult } from '../../infrastructure/utils/queue-utils.js';

export interface TelegramResponseJobData {
  chatId: number;
  text: string;
}

@Injectable()
export class TelegramResponseSendingJob {
  public readonly job: Job;

  constructor(
    jobFactory: JobFactory,
    @Inject('ITelegramService') private readonly telegramService: ITelegramService
  ) {
    this.job = jobFactory.createJob({
      name: 'telegram_bot_responses',
      handler: async ({ data }) => {
        const responseData = data as TelegramResponseJobData;
        
        try {
          // Send response through Telegram service
          await this.telegramService.sendMessage(responseData.chatId, responseData.text);
          
          return createSuccessResult(`Response sent to chat ${responseData.chatId}`);
        } catch (error: any) {
          return createErrorResult(`Failed to send response: ${error.message}`);
        }
      },
    });
  }

  async scheduleResponseSending(chatId: number, text: string) {
    await this.job.scheduleTask({
      chatId,
      text
    });
  }
}
