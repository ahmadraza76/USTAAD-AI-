from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database, is_auto_management_enabled, is_welcome_enabled, is_goodbye_enabled
from database import get_welcome_message, get_goodbye_message, is_verified_user, add_warning, set_ban_status
from database import increment_message_count, get_auto_replies
from ai import is_toxic_message, generate_welcome_message
from config import DEFAULT_WELCOME_IMAGE
from ui import create_keyboard
import logging
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

user_message_timestamps = defaultdict(list)

async def check_flood(user_id, chat_id):
    now = time.time()
    key = (user_id, chat_id)
    user_message_timestamps[key].append(now)
    user_message_timestamps[key] = [t for t in user_message_timestamps[key] if now - t < 30]
    return len(user_message_timestamps[key]) > 5

def register_moderation_handlers(client: Client):
    @client.on_message(filters.new_chat_members)
    async def welcome_new_member(_, message: Message):
        db = Database('group_manager.db')
        if not is_auto_management_enabled(db, message.chat.id) or not is_welcome_enabled(db, message.chat.id):
            return
        for member in message.new_chat_members:
            if member.id == client.me.id:
                await message.reply_photo(
                    photo=DEFAULT_WELCOME_IMAGE,
                    caption="🙏 Thank you for adding Ustaad AI to this group!\n\n"
                            "I'm an advanced AI bot that can help with:\n"
                            "- Answering questions\n"
                            "- Managing groups\n"
                            "- Humanizing text\n"
                            "Use /start to see all options.",
                    reply_markup=create_keyboard([("🤖 Try AI Chat", "ai_chat", None)])
                )
            else:
                custom_msg, image_url = get_welcome_message(db, message.chat.id)
                final_msg = custom_msg.replace("{name}", member.first_name) if custom_msg else await generate_welcome_message(member.first_name)
                await message.reply_photo(photo=image_url, caption=final_msg, parse_mode="HTML")

    @client.on_message(filters.left_chat_member)
    async def goodbye_member(_, message: Message):
        db = Database('group_manager.db')
        if not is_auto_management_enabled(db, message.chat.id) or not is_goodbye_enabled(db, message.chat.id):
            return
        member = message.left_chat_member
        goodbye_msg = get_goodbye_message(db, message.chat.id)
        default_msg = f"👋 {member.mention} has left the group."
        final_msg = goodbye_msg.replace("{name}", member.first_name) if goodbye_msg else default_msg
        await message.reply(final_msg, parse_mode="HTML")

    @client.on_message(filters.text & filters.group)
    async def moderate_message(_, message: Message):
        db = Database('group_manager.db')
        if not is_auto_management_enabled(db, message.chat.id):
            return
        if await check_flood(message.from_user.id, message.chat.id):
            await message.reply("⚠️ Slow down! You're sending messages too fast.", parse_mode="HTML")
            return
        if not is_verified_user(db, message.from_user.id, message.chat.id):
            if await is_toxic_message(message.text):
                await message.delete()
                count, _ = add_warning(db, message.from_user.id, message.chat.id, "Toxic message")
                await message.reply(
                    f"⚠️ {message.from_user.mention}, your message was removed for being inappropriate. Warning {count}/3.",
                    reply_markup=create_keyboard([("📩 Appeal", "appeal_warning", None)]),
                    parse_mode="HTML"
                )
                if count >= 3:
                    await client.ban_chat_member(message.chat.id, message.from_user.id)
                    set_ban_status(db, message.from_user.id, message.chat.id, True)
                    await message.reply(f"🚫 {message.from_user.mention} has been banned for reaching 3 warnings.", parse_mode="HTML")
                return
        increment_message_count(db, message.from_user.id, message.chat.id)
        auto_replies = get_auto_replies(db, message.chat.id)
        for trigger, response in auto_replies.items():
            if trigger.lower() in message.text.lower():
                await message.reply(response, parse_mode="HTML")
                break
