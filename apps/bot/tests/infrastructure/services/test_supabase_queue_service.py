"""
Tests for SupabaseQueueService demonstrating dependency injection benefits.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from infrastructure.services.supabase_queue_service import SupabaseQueueService
from domain.entities.message import IncomingMessage, BotResponse


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    client = Mock()
    client.from_ = Mock()
    client.rpc = Mock()
    return client


@pytest.fixture
def queue_service(mock_supabase_client):
    """Create a SupabaseQueueService with mocked dependencies."""
    return SupabaseQueueService(mock_supabase_client)


@pytest.mark.asyncio
async def test_has_supabase_queues_returns_false_when_pgmq_not_available(queue_service, mock_supabase_client):
    """Test that hasSupabaseQueues returns False when pgmq extension is not available."""
    # Mock the response for checking pgmq extension
    mock_response = Mock()
    mock_response.data = None
    
    mock_supabase_client.from_.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
    
    result = await queue_service.has_supabase_queues()
    
    assert result is False


@pytest.mark.asyncio
async def test_has_supabase_queues_returns_true_when_pgmq_available(queue_service, mock_supabase_client):
    """Test that hasSupabaseQueues returns True when pgmq extension is available."""
    # Mock the response for checking pgmq extension
    mock_response = Mock()
    mock_response.data = {"extname": "pgmq"}
    
    mock_supabase_client.from_.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
    
    result = await queue_service.has_supabase_queues()
    
    assert result is True


@pytest.mark.asyncio
async def test_send_response_uses_table_queue_when_pgmq_not_available(queue_service, mock_supabase_client):
    """Test that sendResponse uses table-based queue when pgmq is not available."""
    response = BotResponse(
        chat_id=123456789,
        text="Test response",
        reply_to_message_id=456
    )
    
    # Mock hasSupabaseQueues to return False
    queue_service._has_pgmq = False
    
    # Mock table insert
    mock_insert_response = Mock()
    mock_insert_response.data = [{"id": 1}]
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_insert_response
    
    await queue_service.send_response(response)
    
    # Verify that table method was called
    mock_supabase_client.table.assert_called_with("message_queue")


@pytest.mark.asyncio
async def test_send_response_uses_supabase_queue_when_pgmq_available(queue_service, mock_supabase_client):
    """Test that sendResponse uses Supabase queue when pgmq is available."""
    response = BotResponse(
        chat_id=123456789,
        text="Test response",
        reply_to_message_id=456
    )
    
    # Mock hasSupabaseQueues to return True
    queue_service._has_pgmq = True
    
    # Mock rpc call
    mock_rpc_response = Mock()
    mock_rpc_response.data = {"msg_id": 123}
    mock_supabase_client.rpc.return_value.execute.return_value = mock_rpc_response
    
    await queue_service.send_response(response)
    
    # Verify that rpc method was called with correct parameters
    mock_supabase_client.rpc.assert_called_with('pgmq_send', {
        'queue_name': 'bot_responses',
        'msg': {
            "chatId": response.chat_id,
            "text": response.text,
            "replyToMessageId": response.reply_to_message_id
        }
    })


@pytest.mark.asyncio
async def test_consume_messages_handles_incoming_messages(queue_service, mock_supabase_client):
    """Test that consumeMessages properly processes incoming messages."""
    # Mock table-based queue response
    queue_service._has_pgmq = False
    
    mock_response = Mock()
    mock_response.data = [{
        "id": 1,
        "payload": {
            "telegramUserId": 123456789,
            "chatId": 123456789,
            "messageText": "Pizza 20 bucks",
            "timestamp": "2023-01-01T12:00:00",
            "messageId": 456
        }
    }]
    
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
    
    # Mock update operations
    mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
    
    # Mock callback
    callback = AsyncMock()
    
    await queue_service.consume_messages(callback)
    
    # Verify callback was called with correct message
    assert callback.call_count == 1
    message = callback.call_args[0][0]
    assert isinstance(message, IncomingMessage)
    assert message.telegram_user_id == 123456789
    assert message.message_text == "Pizza 20 bucks"
