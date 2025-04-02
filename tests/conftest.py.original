"""Common test fixtures and settings for Apple MCP tests."""

import pytest
import pytest_asyncio
import asyncio
import sys
from utils.contacts import ContactsModule
from utils.notes import NotesModule
from utils.mail import MailModule
from utils.message import MessageModule
from utils.reminders import RemindersModule
from utils.calendar import CalendarModule
from utils.maps import MapsModule

# Skip all tests if not on macOS
pytestmark = pytest.mark.skipif(
    not sys.platform == "darwin",
    reason="These tests can only run on macOS"
)

@pytest_asyncio.fixture(scope="module")
def event_loop():
    """Create an event loop for the test module."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module")
async def contacts():
    """Create a ContactsModule instance."""
    module = ContactsModule()
    has_access = await module.check_contacts_access()
    if not has_access:
        pytest.skip("No access to Contacts app")
    return module

@pytest_asyncio.fixture(scope="module")
async def notes():
    """Create a NotesModule instance."""
    module = NotesModule()
    has_access = await module.check_notes_access()
    if not has_access:
        pytest.skip("No access to Notes app")
    return module

@pytest_asyncio.fixture(scope="module")
async def mail():
    """Create a MailModule instance."""
    module = MailModule()
    has_access = await module.check_mail_access()
    if not has_access:
        pytest.skip("No access to Mail app")
    return module

@pytest_asyncio.fixture(scope="module")
async def messages():
    """Create a MessagesModule instance."""
    module = MessageModule()
    has_access = await module.check_messages_access()
    if not has_access:
        pytest.skip("No access to Messages app")
    return module

@pytest_asyncio.fixture(scope="module")
async def reminders():
    """Create a RemindersModule instance."""
    module = RemindersModule()
    has_access = await module.check_reminders_access()
    if not has_access:
        pytest.skip("No access to Reminders app")
    return module

@pytest_asyncio.fixture(scope="module")
async def calendar():
    """Create a CalendarModule instance."""
    module = CalendarModule()
    has_access = await module.check_calendar_access()
    if not has_access:
        pytest.skip("No access to Calendar app")
    return module

@pytest_asyncio.fixture(scope="module")
async def maps():
    """Create a MapsModule instance."""
    module = MapsModule()
    has_access = await module.check_maps_access()
    if not has_access:
        pytest.skip("No access to Maps app")
    return module 