import { Injectable, Logger, Inject, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { MessageProcessorService } from '../../application/services/message-processor.service.js';
import { TELEGRAM_HTTP_CLIENT } from '../providers/telegram-http-client.provider.js';
import type { HttpClient } from '../../utils/httpClient.js';

interface TelegramApiResponse {
    ok: boolean;
    result?: any;
    description?: string;
}

@Injectable()
export class TelegramPollingService implements OnModuleInit, OnModuleDestroy {
    private readonly logger = new Logger(TelegramPollingService.name);
    private lastUpdateId = 0;
    private isPolling = false;
    private pollingTimeout: NodeJS.Timeout | null = null;

    private readonly pollingIntervalInMillis: number = 500;
    private readonly errorPollingIntervalInMillis: number = 2000
    
    constructor(
        private configService: ConfigService,
        @Inject(TELEGRAM_HTTP_CLIENT) private httpClient: HttpClient,
        private messageProcessor: MessageProcessorService,
    ) {
    }

    async onModuleInit() {
        // Only start polling in development
        if (this.configService.get<string>('environment') === 'development') {
            await this.startPolling();
        }
    }

    async onModuleDestroy() {
        await this.stopPolling();
    }

    async startPolling() {
        if (this.isPolling) {
            return;
        }

        this.logger.log('🔄 Starting Telegram polling...');
        this.isPolling = true;

        this.startPollingLoop();

        this.logger.log('✅ Telegram polling started');
    }

    async stopPolling() {
        if (!this.isPolling) {
            return;
        }

        this.logger.log('⏹️ Stopping Telegram polling...');
        this.isPolling = false;

        if (this.pollingTimeout) {
            clearTimeout(this.pollingTimeout);
            this.pollingTimeout = null;
        }

        this.logger.log('✅ Telegram polling stopped');
    }

    private startPollingLoop() {
        if (!this.isPolling) {
            return;
        }

        this.pollForUpdates()
            .then(() => {
                // Schedule the next poll after this one completes
                if (this.isPolling) {
                    this.pollingTimeout = setTimeout(() => {
                        this.startPollingLoop();
                    }, this.pollingIntervalInMillis); // Wait 1 second between polls
                }
            })
            .catch((error) => {
                this.logger.error('Error during polling:', error);
                // Even on error, continue polling after a delay
                if (this.isPolling) {
                    this.pollingTimeout = setTimeout(() => {
                        this.startPollingLoop();
                    }, this.errorPollingIntervalInMillis); // Wait 2 seconds on error before retrying
                }
            });
    }

    private async pollForUpdates() {
        try {
            const response = await this.httpClient.get('/getUpdates', {
                params: {
                    offset: this.lastUpdateId + 1
                }
            });

            const data = response.data as TelegramApiResponse;

            if (!data.ok) {
                this.logger.error('Telegram API returned error:', data);
                return;
            }

            const updates = data.result || [];

            for (const update of updates) {
                try {
                    // Update the last update ID
                    this.lastUpdateId = Math.max(this.lastUpdateId, update.update_id);

                    // Process the update using the same logic as webhook
                    await this.messageProcessor.processWebhookUpdate(update);

                    this.logger.debug(`Processed update ${update.update_id}`);
                } catch (error) {
                    this.logger.error(`Error processing update ${update.update_id}:`, error);
                }
            }

            if (updates.length > 0) {
                this.logger.log(`📨 Processed ${updates.length} updates`);
            }

        } catch (error) {
            this.logger.error({ error: error.message }, 'Error polling for updates:');
        }
    }
}
