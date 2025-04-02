"""Tests for Contacts module using direct execution (no mocks)."""

import pytest
import pytest_asyncio
import asyncio
from utils.contacts import ContactsModule

@pytest.mark.asyncio
async def test_contacts_integration(contacts):
    """Test Contacts integration."""
    # Get all contacts
    all_contacts = await contacts.get_all_numbers()
    assert isinstance(all_contacts, dict)
    
    # Search for a specific contact
    # Use a generic name that might exist
    search_results = await contacts.find_number("John")
    assert isinstance(search_results, list)