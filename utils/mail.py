"""Mail module for interacting with Apple Mail."""

import logging
from typing import Dict, List, Any, Optional

from .applescript import (
    run_applescript_async, 
    AppleScriptError,
    format_applescript_value,
    parse_applescript_record,
    parse_applescript_list
)

logger = logging.getLogger(__name__)

class MailModule:
    """Module for interacting with Apple Mail"""
    
    async def check_mail_access(self) -> bool:
        """Check if Mail app is accessible"""
        try:
            script = '''
            try
                tell application "Mail"
                    get name
                    return true
                end tell
            on error
                return false
            end try
            '''
            
            result = await run_applescript_async(script)
            return result.strip().lower() == "true"
        except Exception as e:
            logger.error(f"Error checking Mail access: {e}")
            return False
    
    async def get_unread_mails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unread emails"""
        script = f'''
            tell application "Mail"
                set unreadMails to {{}}
                set msgs to (messages of inbox whose read status is false)
                repeat with i from 1 to {limit}
                    if i > count of msgs then exit repeat
                    set m to item i of msgs
                    set end of unreadMails to {{
                        subject:subject of m,
                        sender:sender of m,
                        content:content of m,
                        date:date received of m,
                        mailbox:"inbox"
                    }}
                end repeat
                return unreadMails as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            emails = parse_applescript_list(result)
            return [parse_applescript_record(email) for email in emails]
        except AppleScriptError as e:
            logger.error(f"Error getting unread emails: {e}")
            return []
    
    async def get_unread_mails_for_account(self, account: str, mailbox: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unread emails for a specific account"""
        mailbox_part = f'mailbox "{mailbox}"' if mailbox else "inbox"
        
        script = f'''
            tell application "Mail"
                set unreadMails to {{}}
                set theAccount to account "{account}"
                set msgs to (messages of {mailbox_part} of theAccount whose read status is false)
                repeat with i from 1 to {limit}
                    if i > count of msgs then exit repeat
                    set m to item i of msgs
                    set end of unreadMails to {{
                        subject:subject of m,
                        sender:sender of m,
                        content:content of m,
                        date:date received of m,
                        mailbox:name of mailbox of m,
                        account:name of account of m
                    }}
                end repeat
                return unreadMails as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            emails = parse_applescript_list(result)
            return [parse_applescript_record(email) for email in emails]
        except AppleScriptError as e:
            logger.error(f"Error getting unread emails for account: {e}")
            return []
    
    async def search_mails(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search emails"""
        script = f'''
            tell application "Mail"
                set searchResults to {{}}
                set msgs to messages of inbox whose subject contains "{search_term}" or content contains "{search_term}"
                repeat with i from 1 to {limit}
                    if i > count of msgs then exit repeat
                    set m to item i of msgs
                    set end of searchResults to {{
                        subject:subject of m,
                        sender:sender of m,
                        content:content of m,
                        date:date received of m,
                        mailbox:name of mailbox of m,
                        account:name of account of m
                    }}
                end repeat
                return searchResults as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            emails = parse_applescript_list(result)
            return [parse_applescript_record(email) for email in emails]
        except AppleScriptError as e:
            logger.error(f"Error searching emails: {e}")
            return []
    
    async def send_mail(self, to: str, subject: str, body: str, cc: Optional[str] = None, bcc: Optional[str] = None) -> Dict:
        """Send an email"""
        try:
            # Build the recipients part of the script
            recipients = f'make new to recipient with properties {{address:"{to}"}}'
            if cc:
                recipients += f'\nmake new cc recipient with properties {{address:"{cc}"}}'
            if bcc:
                recipients += f'\nmake new bcc recipient with properties {{address:"{bcc}"}}'

            script = f'''
                tell application "Mail"
                    set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
                    tell newMessage
                        {recipients}
                        send
                    end tell
                end tell
            '''
            
            await run_applescript_async(script)
            return {"success": True, "message": f"Email sent to {to}"}
        except AppleScriptError as e:
            logger.error(f"Error sending email: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_mailboxes_for_account(self, account: str) -> List[str]:
        """Get mailboxes for a specific account"""
        script = f'''
            tell application "Mail"
                set theMailboxes to {{}}
                set theAccount to account "{account}"
                repeat with m in mailboxes of theAccount
                    set end of theMailboxes to name of m
                end repeat
                return theMailboxes as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            return parse_applescript_list(result)
        except AppleScriptError as e:
            logger.error(f"Error getting mailboxes: {e}")
            return []
    
    async def get_mailboxes(self) -> List[str]:
        """Get all mailboxes"""
        script = '''
            tell application "Mail"
                set theMailboxes to {}
                repeat with a in accounts
                    repeat with m in mailboxes of a
                        set end of theMailboxes to name of m
                    end repeat
                end repeat
                return theMailboxes as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            return parse_applescript_list(result)
        except AppleScriptError as e:
            logger.error(f"Error getting all mailboxes: {e}")
            return []
    
    async def get_accounts(self) -> List[str]:
        """Get all email accounts"""
        script = '''
            tell application "Mail"
                set theAccounts to {}
                repeat with a in accounts
                    set end of theAccounts to name of a
                end repeat
                return theAccounts as text
            end tell
        '''
        
        try:
            result = await run_applescript_async(script)
            return parse_applescript_list(result)
        except AppleScriptError as e:
            logger.error(f"Error getting accounts: {e}")
            return []