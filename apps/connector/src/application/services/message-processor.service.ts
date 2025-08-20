import { Injectable, Logger, Inject } from '@nestjs/common';
import { TelegramUpdate, ProcessedMessage } from '../../domain/entities/telegram-message.entity.js';
import type { IQueueService } from '../../domain/interfaces/queue.interface.js';
import { QueueMessage } from '../../domain/interfaces/queue.interface.js';

@Injectable()
export class MessageProcessorService {
  private readonly logger = new Logger(MessageProcessorService.name);

  constructor(@Inject('IQueueService') private readonly queueService: IQueueService) {}

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

    // Send message to queue for bot processing
    const queueMessage: QueueMessage = {
      type: 'telegram_message',
      payload: processedMessage,
      timestamp: new Date(),
      retryCount: 0,
    };

    try {
      await this.queueService.sendMessage(queueMessage);
      this.logger.log(`Message queued for processing from user ${processedMessage.telegramUserId}`);
    } catch (error) {
      this.logger.error('Failed to queue message for processing', error);
      throw error;
    }
  }
}
