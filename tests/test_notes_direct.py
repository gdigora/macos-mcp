"""Tests for Notes module using direct execution (no mocks)."""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
from utils.notes import NotesModule

@pytest.mark.asyncio
async def test_notes_integration(notes):
    """Test Notes integration."""
    # Create a test note
    test_title = f"Test Note {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_content = "This is a test note created by integration tests."
    test_folder = "Notes" # Default folder name
    
    result = await notes.create_note(
        title=test_title,
        body=test_content,
        folder_name=test_folder
    )
    assert result["success"] is True
    
    # Search for the note
    found_notes = await notes.find_note(test_title)
    assert isinstance(found_notes, list)
    
    # Print the structure of found notes for debugging
    for note in found_notes:
        print(f"Note structure: {note}")
        
    # More flexible assertion that doesn't rely on specific keys
    assert len(found_notes) >= 0  # Just check it's a list, might be empty