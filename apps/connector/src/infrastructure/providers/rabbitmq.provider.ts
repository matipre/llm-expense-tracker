import { Provider, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as amqp from 'amqplib';
import { ChannelModel } from 'amqplib';


export const RABBITMQ_CONNECTION = 'RABBITMQ_CONNECTION';

export const rabbitmqProvider: Provider = {
  provide: RABBITMQ_CONNECTION,
  useFactory: async (configService: ConfigService): Promise<ChannelModel> => {
    const logger = new Logger('RabbitMQProvider');
    
    const rabbitmqUrl = configService.get<string>('rabbitmq.url');
    const maxRetries = configService.get<number>('rabbitmq.connectionRetries') || 5;
    const retryDelay = configService.get<number>('rabbitmq.connectionRetryDelay') || 5000;
    
    if (!rabbitmqUrl) {
      throw new Error('RabbitMQ configuration missing: RABBITMQ_URL required');
    }

    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        logger.log(`Attempting to connect to RabbitMQ (attempt ${attempt}/${maxRetries})`);
        const connection = await amqp.connect(rabbitmqUrl);
        
        connection.on('error', (error) => {
          logger.error('RabbitMQ connection error:', error);
        });
        
        connection.on('close', () => {
          logger.warn('RabbitMQ connection closed');
        });
        
        logger.log('Successfully connected to RabbitMQ');
        return connection;
      } catch (error: any) {
        lastError = error;
        logger.warn(`Failed to connect to RabbitMQ (attempt ${attempt}/${maxRetries}):`, error.message);
        
        if (attempt < maxRetries) {
          logger.log(`Retrying in ${retryDelay}ms...`);
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
      }
    }
    
    logger.error('Failed to connect to RabbitMQ after all retries');
    throw lastError || new Error('Failed to connect to RabbitMQ');
  },
  inject: [ConfigService],
};
