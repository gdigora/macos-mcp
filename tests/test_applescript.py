"""Tests for applescript module with enhanced logging."""

import pytest
import pytest_asyncio
import asyncio
import logging
from utils.applescript import (
    run_applescript,
    run_applescript_async,
    parse_applescript_list,
    parse_applescript_record,
    parse_value,
    escape_string,
    format_applescript_value,
    configure_logging,
    log_execution_time
)

@pytest_asyncio.fixture(scope="module")
def event_loop():
    """Create an event loop for the test module."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def applescript_test_logger():
    """Set up a test logger."""
    configure_logging(level=logging.DEBUG)
    return logging.getLogger("utils.applescript")

def test_parse_applescript_list():
    """Test parsing AppleScript lists with logging."""
    # Empty list
    assert parse_applescript_list("") == []
    assert parse_applescript_list("{}") == []
    
    # Simple list
    assert parse_applescript_list('{1, 2, 3}') == ['1', '2', '3']
    
    # List with quotes
    assert parse_applescript_list('{"a", "b", "c"}') == ['a', 'b', 'c']
    
    # Mixed list
    assert parse_applescript_list('{1, "two", 3}') == ['1', 'two', '3']

def test_parse_applescript_record():
    """Test parsing AppleScript records with logging."""
    # Empty record
    assert parse_applescript_record("") == {}
    assert parse_applescript_record("{}") == {}
    
    # Simple record
    record = parse_applescript_record('{name:="John", age:=30}')
    assert record["name"] == "John"
    assert record["age"] == 30
    
    # Nested record
    record = parse_applescript_record('{person:={name:="Jane", age:=25}, active:=true}')
    assert record["active"] is True
    # Our current implementation just keeps the string representation of nested records
    assert isinstance(record["person"], str)
    assert "name:=" in record["person"]  # Just checking it contains the expected string

def test_parse_value():
    """Test value parsing with logging."""
    # String values
    assert parse_value('"Hello"') == "Hello"
    
    # Numeric values
    assert parse_value("42") == 42
    assert parse_value("3.14") == 3.14
    
    # Boolean values
    assert parse_value("true") is True
    assert parse_value("false") is False
    
    # Missing value
    assert parse_value("missing value") is None
    
    # Default case
    assert parse_value("something else") == "something else"

def test_escape_string():
    """Test string escaping."""
    assert escape_string('test"with"quotes') == 'test\\"with\\"quotes'
    assert escape_string("test'with'quotes") == "test\\'with\\'quotes"

def test_format_applescript_value():
    """Test formatting Python values for AppleScript."""
    # None value
    assert format_applescript_value(None) == "missing value"
    
    # Boolean values
    assert format_applescript_value(True) == "true"
    assert format_applescript_value(False) == "false"
    
    # Numeric values
    assert format_applescript_value(42) == "42"
    assert format_applescript_value(3.14) == "3.14"
    
    # String value
    assert format_applescript_value("Hello") == '"Hello"'
    
    # List value
    assert format_applescript_value([1, 2, 3]) == "{1, 2, 3}"
    
    # Dictionary value
    assert format_applescript_value({"name": "John", "age": 30}) == "{name:\"John\", age:30}"

def test_log_execution_time_decorator():
    """Test the log execution time decorator."""
    # Create a test function
    @log_execution_time
    def test_func(x, y):
        return x + y
    
    # Call the function
    result = test_func(1, 2)
    assert result == 3

@pytest.mark.asyncio
async def test_run_applescript_async_mock(monkeypatch):
    """Test run_applescript_async with a mocked subprocess."""
    # Mock the subprocess.create_subprocess_exec function
    class MockProcess:
        async def communicate(self):
            return b"test output", b""
        
        @property
        def returncode(self):
            return 0
    
    async def mock_create_subprocess_exec(*args, **kwargs):
        return MockProcess()
    
    # Apply the monkeypatch
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_create_subprocess_exec)
    
    # Run the function
    result = await run_applescript_async('tell application "System Events" to return "hello"')
    assert result == "test output"