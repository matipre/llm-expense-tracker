import { TaskHandlerResult } from '../../domain/interfaces/job-factory.interface.js';

export function createSuccessResult(message?: string): TaskHandlerResult {
  return {
    status: 'success',
    resultMessage: message || 'Task completed successfully'
  };
}

export function createErrorResult(message: string): TaskHandlerResult {
  return {
    status: 'error',
    resultMessage: message
  };
}

export function createCancelledResult(message?: string): TaskHandlerResult {
  return {
    status: 'cancelled',
    resultMessage: message || 'Task was cancelled'
  };
}
