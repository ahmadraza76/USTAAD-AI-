from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, CallbackQuery
from config import COMMAND_DETAILS, DEFAULT_WELCOME_IMAGE, MAIN_MENU_IMG, BOT_USERNAME
from database import Database
import logging

logger = logging.getLogger(__name__)

async def is_admin(client, message):
    if message.chat.type == "private":
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ["administrator", "creator"]
    except Exception as e:
        logger.error(f"Admin check error: {e}")
        return False

def admin_only():
    async def decorator(client, message):
        if not await is_admin(client, message):
            lang = "Hindi" if is_hindi(message.text or "") else "English"
            await message.reply(
                "❌ Yeh command sirf admins ke liye hai!" if lang == "Hindi" else
                "❌ This command is for admins only!"
            )
            return False
        return True
    return filters.create(decorator)

def create_keyboard(buttons):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=cb_data or url, url=url if not cb_data else None)]
        for row in buttons
        for text, cb_data, url in [row] if isinstance(row, tuple)
    ])

def main_menu_keyboard():
    return create_keyboard([
        ("📜 INFO", "bot_info", None),
        ("🆘 HELP", "help_menu", None),
        ("➕ Add to Group", None, f"http://t.me/{BOT_USERNAME}?startgroup=true"),
        ("🤖 AI Chat", "ai_chat", None)
    ])

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
            elif data == "help_menu":
                buttons = [(details["title"], f"help_{category}", None) for category, details in COMMAND_DETAILS.items()]
                buttons.append(("🔙 Back", "back_to_main", None))
                await callback_query.message.edit_media(
                    InputMediaPhoto(
                        media=MAIN_MENU_IMG,
                        caption="Select a command category:",
                        parse_mode="HTML"
                    ),
                    reply_markup=create_keyboard(buttons)
                )
            elif data.startswith("help_"):
                category = data.split("_", 1)[1]
                if category in COMMAND_DETAILS:
                    details = COMMAND_DETAILS[category]
                    await callback_query.message.edit_media(
                        InputMediaPhoto(
                            media=details["image"],
                            caption=f"<b>{details['title']}</b><br><br>"
                                    f"{details['description']}<br><br>" +
                                    "<br>".join(f"• {cmd}" for cmd in details["commands"]),
                            parse_mode="HTML"
                        ),
                        reply_markup=create_keyboard([("🔙 Back", "help_menu", None)])
                    )
            elif data == "ai_chat":
                await callback_query.message.edit_text(
                    "<b>🤖 Ustaad AI Chat</b><br><br>"
                    "Type your question in private chat<br>"
                    "Or use <code>/ask [question]</code><br>"
                    "Example: <code>/ask What is a solar eclipse?</code>",
                    reply_markup=create_keyboard([("🔙 Back", "back_to_main", None)]),
                    parse_mode="HTML"
                )
            elif data == "back_to_main":
                await callback_query.message.edit_media(
                    InputMediaPhoto(
                        media=MAIN_MENU_IMG,
                        caption="Ustaad AI Main Options:",
                        parse_mode="HTML"
                    ),
                    reply_markup=main_menu_keyboard()
                )
            elif data == "appeal_warning":
                await callback_query.message.reply(
                    "📩 Please contact an admin to appeal this warning.",
                    reply_markup=create_keyboard([("📞 Contact Admin", None, "https://t.me/Mrnick66")]),
                    parse_mode="HTML"
                )
            elif data.startswith("confirm_"):
                parts = data.split("_")
                if len(parts) != 4:
                    raise ValueError("Invalid callback data format")
                action, user_id, chat_id = parts[1], int(parts[2]), int(parts[3])
                user = await client.get_users(user_id)
                db = Database('group_manager.db')
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
            elif data.startswith("cancel_"):
                await callback_query.message.edit_text("❌ Action cancelled.", parse_mode="HTML")
            await callback_query.answer()
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await callback_query.message.reply("❌ An error occurred.", parse_mode="HTML")
