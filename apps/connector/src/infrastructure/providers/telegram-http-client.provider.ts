import { Provider } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';
import type { AppConfig } from '../../config/configuration.js';

export const TELEGRAM_HTTP_CLIENT = 'TELEGRAM_HTTP_CLIENT';

export const telegramHttpClientProvider: Provider = {
  provide: TELEGRAM_HTTP_CLIENT,
  useFactory: (configService: ConfigService<AppConfig>) => {
    const botToken = configService.get('telegram.botToken', { infer: true });

    if (!botToken) {
      throw new Error('TELEGRAM_BOT_TOKEN is required for HTTP client configuration');
    }

    const baseURL = `https://api.telegram.org/bot${botToken}`;

    const httpClient = axios.create({
      baseURL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    httpClient.interceptors.request.use(
      (config) => {
        // Log the request (without showing the full token)
        const maskedUrl = config.url?.includes('/bot') 
          ? config.url.replace(/\/bot\d+:[^/]+\//, '/bot***masked***/') 
          : config.url;
        console.log(`📤 Telegram API Request: ${config.method?.toUpperCase()} ${maskedUrl}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for logging
    httpClient.interceptors.response.use(
      (response) => {
        console.log(`📥 Telegram API Response: ${response.status} - ${response.config.url}`);
        return response;
      },
      (error) => {
        const status = error.response?.status;
        const url = error.config?.url;
        console.log(`❌ Telegram API Error: ${status} - ${url}`, error.response?.data);
        return Promise.reject(error);
      }
    );

    return httpClient;
  },
  inject: [ConfigService],
};
