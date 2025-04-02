"""Tests for Calendar module focusing on interface rather than implementation."""

import pytest
import pytest_asyncio
import asyncio
import unittest.mock as mock
from datetime import datetime, timedelta
from utils.calendar import CalendarModule

@pytest.fixture
def mock_calendar():
    """Create a mocked CalendarModule instance."""
    module = CalendarModule()
    
    # Mock the implementation methods but not check_access
    module.check_calendar_access = mock.AsyncMock(return_value=True)
    module.run_applescript_async = mock.AsyncMock(return_value="SUCCESS:Event created successfully")
    
    return module

@pytest.mark.asyncio
async def test_calendar_interface(mock_calendar):
    """Test Calendar module interface."""
    # Test creating an event
    test_title = f"Test Event {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    start_date = datetime.now() + timedelta(hours=1)
    end_date = start_date + timedelta(hours=1)
    
    # Mock the run_applescript_async method on the CalendarModule instance
    mock_calendar.run_applescript_async = mock.AsyncMock(return_value="SUCCESS:Event created successfully")
    
    # Call the create_event method
    result = await mock_calendar.create_event(
        title=test_title,
        start_date=start_date,
        end_date=end_date,
        location="Test Location",
        notes="This is a test event.",
        calendar_name="Work"
    )
    
    # Check the basic structure of the result
    assert isinstance(result, dict)
    assert "success" in result
    
    # Now test search_events with a mocked result
    mock_calendar.run_applescript_async = mock.AsyncMock(
        return_value='{title:"Test Event", start_date:"2025-04-01 14:00:00", end_date:"2025-04-01 15:00:00"}'
    )
    
    events = await mock_calendar.search_events("Test Event")
    assert isinstance(events, list)
    
    # Test get_events with a mocked result
    mock_calendar.run_applescript_async = mock.AsyncMock(
        return_value='{title:"Meeting 1", start_date:"2025-04-01 14:00:00"}, {title:"Meeting 2", start_date:"2025-04-01 16:00:00"}'
    )
    
    all_events = await mock_calendar.get_events()
    assert isinstance(all_events, list)