import { Inject, Injectable, Logger } from '@nestjs/common';
import { ITelegramService } from '../../domain/interfaces/telegram.interface.js';
import { TELEGRAM_HTTP_CLIENT } from '../providers/telegram-http-client.provider.js';
import type { HttpClient } from '../../utils/httpClient.js';

@Injectable()
export class TelegramService implements ITelegramService {
  private readonly logger = new Logger(TelegramService.name);

  constructor(
    @Inject(TELEGRAM_HTTP_CLIENT) private httpClient: HttpClient,
  ) {}

  async sendMessage(chatId: number, text: string): Promise<void> {
    try {
      await this.httpClient.post('/sendMessage', {
        chat_id: chatId,
        text: text,
      });

      this.logger.log(`Message sent to chat ${chatId}`);
    } catch (error) {
      this.logger.error('Error sending Telegram message', error);
      throw error;
    }
  }

  async setWebhook(url: string): Promise<void> {
    try {
      await this.httpClient.post('/setWebhook', {
        url: url,
      });

      this.logger.log(`Webhook set to: ${url}`);
    } catch (error) {
      this.logger.error('Error setting webhook', error);
      throw error;
    }
  }

  async deleteWebhook(): Promise<void> {
    try {
      await this.httpClient.post('/deleteWebhook');

      this.logger.log('Webhook deleted');
    } catch (error) {
      this.logger.error('Error deleting webhook', error);
      throw error;
    }
  }
}
