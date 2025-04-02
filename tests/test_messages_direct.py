"""Tests for Messages module using direct execution (no mocks)."""

import pytest
import pytest_asyncio
import asyncio
from utils.message import MessageModule

@pytest.mark.asyncio
async def test_messages_basic_structure(messages):
    """Test basic messages structure without sending actual messages."""
    # We'll use a placeholder phone number but not actually send
    # This just tests the API structure and access
    phone_number = "+11234567890"  # Placeholder, won't actually be used for sending
    
    # Test reading messages (doesn't actually send anything)
    result = await messages.read_messages(phone_number)
    
    # Print the structure for debugging
    print("Read messages result structure:")
    print(f"Result: {result}")
    
    # Just verify we get back a list
    assert isinstance(result, list)