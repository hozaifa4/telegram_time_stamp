#telegram_analyzer.py
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError

# Load credentials from .env file
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

async def get_message_details(public_username, message_id):
    """
    Fetches message details from a PUBLIC Telegram channel/group.
    Returns a dictionary with details on success, or an error string on failure.
    """
    if not all([API_ID, API_HASH, SESSION_STRING]):
        return "Server Error: API credentials are not configured in the .env file."

    try:
        msg_id = int(message_id)
    except ValueError:
        return f"Invalid Input: Message ID '{message_id}' must be a number."

    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            message = await client.get_messages(public_username, ids=msg_id)
            
            if not message:
                return f"Not Found: Message with ID '{msg_id}' not found in channel '@{public_username}'."

            # Collect message details
            utc_time = message.date
            local_time = utc_time.astimezone()

            details = {
                "message_id": message.id,
                "chat_username": public_username,
                "message_text": message.text or "[This message has no text]",
                "iso_timestamp": utc_time.isoformat(),
                "local_time_str": local_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                "unix_timestamp": utc_time.timestamp()
            }
            return details
        
        except UsernameNotOccupiedError:
            return f"Invalid Channel: The username '@{public_username}' does not exist or is not a channel."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
