export interface ITelegramService {
  sendMessage(chatId: number, text: string): Promise<void>;
  setWebhook(url: string): Promise<void>;
  deleteWebhook(): Promise<void>;
}
