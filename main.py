import os
import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from keep_alive import keep_alive
from database import Database
from commands import register_command_handlers
from ui import register_callback_handlers
from moderation import register_moderation_handlers
from polls import register_poll_handlers

logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

db = Database('group_manager.db')

bot_client = Client(
    name="ustaad_ai_group_manager",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=False
)

async def init_bot():
    logger.info("Bot initialized")

async def shutdown_bot():
    db.close()
    logger.info("Bot shut down")

bot_client.on_startup(init_bot)
bot_client.on_shutdown(shutdown_bot)

register_command_handlers(bot_client)
register_callback_handlers(bot_client)
register_moderation_handlers(bot_client)
register_poll_handlers(bot_client)

if __name__ == "__main__":
    keep_alive()
    logger.info("Starting Ustaad AI Group Manager...")
    bot_client.run()
