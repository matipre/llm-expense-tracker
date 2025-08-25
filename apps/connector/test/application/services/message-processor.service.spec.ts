import { Test, TestingModule } from '@nestjs/testing';
import { MessageProcessorService } from '../../../src/application/services/message-processor.service.js';
import { TelegramMessageProcessingJob } from '../../../src/application/jobs/telegram-message-processing.job.js';
import { TelegramUpdate } from '../../../src/domain/entities/telegram-message.entity.js';

describe('MessageProcessorService', () => {
  let service: MessageProcessorService;
  let telegramJob: jest.Mocked<TelegramMessageProcessingJob>;

  beforeEach(async () => {
    const mockTelegramJob = {
      scheduleMessageProcessing: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        MessageProcessorService,
        {
          provide: TelegramMessageProcessingJob,
          useValue: mockTelegramJob,
        },
      ],
    }).compile();

    service = module.get<MessageProcessorService>(MessageProcessorService);
    telegramJob = module.get(TelegramMessageProcessingJob);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('processWebhookUpdate', () => {
    const baseUpdate: TelegramUpdate = {
      update_id: 123456,
      message: {
        message_id: 789,
        from: {
          id: 123,
          is_bot: false,
          first_name: 'John',
          username: 'john_doe'
        },
        chat: {
          id: 456,
          type: 'private',
          first_name: 'John',
          username: 'john_doe'
        },
        date: 1640995200, // Jan 1, 2022, 00:00:00 UTC
        text: 'Test message'
      }
    };

    it('should process a valid private chat message successfully', async () => {
      telegramJob.scheduleMessageProcessing.mockResolvedValue(undefined);

      await service.processWebhookUpdate(baseUpdate);

      expect(telegramJob.scheduleMessageProcessing).toHaveBeenCalledWith(
        456, // chatId
        'Test message', // messageText
        123, // telegramUserId
        '2022-01-01T00:00:00.000Z', // timestamp
        789 // messageId
      );
    });

    it('should handle updates without message', async () => {
      const updateWithoutMessage: TelegramUpdate = {
        update_id: 123456
      };

      await service.processWebhookUpdate(updateWithoutMessage);

      expect(telegramJob.scheduleMessageProcessing).not.toHaveBeenCalled();
    });

    it('should handle messages without text', async () => {
      const updateWithoutText: TelegramUpdate = {
        ...baseUpdate,
        message: {
          ...baseUpdate.message!,
          text: undefined
        }
      };

      await service.processWebhookUpdate(updateWithoutText);

      expect(telegramJob.scheduleMessageProcessing).not.toHaveBeenCalled();
    });

    it('should ignore non-private chat messages', async () => {
      const groupChatUpdate: TelegramUpdate = {
        ...baseUpdate,
        message: {
          ...baseUpdate.message!,
          chat: {
            ...baseUpdate.message!.chat,
            type: 'group'
          }
        }
      };

      await service.processWebhookUpdate(groupChatUpdate);

      expect(telegramJob.scheduleMessageProcessing).not.toHaveBeenCalled();
    });

    it('should handle messages without from field', async () => {
      const updateWithoutFrom: TelegramUpdate = {
        ...baseUpdate,
        message: {
          ...baseUpdate.message!,
          from: undefined
        }
      };

      telegramJob.scheduleMessageProcessing.mockResolvedValue(undefined);

      await service.processWebhookUpdate(updateWithoutFrom);

      expect(telegramJob.scheduleMessageProcessing).toHaveBeenCalledWith(
        456, // chatId
        'Test message', // messageText
        0, // telegramUserId (default when from is undefined)
        '2022-01-01T00:00:00.000Z', // timestamp
        789 // messageId
      );
    });

    it('should handle job scheduling failures', async () => {
      const error = new Error('Failed to schedule job');
      telegramJob.scheduleMessageProcessing.mockRejectedValue(error);

      await expect(service.processWebhookUpdate(baseUpdate)).rejects.toThrow('Failed to schedule job');

      expect(telegramJob.scheduleMessageProcessing).toHaveBeenCalled();
    });

    it('should handle different chat types correctly', async () => {
      const chatTypes = ['group', 'supergroup', 'channel'] as const;
      
      for (const chatType of chatTypes) {
        const updateWithChatType: TelegramUpdate = {
          ...baseUpdate,
          message: {
            ...baseUpdate.message!,
            chat: {
              ...baseUpdate.message!.chat,
              type: chatType
            }
          }
        };

        await service.processWebhookUpdate(updateWithChatType);
        
        expect(telegramJob.scheduleMessageProcessing).not.toHaveBeenCalled();
      }
    });

    it('should convert timestamp correctly', async () => {
      const specificTimestamp = 1672531200; // Jan 1, 2023, 00:00:00 UTC
      const updateWithTimestamp: TelegramUpdate = {
        ...baseUpdate,
        message: {
          ...baseUpdate.message!,
          date: specificTimestamp
        }
      };

      telegramJob.scheduleMessageProcessing.mockResolvedValue(undefined);

      await service.processWebhookUpdate(updateWithTimestamp);

      expect(telegramJob.scheduleMessageProcessing).toHaveBeenCalledWith(
        456, // chatId
        'Test message', // messageText
        123, // telegramUserId
        '2023-01-01T00:00:00.000Z', // converted timestamp
        789 // messageId
      );
    });
  });
});
