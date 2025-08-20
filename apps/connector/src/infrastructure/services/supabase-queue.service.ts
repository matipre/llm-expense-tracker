import { Injectable, Logger, Inject, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import type { SupabaseClient } from '@supabase/supabase-js';
import { IQueueService, QueueMessage } from '../../domain/interfaces/queue.interface.js';
import { SUPABASE_CLIENT } from '../providers/supabase.provider.js';

@Injectable()
export class SupabaseQueueService implements IQueueService, OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(SupabaseQueueService.name);
  private isConsuming = false;
  private consumerInterval?: NodeJS.Timeout;

  constructor(@Inject(SUPABASE_CLIENT) private readonly supabase: SupabaseClient) {
    this.logger.log('Supabase queue service initialized with injected client');
  }

  async onModuleInit() {
    await this.startConsumer();
  }

  async onModuleDestroy() {
    await this.stopConsumer();
  }

  async sendMessage(message: QueueMessage): Promise<void> {
    try {
      await this.sendToSupabaseQueue(message);

      this.logger.log(`Message sent to queue: ${message.type}`);
    } catch (error) {
      this.logger.error('Error sending message to queue', error);
      throw error;
    }
  }

  private async sendToSupabaseQueue(message: QueueMessage): Promise<void> {
    // Use Supabase Queue API when available
    const queueName = message.type === 'telegram_message' ? 'telegram_received_messages' : 'telegram_bot_responses';

    const { error } = await this.supabase
      .schema('pgmq_public')
      .rpc('send', {
        queue_name: queueName,
        message: message.payload,
        sleep_seconds: 30
      });

    if (error) {
      this.logger.error('Failed to send message to Supabase queue', error);
      throw error;
    }
  }

  async consumeMessages(callback: (message: QueueMessage) => Promise<void>): Promise<void> {
    try {
      await this.consumeFromSupabaseQueue(callback);
    } catch (error) {
      this.logger.error('Error consuming messages:', error);
    }
  }

  private async consumeFromSupabaseQueue(callback: (message: QueueMessage) => Promise<void>): Promise<void> {
    try {
      // Read from telegram_bot_responses queue
      const { data: messages, error } = await this.supabase
        .schema('pgmq_public')
        .rpc('read', {
          n: 10, // quantity of messages to read
          queue_name: 'telegram_bot_responses',
          sleep_seconds: 30 // visibility timeout in seconds
        });

      if (error) {
        this.logger.error('Error reading from Supabase queue', error);
        return;
      }

      for (const msg of messages || []) {
        try {
          const message: QueueMessage = {
            id: msg.msg_id.toString(),
            type: 'bot_response',
            payload: msg.message,
            timestamp: new Date(msg.enqueued_at),
            retryCount: msg.read_ct || 0
          };

          await callback(message);

          // Delete message after successful processing
          await this.supabase.schema('pgmq_public').rpc('delete', {
            queue_name: 'telegram_bot_responses',
            message_id: msg.msg_id
          });

          this.logger.log(`Processed and deleted message ${msg.msg_id}`);

        } catch (error) {
          this.logger.error(`Error processing message ${msg.msg_id}:`, error);
        }
      }
    } catch (error) {
      this.logger.error('Error in consumeFromSupabaseQueue:', error);
    }
  }

  async startConsumer(): Promise<void> {
    if (this.isConsuming) {
      return;
    }

    this.isConsuming = true;
    this.logger.log('Starting Supabase queue consumer');

    // Poll every 5 seconds for bot responses
    this.consumerInterval = setInterval(async () => {
      if (this.isConsuming) {
        await this.consumeMessages(async (message) => {
          // This will be handled by the telegram service to send responses
          this.logger.log(`Received bot response for chat ${message.payload.chatId}: ${message.payload.text}`);
        });
      }
    }, 5000);
  }

  async stopConsumer(): Promise<void> {
    this.isConsuming = false;

    if (this.consumerInterval) {
      clearInterval(this.consumerInterval);
      this.consumerInterval = undefined;
    }

    this.logger.log('Stopped Supabase queue consumer');
  }
}
