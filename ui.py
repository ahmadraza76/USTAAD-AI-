from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, CallbackQuery
from config import COMMAND_DETAILS, DEFAULT_WELCOME_IMAGE, MAIN_MENU_IMG, BOT_USERNAME
from database import Database
import logging
from datetime import datetime, timedelta

# Missing imports
from moderation import add_warning, set_ban_status, add_verified_user
from utils import is_hindi  # Agar aapke paas is_hindi function utils.py mein hai

logger = logging.getLogger(__name__)

# Use the same db instance as main.py
db = Database('group_manager.db')

# ...existing code...

def register_callback_handlers(client: Client):
    @client.on_callback_query()
    async def callback_handler(_, callback_query: CallbackQuery):
        data = callback_query.data
        try:
            if data == "bot_info":
                await callback_query.message.edit_media(
                    InputMediaPhoto(
                        media=DEFAULT_WELCOME_IMAGE,
                        caption=(
                            "<b>🤖 Ustaad AI Bot Information</b><br><br>"
                            "<b>⚙️ Version:</b> 2.2<br>"
                            "<b>🧠 AI Model:</b> DeepSeek AI<br>"
                            "<b>✨ Main Features:</b><br>"
                            "- Smart AI Chat Assistant<br>"
                            "- Group Management<br>"
                            "- Text Humanization<br>"
                            "<b>👨‍💻 Developer:</b> @Mrnick66<br>"
                            "   - Python & AI Specialist<br>"
                            "   - Telegram Bot Developer<br>"
                            "   - Contact for custom bots<br>"
                            "   - <i>﹒Ｐｏｗｅｒｅｄ ｂｙ ＵＳＴＡＡＤ ＡＩ﹒</i><br>"
                            "<i>📌 A powerful AI assistant bot created with Pyrogram</i>"
                        ),
                        parse_mode="HTML"
                    ),
                    reply_markup=create_keyboard([
                        ("🔙 Back", "back_to_main", None),
                        ("📞 Contact", None, "https://t.me/Mrnick66"),
                        ("➕ Add to Group", None, f"http://t.me/{BOT_USERNAME}?startgroup=true")
                    ])
                )
            # ...existing code...
            elif data.startswith("confirm_"):
                parts = data.split("_")
                if len(parts) != 4:
                    raise ValueError("Invalid callback data format")
                action, user_id, chat_id = parts[1], int(parts[2]), int(parts[3])
                user = await client.get_users(user_id)
                # db instance already available
                if action == "ban":
                    await client.ban_chat_member(chat_id, user_id)
                    set_ban_status(db, user_id, chat_id, True)
                    await callback_query.message.edit_text(f"🚫 {user.mention} has been banned.", parse_mode="HTML")
                elif action == "kick":
                    await client.ban_chat_member(chat_id, user_id)
                    await client.unban_chat_member(chat_id, user_id)
                    await callback_query.message.edit_text(f"👢 {user.mention} has been kicked.", parse_mode="HTML")
                elif action == "mute":
                    until_date = datetime.now() + timedelta(hours=24)
                    await client.restrict_chat_member(chat_id, user_id, can_send_messages=False, until_date=until_date)
                    await callback_query.message.edit_text(f"🔇 {user.mention} has been muted for 24 hours.", parse_mode="HTML")
                elif action == "warn":
                    count, _ = add_warning(db, user_id, chat_id, "Manual warning")
                    await callback_query.message.edit_text(f"⚠️ {user.mention} has been warned ({count}/3).", parse_mode="HTML")
                    if count >= 3:
                        await client.ban_chat_member(chat_id, user_id)
                        set_ban_status(db, user_id, chat_id, True)
                        await callback_query.message.reply(f"🚫 {user.mention} has been banned for reaching 3 warnings.", parse_mode="HTML")
                elif action == "verify":
                    add_verified_user(db, user_id, chat_id)
                    await callback_query.message.edit_text(f"✅ {user.mention} has been verified.", parse_mode="HTML")
            # ...existing code...
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await callback_query.message.reply("❌ An error occurred.", parse_mode="HTML")
