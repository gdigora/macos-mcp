# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP server for macOS native apps (Contacts, Notes, Mail, Messages, Reminders, Calendar, Maps) using FastMCP. All interactions happen via AppleScript executed asynchronously.

## Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run MCP server
python apple_mcp.py

# Test server imports
python -c "from apple_mcp import mcp; print([t.name for t in mcp._tool_manager._tools.values()])"

# Run tests
pytest
pytest tests/test_contacts.py
pytest tests/test_contacts.py::test_find_contact -v
pytest --cov=utils tests/
```

## Architecture

```
apple_mcp.py          # FastMCP server entry point - defines all MCP tools
utils/
  applescript.py      # Core AppleScript execution (run_applescript_async, parsing)
  contacts.py         # ContactsModule - Contacts.app integration
  notes.py            # NotesModule - Notes.app integration
  mail.py             # MailModule - Mail.app integration
  message.py          # MessageModule - Messages.app (iMessage) integration
  reminders.py        # RemindersModule - Reminders.app integration
  calendar.py         # CalendarModule - Calendar.app integration
  maps.py             # MapsModule - Maps.app integration
```

**Data flow**: MCP tool → Module class method → `run_applescript_async()` → osascript subprocess → AppleScript parsing utilities → Pydantic model response

**Key pattern**: Each `utils/*.py` module follows the same structure:
- Class with async methods (e.g., `ContactsModule`)
- Methods build AppleScript strings and call `run_applescript_async()`
- Results parsed via `parse_applescript_list()` or `parse_applescript_record()`

**AppleScript helpers** (`utils/applescript.py`):
- `run_applescript_async(script)` - async subprocess execution via osascript
- `parse_applescript_list(output)` - converts `{item1, item2}` to Python list
- `parse_applescript_record(output)` - converts `{key:value}` to Python dict
- `escape_string(s)` - escapes quotes for AppleScript strings
- `AppleScriptError` - exception for script failures

## Adding New Functionality

1. Add module method in appropriate `utils/*.py` file using async pattern
2. Register as MCP tool in `apple_mcp.py` with `@mcp.tool()` decorator
3. Define Pydantic model if returning structured data
4. Add tests in `tests/test_*.py`
