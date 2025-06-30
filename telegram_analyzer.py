# telegram_analyzer.py

import os
import asyncio
from urllib.parse import urlparse
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError, ChannelPrivateError

# Load credentials from .env file
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

def parse_telegram_link(link):
    """
    Parses a Telegram link to extract the chat entity (username or ID) and message ID.
    Handles both public and private ('/c/') links.
    """
    try:
        parsed_url = urlparse(link)
        if parsed_url.netloc != 't.me':
            return None, None, "Invalid Link: This does not appear to be a valid Telegram link."

        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return None, None, "Invalid Link: The link does not contain a channel/group and message ID."

        # Check if it's a private link (e.g., /c/123456789/123)
        if path_parts[0] == 'c':
            if len(path_parts) < 3:
                 return None, None, "Invalid Private Link: The link format is incorrect."
            # For private channels, the chat ID needs a -100 prefix
            chat_entity = int(f"-100{path_parts[1]}")
            message_id = int(path_parts[2])
        # Otherwise, it's a public link
        else:
            chat_entity = path_parts[0]
            message_id = int(path_parts[1])
        
        return chat_entity, message_id, None
    except (ValueError, IndexError):
        return None, None, "Link Parsing Error: The link structure is incorrect. Please provide a valid link."


async def get_details_from_link(link):
    """
    Main function that gets details from a link, supporting both public and private groups.
    """
    chat_entity, message_id, error = parse_telegram_link(link)
    if error:
        return error

    if not all([API_ID, API_HASH, SESSION_STRING]):
        return "Server Error: API credentials are not configured in the .env file."

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            message = await client.get_messages(chat_entity, ids=message_id)
            
            if not message:
                return f"Not Found: Message with ID '{message_id}' not found in the specified chat."

            # Get chat details to display the title/username
            chat_info = await client.get_entity(chat_entity)
            display_name = chat_info.title if hasattr(chat_info, 'title') else f"@{chat_info.username}"

            utc_time = message.date
            local_time = utc_time.astimezone()

            details = {
                "message_id": message.id,
                "chat_display_name": display_name,
                "message_text": message.text or "[This message has no text]",
                "iso_timestamp": utc_time.isoformat(),
                "local_time_str": local_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                "unix_timestamp": utc_time.timestamp()
            }
            return details
        
        except ChannelPrivateError:
            return "Access Error: This is a private group and you are not a member. Please join the group first."
        except (UsernameNotOccupiedError, ValueError):
            return f"Invalid Chat: The specified channel or group could not be found."
        except Exception as e:
            return f"An unexpected error occurred: {e}"