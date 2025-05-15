from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_USERNAME, DEFAULT_WELCOME_IMAGE
from database import Database, get_welcome_message, set_welcome_message, delete_welcome_message
from database import get_goodbye_message, set_goodbye_message, delete_goodbye_message
from database import toggle_welcome, toggle_goodbye, toggle_auto_management
from database import add_auto_reply, remove_auto_reply, get_auto_replies
from ui import create_keyboard, admin_only
from ai import ask_deepseek, humanize_text, sanitize_input, is_hindi
import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def register_command_handlers(client: Client):
    @client.on_message(filters.command("start"))
    async def start(_, message: Message):
        lang = "Hindi" if is_hindi(message.text or "") else "English"
        if message.chat.type == "private":
            caption = (
                "🌟 नमस्ते! मैं Ustaad AI हूँ - आपका उन्नत AI सहायक<br><br>"
                "मैं आपकी मदद कर सकता हूँ:<br>"
                "- AI चैट (DeepSeek AI)<br>"
                "- ग्रुप प्रबंधन<br>"
                "- टेक्स्ट को मानवीय बनाना<br>"
                "नीचे के बटन का उपयोग करें:<br>"
                "<i>Powered by Ustaad AI</i>" if lang == "Hindi" else
                "🌟 Hello! I'm Ustaad AI - Your Advanced AI Assistant<br><br>"
                "I can help you with:<br>"
                "- AI Chat (DeepSeek AI)<br>"
                "- Managing groups<br>"
                "- Humanizing text<br>"
                "Use buttons below to explore:<br>"
                "<i>Powered by Ustaad AI</i>"
            )
            await message.reply_photo(
                photo=DEFAULT_WELCOME_IMAGE,
                caption=caption,
                reply_markup=create_keyboard([
                    ("📜 INFO", "bot_info", None),
                    ("🆘 HELP", "help_menu", None),
                    ("➕ Add to Group", None, f"http://t.me/{BOT_USERNAME}?startgroup=true"),
                    ("🤖 AI Chat", "ai_chat", None)
                ]),
                parse_mode="HTML"
            )
        else:
            caption = (
                "हेलो! Ustaad AI इस ग्रुप में मदद के लिए तैयार है।<br><br>"
                "सभी फीचर्स देखने के लिए प्राइवेट चैट में /start करें।" if lang == "Hindi" else
                "Hello! Ustaad AI is ready to assist in this group.<br><br>"
                "Use /start in private chat to see all features."
            )
            await message.reply_photo(
                photo=DEFAULT_WELCOME_IMAGE,
                caption=caption,
                reply_markup=create_keyboard([("🤖 Try AI Chat", "ai_chat", None)]),
                parse_mode="HTML"
            )

    @client.on_message(filters.command("ask"))
    async def ai_chat(_, message: Message):
        if len(message.command) < 2:
            return await message.reply("Please ask a question.<br>Example: <code>/ask What is a solar eclipse?</code>", parse_mode="HTML")
        question = sanitize_input(' '.join(message.command[1:]))
        processing_msg = await message.reply("🧠 Ustaad AI is thinking...", parse_mode="HTML")
        response = await ask_deepseek(question)
        await processing_msg.delete()
        await message.reply(f"🧠 Ustaad AI Response:<br>{response}", parse_mode="HTML")

    @client.on_message(filters.command("humanize"))
    async def humanize(_, message: Message):
        if len(message.command) < 2:
            return await message.reply("Please provide text to humanize.<br>Example: <code>/humanize I am commencing the utilization of this bot.</code>", parse_mode="HTML")
        text = sanitize_input(' '.join(message.command[1:]))
        processing_msg = await message.reply("🗣️ Ustaad AI is making it sound human...", parse_mode="HTML")
        response = humanize_text(text)
        await processing_msg.delete()
        await message.reply(response, parse_mode="HTML")

    @client.on_message(filters.command("promote") & filters.group & admin_only())
    async def promote_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/promote @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            await client.promote_chat_member(
                message.chat.id, user.id,
                can_manage_chat=True, can_delete_messages=True, can_restrict_members=True, can_pin_messages=True
            )
            await message.reply(f"✅ {user.mention} has been promoted to admin.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Promote error: {e}")
            await message.reply("❌ Failed to promote user.", parse_mode="HTML")

    @client.on_message(filters.command("demote") & filters.group & admin_only())
    async def demote_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/demote @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            await client.promote_chat_member(message.chat.id, user.id)
            await message.reply(f"✅ {user.mention} has been demoted.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Demote error: {e}")
            await message.reply("❌ Failed to demote user.", parse_mode="HTML")

    @client.on_message(filters.command("ban") & filters.group & admin_only())
    async def ban_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/ban @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            await message.reply(
                f"Are you sure you want to ban {user.mention}?",
                reply_markup=create_keyboard([
                    ("✅ Confirm", f"confirm_ban_{user.id}_{message.chat.id}", None),
                    ("❌ Cancel", f"cancel_ban_{user.id}_{message.chat.id}", None)
                ]),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ban error: {e}")
            await message.reply("❌ Failed to ban user.", parse_mode="HTML")

    @client.on_message(filters.command("unban") & filters.group & admin_only())
    async def unban_user(_, message: Message):
        if len(message.command) < 2:
            return await message.reply("Please mention a user: <code>/unban @username</code>", parse_mode="HTML")
        try:
            user = await client.get_users(message.command[1])
            await client.unban_chat_member(message.chat.id, user.id)
            db = Database('group_manager.db')
            set_ban_status(db, user.id, message.chat.id, False)
            await message.reply(f"✅ {user.mention} has been unbanned.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Unban error: {e}")
            await message.reply("❌ Failed to unban user.", parse_mode="HTML")

    @client.on_message(filters.command("verify") & filters.group & admin_only())
    async def verify_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/verify @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            await message.reply(
                f"Are you sure you want to verify {user.mention}?",
                reply_markup=create_keyboard([
                    ("✅ Confirm", f"confirm_verify_{user.id}_{message.chat.id}", None),
                    ("❌ Cancel", f"cancel_verify_{user.id}_{message.chat.id}", None)
                ]),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Verify error: {e}")
            await message.reply("❌ Failed to verify user.", parse_mode="HTML")

    @client.on_message(filters.command("kick") & filters.group & admin_only())
    async def kick_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/kick @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            await message.reply(
                f"Are you sure you want to kick {user.mention}?",
                reply_markup=create_keyboard([
                    ("✅ Confirm", f"confirm_kick_{user.id}_{message.chat.id}", None),
                    ("❌ Cancel", f"cancel_kick_{user.id}_{message.chat.id}", None)
                ]),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Kick error: {e}")
            await message.reply("❌ Failed to kick user.", parse_mode="HTML")

    @client.on_message(filters.command("mute") & filters.group & admin_only())
    async def mute_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/mute @username [duration]</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            duration = 24 * 3600
            if len(message.command) > 2:
                dur_str = message.command[2]
                if dur_str.endswith(('s', 'm', 'h')):
                    value = int(dur_str[:-1])
                    unit = dur_str[-1]
                    duration = value if unit == 's' else value * 60 if unit == 'm' else value * 3600
            await message.reply(
                f"Are you sure you want to mute {user.mention} for {duration//3600} hours?",
                reply_markup=create_keyboard([
                    ("✅ Confirm", f"confirm_mute_{user.id}_{message.chat.id}", None),
                    ("❌ Cancel", f"cancel_mute_{user.id}_{message.chat.id}", None)
                ]),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Mute error: {e}")
            await message.reply("❌ Failed to mute user.", parse_mode="HTML")

    @client.on_message(filters.command("unmute") & filters.group & admin_only())
    async def unmute_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/unmute @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            await client.restrict_chat_member(message.chat.id, user.id, can_send_messages=True)
            await message.reply(f"✅ {user.mention} has been unmuted.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Unmute error: {e}")
            await message.reply("❌ Failed to unmute user.", parse_mode="HTML")

    @client.on_message(filters.command("ro") & filters.group & admin_only())
    async def set_read_only(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/ro @username [duration]</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            duration = 3600
            if len(message.command) > 2:
                dur_str = message.command[2]
                if dur_str.endswith(('s', 'm', 'h')):
                    value = int(dur_str[:-1])
                    unit = dur_str[-1]
                    duration = value if unit == 's' else value * 60 if unit == 'm' else value * 3600
            until_date = datetime.now() + timedelta(seconds=duration)
            await client.restrict_chat_member(
                message.chat.id, user.id,
                can_send_messages=False, can_send_media=False, can_send_polls=False, can_send_other_messages=False,
                until_date=until_date
            )
            await message.reply(f"✅ {user.mention} is in read-only mode for {duration//3600} hours.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Read-only error: {e}")
            await message.reply("❌ Failed to set read-only mode.", parse_mode="HTML")

    @client.on_message(filters.command("unro") & filters.group & admin_only())
    async def unset_read_only(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/unro @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            await client.restrict_chat_member(
                message.chat.id, user.id,
                can_send_messages=True, can_send_media=True, can_send_polls=True, can_send_other_messages=True
            )
            await message.reply(f"✅ {user.mention} has been removed from read-only mode.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Unset read-only error: {e}")
            await message.reply("❌ Failed to remove read-only mode.", parse_mode="HTML")

    @client.on_message(filters.command("warn") & filters.group & admin_only())
    async def warn_user(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/warn @username [reason]</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            reason = ' '.join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
            await message.reply(
                f"Are you sure you want to warn {user.mention} for: {reason}?",
                reply_markup=create_keyboard([
                    ("✅ Confirm", f"confirm_warn_{user.id}_{message.chat.id}", None),
                    ("❌ Cancel", f"cancel_warn_{user.id}_{message.chat.id}", None)
                ]),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Warn error: {e}")
            await message.reply("❌ Failed to warn user.", parse_mode="HTML")

    @client.on_message(filters.command("pin") & filters.group & admin_only())
    async def pin_message(_, message: Message):
        if not message.reply_to_message:
            return await message.reply("Please reply to a message to pin.", parse_mode="HTML")
        try:
            await message.reply_to_message.pin()
            await message.reply("✅ Message pinned.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Pin error: {e}")
            await message.reply("❌ Failed to pin message.", parse_mode="HTML")

    @client.on_message(filters.command("unpin") & filters.group & admin_only())
    async def unpin_message(_, message: Message):
        if not message.reply_to_message:
            return await message.reply("Please reply to a message to unpin.", parse_mode="HTML")
        try:
            await message.reply_to_message.unpin()
            await message.reply("✅ Message unpinned.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Unpin error: {e}")
            await message.reply("❌ Failed to unpin message.", parse_mode="HTML")

    @client.on_message(filters.command("del") & filters.group & admin_only())
    async def delete_message(_, message: Message):
        if not message.reply_to_message:
            return await message.reply("Please reply to a message to delete.", parse_mode="HTML")
        try:
            await message.reply_to_message.delete()
            await message.reply("✅ Message deleted.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Delete error: {e}")
            await message.reply("❌ Failed to delete message.", parse_mode="HTML")

    @client.on_message(filters.command("purge") & filters.group & admin_only())
    async def purge_messages(_, message: Message):
        if len(message.command) < 2 or not message.command[1].isdigit():
            return await message.reply("Please specify a number: <code>/purge 10</code>", parse_mode="HTML")
        count = min(int(message.command[1]), 100)
        try:
            async for msg in client.iter_history(message.chat.id, limit=count):
                await msg.delete()
            await message.reply(f"✅ {count} messages deleted.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Purge error: {e}")
            await message.reply("❌ Failed to purge messages.", parse_mode="HTML")

    @client.on_message(filters.command("clean") & filters.group & admin_only())
    async def clean_messages(_, message: Message):
        try:
            async for msg in client.iter_history(message.chat.id, limit=100):
                if msg.from_user.id == client.me.id or await is_toxic_message(msg.text or ""):
                    await msg.delete()
            await message.reply("✅ Cleaned bot messages and spam.", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Clean error: {e}")
            await message.reply("❌ Failed to clean messages.", parse_mode="HTML")

    @client.on_message(filters.command("setwelcome") & filters.group & admin_only())
    async def set_welcome(_, message: Message):
        if len(message.command) < 2:
            return await message.reply("Please provide a welcome message: <code>/setwelcome Welcome {name}!</code>", parse_mode="HTML")
        msg = ' '.join(message.command[1:])
        db = Database('group_manager.db')
        set_welcome_message(db, message.chat.id, msg)
        await message.reply("✅ Welcome message set.", parse_mode="HTML")

    @client.on_message(filters.command("delwelcome") & filters.group & admin_only())
    async def delete_welcome(_, message: Message):
        db = Database('group_manager.db')
        delete_welcome_message(db, message.chat.id)
        await message.reply("✅ Welcome message deleted.", parse_mode="HTML")

    @client.on_message(filters.command("setgoodbye") & filters.group & admin_only())
    async def set_goodbye(_, message: Message):
        if len(message.command) < 2:
            return await message.reply("Please provide a goodbye message: <code>/setgoodbye Goodbye {name}!</code>", parse_mode="HTML")
        msg = ' '.join(message.command[1:])
        db = Database('group_manager.db')
        set_goodbye_message(db, message.chat.id, msg)
        await message.reply("✅ Goodbye message set.", parse_mode="HTML")

    @client.on_message(filters.command("delgoodbye") & filters.group & admin_only())
    async def delete_goodbye(_, message: Message):
        db = Database('group_manager.db')
        delete_goodbye_message(db, message.chat.id)
        await message.reply("✅ Goodbye message deleted.", parse_mode="HTML")

    @client.on_message(filters.command("welcome") & filters.group & admin_only())
    async def toggle_welcome_cmd(_, message: Message):
        if len(message.command) < 2 or message.command[1].lower() not in ["on", "off"]:
            return await message.reply("Please specify: <code>/welcome on</code> or <code>/welcome off</code>", parse_mode="HTML")
        status = message.command[1].lower() == "on"
        db = Database('group_manager.db')
        toggle_welcome(db, message.chat.id, status)
        await message.reply(f"✅ Welcome messages {'enabled' if status else 'disabled'}.", parse_mode="HTML")

    @client.on_message(filters.command("goodbye") & filters.group & admin_only())
    async def toggle_goodbye_cmd(_, message: Message):
        if len(message.command) < 2 or message.command[1].lower() not in ["on", "off"]:
            return await message.reply("Please specify: <code>/goodbye on</code> or <code>/goodbye off</code>", parse_mode="HTML")
        status = message.command[1].lower() == "on"
        db = Database('group_manager.db')
        toggle_goodbye(db, message.chat.id, status)
        await message.reply(f"✅ Goodbye messages {'enabled' if status else 'disabled'}.", parse_mode="HTML")

    @client.on_message(filters.command("setwelcomeimage") & filters.group & admin_only())
    async def set_welcome_image(_, message: Message):
        if len(message.command) < 2 or not re.match(r'https?://\S+', message.command[1]):
            return await message.reply("Please provide a valid image URL: <code>/setwelcomeimage https://example.com/image.jpg</code>", parse_mode="HTML")
        image_url = message.command[1]
        db = Database('group_manager.db')
        msg, _ = get_welcome_message(db, message.chat.id)
        set_welcome_message(db, message.chat.id, msg or "Welcome {name}!", image_url)
        await message.reply("✅ Welcome image set.", parse_mode="HTML")

    @client.on_message(filters.command("filter") & filters.group & admin_only())
    async def add_filter(_, message: Message):
        if len(message.command) < 3:
            return await message.reply("Usage: <code>/filter word response</code>", parse_mode="HTML")
        trigger, response = message.command[1], ' '.join(message.command[2:])
        db = Database('group_manager.db')
        add_auto_reply(db, message.chat.id, trigger, response)
        await message.reply(f"✅ Auto-reply set for '{trigger}'", parse_mode="HTML")

    @client.on_message(filters.command("stop") & filters.group & admin_only())
    async def remove_filter(_, message: Message):
        if len(message.command) < 2:
            return await message.reply("Usage: <code>/stop word</code>", parse_mode="HTML")
        trigger = message.command[1]
        db = Database('group_manager.db')
        remove_auto_reply(db, message.chat.id, trigger)
        await message.reply(f"✅ Auto-reply for '{trigger}' removed.", parse_mode="HTML")

    @client.on_message(filters.command("filters") & filters.group & admin_only())
    async def list_filters(_, message: Message):
        db = Database('group_manager.db')
        auto_replies = get_auto_replies(db, message.chat.id)
        if not auto_replies:
            return await message.reply("No auto-replies set.", parse_mode="HTML")
        response = "Active auto-replies:<br>" + "<br>".join(f"• {trigger}: {response}" for trigger, response in auto_replies.items())
        await message.reply(response, parse_mode="HTML")

    @client.on_message(filters.command("toggleauto") & filters.group & admin_only())
    async def toggle_auto(_, message: Message):
        if len(message.command) < 2 or message.command[1].lower() not in ["on", "off"]:
            return await message.reply("Please specify: <code>/toggleauto on</code> or <code>/toggleauto off</code>", parse_mode="HTML")
        status = message.command[1].lower() == "on"
        db = Database('group_manager.db')
        toggle_auto_management(db, message.chat.id, status)
        await message.reply(f"✅ Auto-management {'enabled' if status else 'disabled'}.", parse_mode="HTML")

    @client.on_message(filters.command("id"))
    async def get_id(_, message: Message):
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            await message.reply(f"User ID: {user_id}<br>Chat ID: {message.chat.id}", parse_mode="HTML")
        else:
            await message.reply(f"Chat ID: {message.chat.id}", parse_mode="HTML")

    @client.on_message(filters.command("userinfo") & filters.group)
    async def user_info(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/userinfo @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            db = Database('group_manager.db')
            msg_count, warn_count, banned = get_user_stats(db, user.id, message.chat.id)
            verified = is_verified_user(db, user.id, message.chat.id)
            await message.reply(
                f"<b>👤 User Info</b><br><br>"
                f"Name: {user.mention}<br>"
                f"ID: {user.id}<br>"
                f"Messages: {msg_count}<br>"
                f"Warnings: {warn_count}/3<br>"
                f"Banned: {'Yes' if banned else 'No'}<br>"
                f"Verified: {'Yes' if verified else 'No'}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Userinfo error: {e}")
            await message.reply("❌ Failed to fetch user info.", parse_mode="HTML")

    @client.on_message(filters.command("chatinfo") & filters.group)
    async def chat_info(_, message: Message):
        try:
            chat = await client.get_chat(message.chat.id)
            await message.reply(
                f"<b>🏛 Chat Info</b><br><br>"
                f"Title: {chat.title}<br>"
                f"ID: {chat.id}<br>"
                f"Type: {chat.type}<br>"
                f"Members: {chat.members_count}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Chatinfo error: {e}")
            await message.reply("❌ Failed to fetch chat info.", parse_mode="HTML")

    @client.on_message(filters.command("admins") & filters.group)
    async def list_admins(_, message: Message):
        try:
            admins = []
            async for member in client.iter_chat_members(message.chat.id, filter="administrators"):
                admins.append(f"• {member.user.mention}")
            await message.reply(
                "<b>👑 Admins</b><br><br>" + "<br>".join(admins) if admins else "No admins found.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Admins error: {e}")
            await message.reply("❌ Failed to fetch admins.", parse_mode="HTML")

    @client.on_message(filters.command("stats") & filters.group)
    async def user_stats(_, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("Please reply to a user or mention them: <code>/stats @username</code>", parse_mode="HTML")
        try:
            user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1])
            db = Database('group_manager.db')
            msg_count, warn_count, banned = get_user_stats(db, user.id, message.chat.id)
            await message.reply(
                f"<b>📊 Stats for {user.mention}</b><br><br>"
                f"Messages: {msg_count}<br>"
                f"Warnings: {warn_count}/3<br>"
                f"Banned: {'Yes' if banned else 'No'}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await message.reply("❌ Failed to fetch stats.", parse_mode="HTML")
