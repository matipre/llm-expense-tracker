export interface TaskHandlerArgs {
  data: unknown;
}

export interface TaskHandlerResult {
  status: 'success' | 'error' | 'cancelled';
  resultMessage?: string;
}

export interface JobOptions {
  name: string;
  handler?: (args: TaskHandlerArgs) => Promise<TaskHandlerResult>;
  pollIntervalInMillis?: number;
  visibilityTimeoutInSeconds?: number;
}

export interface Job {
  scheduleTask(data: any): Promise<void>;
  turnOn(): Promise<void>;
  turnOff(): Promise<void>;
}

export interface JobFactory {
  createJob(options: JobOptions): Job;
}
