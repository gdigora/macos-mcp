"""Reminders module for interacting with Apple Reminders."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .applescript import (
    run_applescript_async, 
    AppleScriptError,
    format_applescript_value,
    parse_applescript_record,
    parse_applescript_list
)

logger = logging.getLogger(__name__)

class RemindersModule:
    """Module for interacting with Apple Reminders"""
    
    async def check_reminders_access(self) -> bool:
        """Check if Reminders app is accessible"""
        try:
            script = '''
            try
                tell application "Reminders"
                    get name
                    return true
                end tell
            on error
                return false
            end try
            '''
            
            result = await run_applescript_async(script)
            return result.lower() == 'true'
        except Exception as e:
            logger.error(f"Cannot access Reminders app: {e}")
            return False
    
    async def get_all_lists(self) -> List[Dict[str, Any]]:
        """Get all reminder lists"""
        script = '''
            tell application "Reminders"
                set output to "["
                set isFirst to true
                repeat with l in every list
                    set listName to name of l
                    set listId to id of l
                    set reminderCount to count of (reminders in l)
                    if not isFirst then
                        set output to output & ","
                    end if
                    set output to output & "{\\"name\\":\\"" & listName & "\\",\\"id\\":\\"" & listId & "\\",\\"reminder_count\\":" & reminderCount & "}"
                    set isFirst to false
                end repeat
                set output to output & "]"
                return output
            end tell
        '''

        try:
            import json
            result = await run_applescript_async(script)
            return json.loads(result)
        except AppleScriptError as e:
            logger.error(f"Error getting reminder lists: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing reminder lists JSON: {e}")
            return []
    
    async def get_all_reminders(self, limit: int = 50, list_name: Optional[str] = None, include_completed: bool = False) -> List[Dict[str, Any]]:
        """Get reminders. Filters to incomplete by default for performance."""
        target_list = f'list "{list_name}"' if list_name else 'default list'
        completed_filter = "" if include_completed else " whose completed is false"
        # Batch fetch names in single Apple event
        script = f'''
            tell application "Reminders"
                set theList to {target_list}
                set allNames to name of (reminders of theList{completed_filter})
                set maxItems to {limit}
                if (count of allNames) < maxItems then set maxItems to (count of allNames)
                set resultList to items 1 thru maxItems of allNames
                return resultList
            end tell
        '''

        try:
            result = await run_applescript_async(script)
            # Parse AppleScript list format: "item1, item2, item3"
            if not result.strip():
                return []
            names = parse_applescript_list(result)
            return [{"name": name.strip()} for name in names if name.strip()]
        except AppleScriptError as e:
            logger.error(f"Error getting all reminders: {e}")
            return []
    
    async def search_reminders(self, search_text: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for reminders matching text using server-side filtering (faster)."""
        # Use 'whose' clause for server-side filtering - much faster than AppleScript iteration
        from .applescript import escape_string
        escaped_text = escape_string(search_text)
        script = f'''
            tell application "Reminders"
                try
                    set matchingNames to name of (reminders whose name contains "{escaped_text}")
                    set maxItems to {limit}
                    if (count of matchingNames) < maxItems then set maxItems to (count of matchingNames)
                    if maxItems = 0 then return ""
                    set resultList to items 1 thru maxItems of matchingNames
                    return resultList
                on error errMsg
                    return "ERROR:" & errMsg
                end try
            end tell
        '''

        try:
            result = await run_applescript_async(script)
            if result.startswith("ERROR:"):
                logger.error(f"Error in AppleScript: {result}")
                return []
            if not result.strip():
                return []
            names = parse_applescript_list(result)
            return [{"name": name.strip()} for name in names if name.strip()]
        except AppleScriptError as e:
            logger.error(f"Error searching reminders: {e}")
            return []
    
    async def open_reminder(self, search_text: str) -> Dict[str, Any]:
        """Open a reminder matching text"""
        script = f'''
            tell application "Reminders"
                set foundReminder to missing value
                repeat with r in every reminder
                    if name of r contains "{search_text}" then
                        set foundReminder to r
                        exit repeat
                    end if
                end repeat
                
                if foundReminder is not missing value then
                    show foundReminder
                    return "SUCCESS:Opened reminder: " & name of foundReminder
                else
                    return "ERROR:No reminder found matching '{search_text}'"
                end if
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            success = result.startswith("SUCCESS:")
            
            return {
                "success": success,
                "message": result.replace("SUCCESS:", "").replace("ERROR:", ""),
                "reminder": None  # Note: We could parse the reminder details if needed
            }
        except AppleScriptError as e:
            logger.error(f"Error opening reminder: {e}")
            return {
                "success": False,
                "message": str(e),
                "reminder": None
            }
    
    async def create_reminder(self, name: str, list_name: str = None, notes: str = None, due_date: datetime = None) -> Dict[str, Any]:
        """Create a new reminder"""
        # Format date for AppleScript if provided
        due_date_str = due_date.strftime("%Y-%m-%d %H:%M:%S") if due_date else None
        
        # Build the properties string
        properties = [f'name:"{name}"']
        if notes:
            properties.append(f'body:"{notes}"')
        if due_date_str:
            properties.append(f'due date:date "{due_date_str}"')
            
        properties_str = ", ".join(properties)
        
        # Use default "Reminders" list if none specified
        list_to_use = list_name or 'Reminders'
        
        script = f'''
            tell application "Reminders"
                try
                    tell list "{list_to_use}"
                        make new reminder with properties {{{properties_str}}}
                        return "SUCCESS:Reminder created successfully in list '{list_to_use}'"
                    end tell
                on error errMsg
                    return "ERROR:" & errMsg
                end try
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            success = result.startswith("SUCCESS:")
            return {
                "success": success,
                "message": result.replace("SUCCESS:", "").replace("ERROR:", "")
            }
        except AppleScriptError as e:
            logger.error(f"Error creating reminder: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def delete_completed_reminders(self, list_name: Optional[str] = None, batch_size: int = 10) -> Dict[str, Any]:
        """Delete completed reminders in batches. Returns count deleted."""
        target_list = f'list "{list_name}"' if list_name else 'default list'
        script = f'''
            tell application "Reminders"
                try
                    set theList to {target_list}
                    set completedOnes to (reminders of theList whose completed is true)
                    set totalCount to count of completedOnes
                    set deleteCount to {batch_size}
                    if totalCount < deleteCount then set deleteCount to totalCount

                    repeat with i from 1 to deleteCount
                        delete item 1 of completedOnes
                        -- Refresh the list after each delete
                        set completedOnes to (reminders of theList whose completed is true)
                    end repeat

                    return "SUCCESS:" & deleteCount & " deleted, " & (totalCount - deleteCount) & " remaining"
                on error errMsg
                    return "ERROR:" & errMsg
                end try
            end tell
        '''

        try:
            result = await run_applescript_async(script)
            success = result.startswith("SUCCESS:")
            return {
                "success": success,
                "message": result.replace("SUCCESS:", "").replace("ERROR:", "")
            }
        except AppleScriptError as e:
            logger.error(f"Error deleting completed reminders: {e}")
            return {"success": False, "message": str(e)}

    async def get_completed_count(self, list_name: Optional[str] = None) -> Dict[str, Any]:
        """Get count of completed reminders in a list."""
        target_list = f'list "{list_name}"' if list_name else 'default list'
        script = f'''
            tell application "Reminders"
                try
                    set theList to {target_list}
                    set completedCount to count of (reminders of theList whose completed is true)
                    set incompleteCount to count of (reminders of theList whose completed is false)
                    return "completed:" & completedCount & ",incomplete:" & incompleteCount
                on error errMsg
                    return "ERROR:" & errMsg
                end try
            end tell
        '''

        try:
            result = await run_applescript_async(script)
            if result.startswith("ERROR:"):
                return {"success": False, "message": result.replace("ERROR:", "")}
            # Parse "completed:X,incomplete:Y"
            parts = dict(p.split(":") for p in result.split(","))
            return {
                "success": True,
                "completed": int(parts.get("completed", 0)),
                "incomplete": int(parts.get("incomplete", 0))
            }
        except AppleScriptError as e:
            logger.error(f"Error getting completed count: {e}")
            return {"success": False, "message": str(e)}

    async def get_reminders_from_list_by_id(self, list_id: str, props: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get reminders from a specific list by ID"""
        if not props:
            props = ["name", "id", "notes", "due_date", "completed"]
            
        props_str = ", ".join(props)
        
        script = f'''
            tell application "Reminders"
                set theList to list id "{list_id}"
                set listReminders to {{}}
                repeat with r in reminders in theList
                    set reminderProps to {{}}
                    {" ".join([f'set end of reminderProps to {{"{prop}":{prop} of r}}' for prop in props])}
                    set end of listReminders to reminderProps
                end repeat
                return listReminders as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            reminders = parse_applescript_list(result)
            
            # Combine properties for each reminder
            parsed_reminders = []
            for reminder in reminders:
                reminder_data = {}
                for prop_dict in parse_applescript_list(reminder):
                    reminder_data.update(parse_applescript_record(prop_dict))
                parsed_reminders.append(reminder_data)
                
            return parsed_reminders
        except AppleScriptError as e:
            logger.error(f"Error getting reminders from list: {e}")
            return []