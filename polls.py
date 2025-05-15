from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database, save_poll, load_polls
from config import DEFAULT_WELCOME_IMAGE
from ui import create_keyboard
import logging
import re
import json
import asyncio
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

active_polls = {}

def register_poll_handlers(client: Client):
    db = Database('group_manager.db')
    global active_polls
    active_polls = load_polls(db)

    @client.on_message(filters.command("poll") & filters.group & admin_only())
    async def create_poll(_, message: Message):
        if len(message.command) < 4:
            return await message.reply("Usage: <code>/poll \"Question?\" option1 option2 [option3 ...] [timeout]</code>", parse_mode="HTML")
        try:
            content = ' '.join(message.command[1:])
            question_match = re.match(r'"([^"]+)"\s+(.+)', content)
            if not question_match:
                return await message.reply("❌ Invalid poll format: <code>/poll \"Question?\" option1 option2</code>", parse_mode="HTML")
            question, options_str = question_match.groups()
            parts = options_str.split()
            timeout = 60
            if parts[-1].endswith(('s', 'm', 'h')):
                try:
                    unit, value = parts[-1][-1], int(parts[-1][:-1])
                    timeout = value if unit == 's' else value * 60 if unit == 'm' else value * 3600
                    parts.pop(-1)
                except ValueError:
                    pass
            options = parts[:10]
            if len(options) < 2:
                return await message.reply("❌ At least two options required.", parse_mode="HTML")
            keyboard = create_keyboard([(f"{opt} (0)", f"vote_{i}_{message.id}", None) for i, opt in enumerate(options)])
            sent_msg = await message.reply_photo(
                photo=DEFAULT_WELCOME_IMAGE,
                caption=f"<b>📊 Poll</b>: {question}<br><br>Tap to vote:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            poll_data = {
                "chat_id": message.chat.id,
                "question": question,
                "options": options,
                "votes": defaultdict(int),
                "voters": set(),
                "created_at": time.time()
            }
            active_polls[sent_msg.id] = poll_data
            save_poll(db, sent_msg.id, poll_data)
            asyncio.create_task(end_poll_after_timeout(sent_msg.id, timeout))
        except Exception as e:
            logger.error(f"Poll creation error: {e}")
            await message.reply("❌ Failed to create poll.", parse_mode="HTML")

    @client.on_callback_query(filters.regex(r'^vote_\d+_\d+$'))
    async def handle_poll_vote(_, callback_query):
        parts = callback_query.data.split('_')
        option_index = int(parts[1])
        poll_msg_id = int(parts[2])
        if poll_msg_id not in active_polls:
            return await callback_query.answer("❌ This poll has ended.")
        poll = active_polls[poll_msg_id]
        user_id = callback_query.from_user.id
        if user_id in poll["voters"]:
            return await callback_query.answer("⚠️ You've already voted!")
        poll["votes"][option_index] += 1
        poll["voters"].add(user_id)
        save_poll(db, poll_msg_id, poll)
        keyboard = create_keyboard([(f"{opt} ({poll['votes'][i]})", f"vote_{i}_{poll_msg_id}", None) for i, opt in enumerate(poll["options"])])
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        await callback_query.answer("✅ Voted successfully!")

async def end_poll_after_timeout(msg_id, timeout):
    await asyncio.sleep(timeout)
    if msg_id not in active_polls:
        return
    poll = active_polls.pop(msg_id)
    results = "<br>".join([f"• {opt}: {poll['votes'][i]} vote(s)" for i, opt in enumerate(poll['options'])])
    max_vote = max(poll['votes'].values(), default=0)
    winners = [poll['options'][i] for i in poll['votes'] if poll['votes'][i] == max_vote]
    winner_text = ", ".join(winners) if winners else "No votes"
    try:
        db = Database('group_manager.db')
        await bot_client.send_message(
            poll['chat_id'],
            f"🏁 Poll ended! Winner(s): <b>{winner_text}</b><br><br>Results:<br>{results}",
            parse_mode="HTML"
        )
        db.execute("DELETE FROM polls WHERE msg_id=?", (msg_id,))
    except Exception as e:
        logger.error(f"Poll end error: {e}")
