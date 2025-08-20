import { Injectable, Logger } from '@nestjs/common';
import { TelegramUpdate, ProcessedMessage } from '../../domain/entities/telegram-message.entity.js';
import { TelegramMessageProcessingJob } from '../jobs/telegram-message-processing.job.js';

@Injectable()
export class MessageProcessorService {
  private readonly logger = new Logger(MessageProcessorService.name);

  constructor(private readonly telegramJob: TelegramMessageProcessingJob) {}

  async processWebhookUpdate(update: TelegramUpdate): Promise<void> {
    this.logger.log(`Processing update: ${update.update_id}`);

    if (!update.message || !update.message.text) {
      this.logger.log('No text message found in update, skipping');
      return;
    }

    const message = update.message;
    
    // Only process private chat messages for now
    if (message.chat.type !== 'private') {
      this.logger.log('Ignoring non-private chat message');
      return;
    }

    const processedMessage: ProcessedMessage = {
      telegramUserId: message.from?.id || 0,
      chatId: message.chat.id,
      messageText: message.text,
      timestamp: new Date(message.date * 1000),
      messageId: message.message_id,
    };

    try {
      await this.telegramJob.scheduleMessageProcessing(
        processedMessage.chatId,
        processedMessage.messageText,
        processedMessage.telegramUserId,
        processedMessage.timestamp.toISOString(),
        processedMessage.messageId
      );
      this.logger.log(`Message queued for processing from user ${processedMessage.telegramUserId}`);
    } catch (error) {
      this.logger.error('Failed to queue message for processing', error);
      throw error;
    }
  }
}
