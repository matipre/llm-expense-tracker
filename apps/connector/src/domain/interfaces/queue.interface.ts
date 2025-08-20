export interface QueueMessage {
  id?: string;
  type: 'telegram_message' | 'bot_response';
  payload: any;
  timestamp: Date;
  retryCount?: number;
}

export interface IQueueService {
  sendMessage(message: QueueMessage): Promise<void>;
  consumeMessages(callback: (message: QueueMessage) => Promise<void>): Promise<void>;
  startConsumer(): Promise<void>;
  stopConsumer(): Promise<void>;
}
