import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { ITelegramService } from '../../domain/interfaces/telegram.interface.js';

@Injectable()
export class TelegramService implements ITelegramService {
  private readonly logger = new Logger(TelegramService.name);
  private readonly botToken: string;
  private readonly baseUrl: string;

  constructor(private configService: ConfigService) {
    this.botToken = this.configService.get<string>('telegram.botToken');
    
    if (!this.botToken) {
      throw new Error('Telegram bot token is required');
    }
    
    this.baseUrl = `https://api.telegram.org/bot${this.botToken}`;
  }

  async sendMessage(chatId: number, text: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/sendMessage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_id: chatId,
          text: text,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        this.logger.error(`Failed to send message: ${error}`);
        throw new Error(`Telegram API error: ${response.status}`);
      }

      this.logger.log(`Message sent to chat ${chatId}`);
    } catch (error) {
      this.logger.error('Error sending Telegram message', error);
      throw error;
    }
  }

  async setWebhook(url: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/setWebhook`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        this.logger.error(`Failed to set webhook: ${error}`);
        throw new Error(`Telegram API error: ${response.status}`);
      }

      this.logger.log(`Webhook set to: ${url}`);
    } catch (error) {
      this.logger.error('Error setting webhook', error);
      throw error;
    }
  }

  async deleteWebhook(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/deleteWebhook`, {
        method: 'POST',
      });

      if (!response.ok) {
        const error = await response.text();
        this.logger.error(`Failed to delete webhook: ${error}`);
        throw new Error(`Telegram API error: ${response.status}`);
      }

      this.logger.log('Webhook deleted');
    } catch (error) {
      this.logger.error('Error deleting webhook', error);
      throw error;
    }
  }
}
