import { Injectable, Logger, Inject } from '@nestjs/common';
import type { SupabaseClient } from '@supabase/supabase-js';
import { JobFactory, Job, JobOptions } from '../../domain/interfaces/job-factory.interface.js';
import { SUPABASE_CLIENT } from '../providers/supabase.provider.js';

@Injectable()
export class SupabaseJobFactory implements JobFactory {
  private readonly logger = new Logger(SupabaseJobFactory.name);

  private readonly DEFAULT_POLL_INTERVAL_IN_MILLIS = 1000;
  private readonly DEFAULT_VISIBILITY_TIMEOUT_IN_SECONDS = 5;

  constructor(@Inject(SUPABASE_CLIENT) private readonly supabase: SupabaseClient) {}

  createJob(options: JobOptions): Job {
    this.logger.log(`SupabaseJobFactory - Creating job '${options.name}'`);

    // Set default values for new options
    const visibilityTimeoutInSeconds = options.visibilityTimeoutInSeconds ?? this.DEFAULT_VISIBILITY_TIMEOUT_IN_SECONDS;

    let workerInterval: any;

    const scheduleTask = async (data: any) => {
      const { error } = await this.supabase
        .schema('pgmq_public')
        .rpc('send', {
          queue_name: options.name,
          message: { data },
          sleep_seconds: visibilityTimeoutInSeconds
        });

      if (error) {
        this.logger.error(`Failed to send message to queue ${options.name}`, error);
        throw error;
      }

      this.logger.log(`SupabaseJobFactory - Scheduled task for job '${options.name}'`);
    };

    return {
      scheduleTask,
      turnOn: async () => {
        this.logger.log(`SupabaseJobFactory - Turning on worker for job '${options.name}'`);
        workerInterval = await this.createWorker(options);
      },
      turnOff: async () => {
        this.logger.log(`SupabaseJobFactory - Turning off worker for job '${options.name}'`);
        if (workerInterval) {
          clearInterval(workerInterval);
          workerInterval = null;
        }
      },
    };
  }

  private async createWorker(options: JobOptions): Promise<any> {
    this.logger.log(`SupabaseJobFactory - Starting worker for job '${options.name}'. QueueName: ${options.name}`);

    // Set default values for new options
    const pollIntervalInMillis = options.pollIntervalInMillis ?? this.DEFAULT_POLL_INTERVAL_IN_MILLIS;
    const visibilityTimeoutInSeconds = options.visibilityTimeoutInSeconds ?? this.DEFAULT_VISIBILITY_TIMEOUT_IN_SECONDS;

    if(!options.handler) {
        this.logger.log(`SupabaseJobFactory - No handler for job '${options.name}'`);
        return;
    }

    // Poll based on configured interval
    const interval = setInterval(async () => {
      try {
        const { data: messages, error } = await this.supabase
          .schema('pgmq_public')
          .rpc('read', {
            n: 10, // quantity of messages to read
            queue_name: options.name,
            sleep_seconds: visibilityTimeoutInSeconds
          });

        if (error) {
          this.logger.error(`Error reading from queue ${options.name}`, error);
          return;
        }

        for (const msg of messages || []) {
          this.logger.debug(`SupabaseJobFactory - Processing job '${options.name}' with id ${msg.msg_id}`);
          try {
            const result = await options.handler({ data: (msg.message as any).data });

            // Handle result based on status
            if (result.status === 'error') {
              this.logger.error(`SupabaseJobFactory - Job failed '${options.name}' with id ${msg.msg_id}: ${result.resultMessage}`);
              // For Supabase, we can archive failed messages or just delete them
              await this.supabase.schema('pgmq_public').rpc('archive', {
                queue_name: options.name,
                message_id: msg.msg_id
              });
            } else if (result.status === 'cancelled') {
              this.logger.log(`SupabaseJobFactory - Job cancelled '${options.name}' with id ${msg.msg_id}`);
              await this.supabase.schema('pgmq_public').rpc('delete', {
                queue_name: options.name,
                message_id: msg.msg_id
              });
            } else {
              // Success
              await this.supabase.schema('pgmq_public').rpc('delete', {
                queue_name: options.name,
                message_id: msg.msg_id
              });
              this.logger.log(`SupabaseJobFactory - Job completed '${options.name}' with id ${msg.msg_id}`);
            }

          } catch (error: any) {
            this.logger.error(`SupabaseJobFactory - Error processing job '${options.name}' with id ${msg.msg_id}`, error);
            // Archive failed messages
            await this.supabase.schema('pgmq_public').rpc('archive', {
              queue_name: options.name,
              message_id: msg.msg_id
            });
          }
        }
      } catch (error) {
        this.logger.error(`SupabaseJobFactory - Error in worker for queue ${options.name}:`, error);
      }
    }, pollIntervalInMillis);

    return interval;
  }
}
