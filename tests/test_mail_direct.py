"""Tests for Mail module using direct execution (no mocks)."""

import pytest
import pytest_asyncio
import asyncio
from utils.mail import MailModule

@pytest.mark.asyncio
async def test_mail_basic_functions(mail):
    """Test basic mail functions without sending actual emails."""
    # Test searching for emails (doesn't require sending)
    emails = await mail.search_mails("test")
    
    # Print the structure for debugging
    print("Search emails result structure:")
    print(f"Emails: {emails}")
    
    # Just verify we get a list back, content will depend on access
    assert isinstance(emails, list)
    
    # Test getting unread emails
    unread = await mail.get_unread_mails()
    
    # Print the structure for debugging
    print("Unread emails result structure:")
    print(f"Unread: {unread}")
    
    # Just verify we get a list back, content will depend on access
    assert isinstance(unread, list)