import { Test, TestingModule } from '@nestjs/testing';
import { TelegramPollingService } from '../../../src/infrastructure/services/telegram-polling.service.js';
import { MessageProcessorService } from '../../../src/application/services/message-processor.service.js';
import { IS_POLLING_ENABLED } from '../../../src/infrastructure/constants/injection-tokens.js';
import { TELEGRAM_HTTP_CLIENT } from '../../../src/infrastructure/providers/telegram-http-client.provider.js';
import { TelegramUpdate } from '../../../src/domain/entities/telegram-message.entity.js';

describe('TelegramPollingService', () => {
  let service: TelegramPollingService;
  let httpClient: jest.Mocked<any>;
  let messageProcessor: jest.Mocked<MessageProcessorService>;

  beforeEach(async () => {
    const mockHttpClient = {
      get: jest.fn(),
    };

    const mockMessageProcessor = {
      processWebhookUpdate: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TelegramPollingService,
        {
          provide: IS_POLLING_ENABLED,
          useValue: true,
        },
        {
          provide: TELEGRAM_HTTP_CLIENT,
          useValue: mockHttpClient,
        },
        {
          provide: MessageProcessorService,
          useValue: mockMessageProcessor,
        },
      ],
    }).compile();

    service = module.get<TelegramPollingService>(TelegramPollingService);
    httpClient = module.get(TELEGRAM_HTTP_CLIENT);
    messageProcessor = module.get(MessageProcessorService);
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
  });

  describe('lifecycle hooks', () => {
    it('should start polling on module init when polling is enabled', async () => {
      const startPollingSpy = jest.spyOn(service, 'startPolling').mockResolvedValue();

      await service.onModuleInit();

      expect(startPollingSpy).toHaveBeenCalled();
    });

    it('should stop polling on module destroy', async () => {
      const stopPollingSpy = jest.spyOn(service, 'stopPolling').mockResolvedValue();

      await service.onModuleDestroy();

      expect(stopPollingSpy).toHaveBeenCalled();
    });
  });

  describe('polling control', () => {
    it('should not start polling twice', async () => {
      const mockGetUpdates = jest.fn().mockResolvedValue({
        data: { ok: true, result: [] }
      });
      httpClient.get.mockImplementation(mockGetUpdates);

      await service.startPolling();
      await service.startPolling(); // Second call should be ignored

      expect(service['isPolling']).toBe(true);
    });

    it('should stop polling when requested', async () => {
      const mockGetUpdates = jest.fn().mockResolvedValue({
        data: { ok: true, result: [] }
      });
      httpClient.get.mockImplementation(mockGetUpdates);

      await service.startPolling();
      expect(service['isPolling']).toBe(true);

      await service.stopPolling();
      expect(service['isPolling']).toBe(false);
    });

    it('should not stop polling twice', async () => {
      await service.stopPolling();
      await service.stopPolling(); // Second call should be handled gracefully

      expect(service['isPolling']).toBe(false);
    });
  });

  describe('update processing', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should process updates from Telegram API', async () => {
      const mockUpdate: TelegramUpdate = {
        update_id: 123,
        message: {
          message_id: 456,
          chat: { id: 789, type: 'private' },
          date: 1640995200,
          text: 'Hello',
        },
      };

      httpClient.get.mockResolvedValue({
        data: {
          ok: true,
          result: [mockUpdate],
        },
      });

      messageProcessor.processWebhookUpdate.mockResolvedValue();

      await service['pollForUpdates']();

      expect(httpClient.get).toHaveBeenCalledWith('/getUpdates', {
        params: { offset: 1 },
      });
      expect(messageProcessor.processWebhookUpdate).toHaveBeenCalledWith(mockUpdate);
      expect(service['lastUpdateId']).toBe(123);
    });

    it('should handle empty updates response', async () => {
      httpClient.get.mockResolvedValue({
        data: {
          ok: true,
          result: [],
        },
      });

      await service['pollForUpdates']();

      expect(httpClient.get).toHaveBeenCalled();
      expect(messageProcessor.processWebhookUpdate).not.toHaveBeenCalled();
    });

    it('should handle API error response', async () => {
      httpClient.get.mockResolvedValue({
        data: {
          ok: false,
          description: 'API Error',
        },
      });

      await service['pollForUpdates']();

      expect(httpClient.get).toHaveBeenCalled();
      expect(messageProcessor.processWebhookUpdate).not.toHaveBeenCalled();
    });

    it('should handle HTTP request errors', async () => {
      const error = new Error('Network error');
      httpClient.get.mockRejectedValue(error);

      await expect(service['pollForUpdates']()).resolves.not.toThrow();
      expect(messageProcessor.processWebhookUpdate).not.toHaveBeenCalled();
    });

    it('should continue processing other updates if one fails', async () => {
      const update1: TelegramUpdate = { update_id: 1 };
      const update2: TelegramUpdate = { update_id: 2 };

      httpClient.get.mockResolvedValue({
        data: {
          ok: true,
          result: [update1, update2],
        },
      });

      messageProcessor.processWebhookUpdate
        .mockRejectedValueOnce(new Error('Processing error'))
        .mockResolvedValueOnce();

      await service['pollForUpdates']();

      expect(messageProcessor.processWebhookUpdate).toHaveBeenCalledTimes(2);
      expect(service['lastUpdateId']).toBe(2);
    });

    it('should update lastUpdateId to the highest update ID', async () => {
      const updates = [
        { update_id: 100 },
        { update_id: 105 },
        { update_id: 102 },
      ];

      httpClient.get.mockResolvedValue({
        data: {
          ok: true,
          result: updates,
        },
      });

      messageProcessor.processWebhookUpdate.mockResolvedValue();

      await service['pollForUpdates']();

      expect(service['lastUpdateId']).toBe(105);
    });
  });
});

// Test with polling disabled
describe('TelegramPollingService - Polling Disabled', () => {
  let service: TelegramPollingService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TelegramPollingService,
        {
          provide: IS_POLLING_ENABLED,
          useValue: false, // Polling disabled
        },
        {
          provide: TELEGRAM_HTTP_CLIENT,
          useValue: { get: jest.fn() },
        },
        {
          provide: MessageProcessorService,
          useValue: { processWebhookUpdate: jest.fn() },
        },
      ],
    }).compile();

    service = module.get<TelegramPollingService>(TelegramPollingService);
  });

  it('should not start polling on module init when polling is disabled', async () => {
    const startPollingSpy = jest.spyOn(service, 'startPolling').mockResolvedValue();

    await service.onModuleInit();

    expect(startPollingSpy).not.toHaveBeenCalled();
  });
});
