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
    Parses a single Telegram link to extract the chat entity and message ID.
    """
    try:
        parsed_url = urlparse(link)
        if parsed_url.netloc != 't.me':
            return None, None
        
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) < 2:
            return None, None

        if path_parts[0] == 'c':
            if len(path_parts) < 3: return None, None
            chat_entity = int(f"-100{path_parts[1]}")
            message_id = int(path_parts[2])
        else:
            chat_entity = path_parts[0]
            message_id = int(path_parts[1])
        
        return chat_entity, message_id
    except (ValueError, IndexError):
        return None, None

async def analyze_links_in_bulk(links):
    """
    Analyzes a list of Telegram links and returns successful and failed results.
    """
    if not all([API_ID, API_HASH, SESSION_STRING]):
        return [], [{"link": link, "reason": "Server Error: API credentials not configured."} for link in links]

    successful_results = []
    failed_results = []

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        for link in links:
            chat_entity, message_id = parse_telegram_link(link)
            
            if not chat_entity or not message_id:
                failed_results.append({"link": link, "reason": "Invalid link format"})
                continue

            try:
                message = await client.get_messages(chat_entity, ids=message_id)
                if not message:
                    failed_results.append({"link": link, "reason": "Message not found"})
                    continue

                chat_info = await client.get_entity(chat_entity)
                display_name = chat_info.title if hasattr(chat_info, 'title') else f"@{chat_info.username}"
                
                utc_time = message.date
                local_time = utc_time.astimezone()

                successful_results.append({
                    "message_id": message.id,
                    "chat_display_name": display_name,
                    "local_time_str": local_time.strftime('%Y-%m-%d %H:%M:%S.%f %Z'),
                    "iso_timestamp": utc_time.isoformat(),
                    "unix_timestamp": message.date.timestamp()
                })
            
            except ChannelPrivateError:
                failed_results.append({"link": link, "reason": "Access Error: You are not in this private group."})
            except Exception as e:
                failed_results.append({"link": link, "reason": f"Error: {type(e).__name__}"})
    
    return successful_results, failed_results
