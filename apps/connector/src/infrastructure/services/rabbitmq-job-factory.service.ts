import { Injectable, Logger, Inject, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as amqp from 'amqplib';

import { JobFactory, Job, JobOptions } from '../../domain/interfaces/job-factory.interface.js';
import { RABBITMQ_CONNECTION } from '../providers/rabbitmq.provider.js';
import type { ChannelModel } from 'amqplib';

interface RabbitMQMessage {
  msgId: string;
  data: any;
  attempts: number;
  maxRetries: number;
}

@Injectable()
export class RabbitMQJobFactory implements JobFactory, OnModuleDestroy {
  private readonly logger = new Logger(RabbitMQJobFactory.name);
  private readonly channels = new Map<string, amqp.Channel>();
  private readonly workers = new Map<string, boolean>();

  constructor(
    @Inject(RABBITMQ_CONNECTION) private readonly connection: ChannelModel,
    private readonly configService: ConfigService,
  ) {}

  async onModuleDestroy() {
    this.logger.log('Shutting down RabbitMQ channels and workers');
    
    // Stop all workers
    for (const [queueName] of this.workers) {
      this.workers.set(queueName, false);
    }

    // Close all channels
    for (const [queueName, channel] of this.channels) {
      try {
        await channel.close();
        this.logger.log(`Closed channel for queue: ${queueName}`);
      } catch (error) {
        this.logger.warn(`Error closing channel for queue ${queueName}:`, error);
      }
    }
    
    this.channels.clear();
    this.workers.clear();
  }

  createJob(options: JobOptions): Job {
    this.logger.log(`RabbitMQJobFactory - Creating job '${options.name}'`);

    const scheduleTask = async (data: any) => {
      try {
        const channel = await this.getChannel(options.name);
        const exchange = this.configService.get<string>('rabbitmq.exchange')!;
        const maxRetries = this.configService.get<number>('queue.maxRetries', 3);
        
        const message: RabbitMQMessage = {
          msgId: this.generateMessageId(),
          data,
          attempts: 0,
          maxRetries,
        };

        const published = channel.publish(
          exchange,
          options.name,
          Buffer.from(JSON.stringify(message)),
          { persistent: true }
        );

        if (!published) {
          throw new Error('Failed to publish message to RabbitMQ');
        }

        this.logger.log(`RabbitMQJobFactory - Scheduled task for job '${options.name}'`);
      } catch (error) {
        this.logger.error(`Failed to send message to queue ${options.name}`, error);
        throw error;
      }
    };

    return {
      scheduleTask,
      turnOn: async () => {
        this.logger.log(`RabbitMQJobFactory - Turning on worker for job '${options.name}'`);
        await this.createWorker(options);
      },
      turnOff: async () => {
        this.logger.log(`RabbitMQJobFactory - Turning off worker for job '${options.name}'`);
        this.workers.set(options.name, false);
      },
    };
  }

  private async createWorker(options: JobOptions): Promise<void> {
    if (!options.handler) {
      this.logger.log(`RabbitMQJobFactory - No handler for job '${options.name}'`);
      return;
    }

    this.logger.log(`RabbitMQJobFactory - Starting worker for job '${options.name}'. QueueName: ${options.name}`);
    
    const channel = await this.getChannel(options.name);
    const prefetchCount = this.configService.get<number>('queue.prefetchCount', 10);
    
    // Set QoS to control how many messages are delivered to this consumer
    await channel.prefetch(prefetchCount);
    
    // Set this worker as active
    this.workers.set(options.name, true);

    // Start consuming messages
    await channel.consume(
      options.name,
      async (msg) => {
        if (!msg || !this.workers.get(options.name)) {
          return;
        }

        try {
          const messageContent: RabbitMQMessage = JSON.parse(msg.content.toString());
          this.logger.debug(`RabbitMQJobFactory - Processing job '${options.name}' with id ${messageContent.msgId}`);

          const result = await options.handler!({ data: messageContent.data });

          // Handle result based on status
          if (result.status === 'error') {
            this.logger.error(`RabbitMQJobFactory - Job failed '${options.name}' with id ${messageContent.msgId}: ${result.resultMessage}`);
            await this.handleFailedMessage(channel, msg, messageContent, options.name);
          } else if (result.status === 'cancelled') {
            this.logger.log(`RabbitMQJobFactory - Job cancelled '${options.name}' with id ${messageContent.msgId}`);
            channel.ack(msg);
          } else {
            // Success
            channel.ack(msg);
            this.logger.log(`RabbitMQJobFactory - Job completed '${options.name}' with id ${messageContent.msgId}`);
          }

        } catch (error: any) {
          this.logger.error(`RabbitMQJobFactory - Error processing job '${options.name}'`, error);
          
          try {
            const messageContent: RabbitMQMessage = JSON.parse(msg.content.toString());
            await this.handleFailedMessage(channel, msg, messageContent, options.name);
          } catch (parseError) {
            // If we can't parse the message, just reject it
            channel.nack(msg, false, false);
          }
        }
      },
      { noAck: false }
    );

    this.logger.log(`RabbitMQJobFactory - Worker started for queue: ${options.name}`);
  }

  private async handleFailedMessage(
    channel: amqp.Channel,
    msg: amqp.ConsumeMessage,
    messageContent: RabbitMQMessage,
    queueName: string
  ): Promise<void> {
    messageContent.attempts += 1;

    if (messageContent.attempts >= messageContent.maxRetries) {
      // Send to dead letter queue
      const dlxExchange = this.configService.get<string>('rabbitmq.dlxExchange')!;
      const dlqName = `${queueName}.dlq`;
      
      channel.publish(
        dlxExchange,
        dlqName,
        Buffer.from(JSON.stringify(messageContent)),
        { persistent: true }
      );
      
      this.logger.warn(`Message sent to DLQ after ${messageContent.attempts} attempts: ${messageContent.msgId}`);
      channel.ack(msg);
    } else {
      // Retry: republish the message with updated attempt count
      const exchange = this.configService.get<string>('rabbitmq.exchange')!;
      
      // Add delay before retry (exponential backoff)
      const delay = Math.min(1000 * Math.pow(2, messageContent.attempts - 1), 30000);
      
      setTimeout(() => {
        channel.publish(
          exchange,
          queueName,
          Buffer.from(JSON.stringify(messageContent)),
          { persistent: true }
        );
      }, delay);
      
      channel.ack(msg);
      this.logger.log(`Message will be retried in ${delay}ms (attempt ${messageContent.attempts}/${messageContent.maxRetries}): ${messageContent.msgId}`);
    }
  }

  private async getChannel(queueName: string): Promise<amqp.Channel> {
    if (this.channels.has(queueName)) {
      return this.channels.get(queueName)!;
    }

    const channel = await this.connection.createChannel();
    const exchange = this.configService.get<string>('rabbitmq.exchange')!;
    const dlxExchange = this.configService.get<string>('rabbitmq.dlxExchange')!;

    // Declare exchanges
    await channel.assertExchange(exchange, 'direct', { durable: true });
    await channel.assertExchange(dlxExchange, 'direct', { durable: true });

    // Declare main queue
    await channel.assertQueue(queueName, { 
      durable: true,
      deadLetterExchange: dlxExchange,
      deadLetterRoutingKey: `${queueName}.dlq`
    });

    // Declare dead letter queue
    const dlqName = `${queueName}.dlq`;
    await channel.assertQueue(dlqName, { durable: true });

    // Bind queues to exchanges
    await channel.bindQueue(queueName, exchange, queueName);
    await channel.bindQueue(dlqName, dlxExchange, dlqName);

    this.channels.set(queueName, channel);
    this.logger.log(`Created and configured channel for queue: ${queueName}`);

    return channel;
  }

  private generateMessageId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
