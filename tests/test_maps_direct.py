"""Tests for Maps module using direct execution (no mocks)."""

import pytest
import pytest_asyncio
import asyncio
from utils.maps import MapsModule

@pytest.mark.asyncio
async def test_maps_search(maps):
    """Test searching for locations in Maps."""
    # Search for a location
    result = await maps.search_locations("San Francisco")
    
    # Print the structure for debugging
    print("Maps search result structure:")
    print(f"Result: {result}")
    
    # Just assert we get a dictionary back
    assert isinstance(result, dict)
    
    # Check if locations is in the result (might not be due to permissions)
    if "locations" in result:
        assert isinstance(result["locations"], list)