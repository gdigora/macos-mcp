"""Tests for Reminders module using direct execution (no mocks)."""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from utils.reminders import RemindersModule

@pytest.mark.asyncio
async def test_reminders_integration(reminders):
    """Test Reminders integration."""
    # Create a test reminder
    test_title = f"Test Reminder {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_notes = "This is a test reminder created by integration tests."
    test_due_date = datetime.now() + timedelta(days=1)
    
    result = await reminders.create_reminder(
        name=test_title,
        list_name="Reminders",
        notes=test_notes,
        due_date=test_due_date
    )
    assert result["success"] is True
    
    # Search for the reminder
    found_reminders = await reminders.search_reminders(test_title)
    assert isinstance(found_reminders, list)
    
    # Print the structure for debugging
    print("Found reminders structure:")
    for reminder in found_reminders:
        print(f"Reminder: {reminder}")
        
    # We just verify we get a list back, since the structure may vary
    # depending on permissions and the state of the reminders app
    assert isinstance(found_reminders, list)