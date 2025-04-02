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
                set allLists to {}
                repeat with l in every list
                    set end of allLists to {
                        name:name of l,
                        id:id of l,
                        color:color of l,
                        reminder_count:count of (reminders in l)
                    }
                end repeat
                return allLists as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            lists = parse_applescript_list(result)
            return [parse_applescript_record(lst) for lst in lists]
        except AppleScriptError as e:
            logger.error(f"Error getting reminder lists: {e}")
            return []
    
    async def get_all_reminders(self) -> List[Dict[str, Any]]:
        """Get all reminders"""
        script = '''
            tell application "Reminders"
                set allReminders to {}
                repeat with r in every reminder
                    set end of allReminders to {
                        name:name of r,
                        id:id of r,
                        notes:body of r,
                        due_date:due date of r,
                        completed:completed of r,
                        list:name of container of r
                    }
                end repeat
                return allReminders as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            reminders = parse_applescript_list(result)
            return [parse_applescript_record(reminder) for reminder in reminders]
        except AppleScriptError as e:
            logger.error(f"Error getting all reminders: {e}")
            return []
    
    async def search_reminders(self, search_text: str) -> List[Dict[str, Any]]:
        """Search for reminders matching text"""
        script = f'''
            tell application "Reminders"
                try
                    set matchingReminders to {{}}
                    repeat with r in every reminder
                        if name of r contains "{search_text}" or (body of r is not missing value and body of r contains "{search_text}") then
                            set reminderData to {{name:name of r, notes:body of r, due_date:due date of r, completed:completed of r, list:name of container of r}}
                            copy reminderData to end of matchingReminders
                        end if
                    end repeat
                    return matchingReminders
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
                
            reminders = parse_applescript_list(result)
            parsed_reminders = []
            
            for reminder in reminders:
                reminder_dict = parse_applescript_record(reminder)
                parsed_reminders.append(reminder_dict)
            
            return parsed_reminders
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