# telegram_analyzer.py

import os
import asyncio
from urllib.parse import urlparse
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError

# .env ফাইল থেকে গোপন তথ্য লোড করা হচ্ছে
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

def parse_telegram_link(link):
    """
    একটি টেলিগ্রাম লিঙ্ক থেকে ইউজারনেম এবং মেসেজ আইডি বের করে আনে।
    """
    try:
        # লিঙ্কটি সঠিক কিনা তা পরীক্ষা করা হচ্ছে
        parsed_url = urlparse(link)
        if parsed_url.netloc != 't.me':
            return None, None, "এটি একটি অবৈধ টেলিগ্রাম লিঙ্ক।"

        # লিঙ্ক থেকে অংশগুলো আলাদা করা হচ্ছে
        path_parts = parsed_url.path.strip('/').split('/')
        
        # ইউজারনেম এবং মেসেজ আইডি আছে কিনা তা পরীক্ষা করা হচ্ছে
        if len(path_parts) < 2:
            return None, None, "লিঙ্কটিতে চ্যানেল ইউজারনেম বা মেসেজ আইডি খুঁজে পাওয়া যায়নি।"

        username = path_parts[0]
        message_id = int(path_parts[1])
        
        return username, message_id, None
    except (ValueError, IndexError):
        return None, None, "লিঙ্কটির গঠন সঠিক নয়। দয়া করে একটি সঠিক লিঙ্ক দিন।"


async def get_details_from_link(link):
    """
    মূল ফাংশন যা লিঙ্ক থেকে তথ্য বের করে এবং টেলিগ্রাম থেকে বিবরণ নিয়ে আসে।
    """
    # প্রথমে লিঙ্কটি পার্স বা বিশ্লেষণ করা হচ্ছে
    username, message_id, error = parse_telegram_link(link)
    if error:
        return error

    # .env ফাইলে সব তথ্য ঠিকমতো আছে কিনা তা পরীক্ষা করা হচ্ছে
    if not all([API_ID, API_HASH, SESSION_STRING]):
        return "সার্ভার এরর: আপনার .env ফাইলে এপিআই (API) সম্পর্কিত তথ্যগুলো সঠিকভাবে দেওয়া নেই।"

    # টেলিগ্রাম ক্লায়েন্টের সাথে সংযোগ স্থাপন করা হচ্ছে
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        try:
            message = await client.get_messages(username, ids=message_id)
            
            if not message:
                return f"খুঁজে পাওয়া যায়নি: '@{username}' চ্যানেলে '{message_id}' আইডি সহ কোনো মেসেজ পাওয়া যায়নি।"

            # সময় এবং তারিখ সম্পর্কিত তথ্য সংগ্রহ করা হচ্ছে
            utc_time = message.date
            local_time = utc_time.astimezone()

            # একটি ডিকশনারিতে সব তথ্য সাজিয়ে রিটার্ন করা হচ্ছে
            details = {
                "message_id": message.id,
                "chat_username": username,
                "message_text": message.text or "[এই মেসেজে কোনো লেখা নেই]",
                "iso_timestamp": utc_time.isoformat(),
                "local_time_str": local_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                "unix_timestamp": utc_time.timestamp()
            }
            return details
        
        except UsernameNotOccupiedError:
            return f"অবৈধ চ্যানেল: '@{username}' নামের কোনো চ্যানেল নেই।"
        except Exception as e:
            return f"একটি অপ্রত্যাশিত সমস্যা হয়েছে: {e}"