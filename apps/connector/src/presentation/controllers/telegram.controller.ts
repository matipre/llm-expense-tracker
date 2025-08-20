import { Body, Controller, Post, Logger, HttpCode, HttpStatus } from '@nestjs/common';
import { TelegramWebhookDto } from '../dtos/telegram-webhook.dto.js';
import { MessageProcessorService } from '../../application/services/message-processor.service.js';

@Controller('telegram')
export class TelegramController {
  private readonly logger = new Logger(TelegramController.name);

  constructor(private readonly messageProcessor: MessageProcessorService) {}

  @Post('webhook')
  @HttpCode(HttpStatus.OK)
  async handleWebhook(@Body() update: TelegramWebhookDto) {
    try {
      this.logger.log(`Received webhook update: ${update.update_id}`);
      
      if (update.message?.text) {
        this.logger.log(`Message from ${update.message.from?.first_name}: ${update.message.text}`);
      }
      
      await this.messageProcessor.processWebhookUpdate(update);
      
      return { ok: true };
    } catch (error) {
      this.logger.error('Error processing webhook', error.message, error.stack);
      throw error;
    }
  }
}
