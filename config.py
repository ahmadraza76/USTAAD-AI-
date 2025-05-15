import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot Credentials
try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_USERNAME = os.getenv("BOT_USERNAME")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
except (TypeError, ValueError) as e:
    logger.error(f"Environment variable error: {e}")
    raise SystemExit("Missing or invalid environment variables. Check .env file.")

# Image URLs
DEFAULT_WELCOME_IMAGE = "https://graph.org/file/a00fd3a852b79eb8f17e8-68ab656cb3a31269fe.jpg"
MAIN_MENU_IMG = DEFAULT_WELCOME_IMAGE

# Command Categories
COMMAND_DETAILS = {
    "admin_management": {
        "title": "ADMIN MANAGEMENT",
        "description": "Manage user roles and permissions",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/promote @user - Promote a user to admin",
            "/demote @user - Remove admin rights",
            "/ban @user - Ban a user from the group",
            "/unban @user - Unban a user",
            "/verify @user - Verify a user for special permissions"
        ]
    },
    "user_controls": {
        "title": "USER CONTROLS",
        "description": "Control group member actions",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/kick @user - Kick a user from the group",
            "/mute @user [duration] - Mute a user (e.g., 24h)",
            "/unmute @user - Unmute a user",
            "/ro @user [duration] - Set read-only mode (e.g., 1h)",
            "/unro @user - Remove read-only restriction",
            "/warn @user [reason] - Issue a warning"
        ]
    },
    "message_controls": {
        "title": "MESSAGE CONTROLS",
        "description": "Manage group messages",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/pin [reply] - Pin a message",
            "/unpin [reply] - Unpin a message",
            "/del [reply] - Delete a message",
            "/purge N - Delete last N messages",
            "/clean - Remove bot messages or spam"
        ]
    },
    "welcome_goodbye": {
        "title": "WELCOME/GOODBYE",
        "description": "Set up greeting messages",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/setwelcome [text] - Set custom welcome message",
            "/delwelcome - Delete welcome message",
            "/setgoodbye [text] - Set custom goodbye message",
            "/delgoodbye - Delete goodbye message",
            "/welcome on/off - Toggle welcome messages",
            "/goodbye on/off - Toggle goodbye messages",
            "/setwelcomeimage [url] - Set welcome image"
        ]
    },
    "automation": {
        "title": "AUTOMATION",
        "description": "Automate group tasks and replies",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/filter word response - Add auto-reply for a word",
            "/stop word - Remove auto-reply",
            "/filters - List active auto-replies",
            "/toggleauto on/off - Toggle automatic management"
        ]
    },
    "info_commands": {
        "title": "INFO COMMANDS",
        "description": "Get group and user information",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/id - Show user/chat ID",
            "/userinfo @user - Show user details",
            "/chatinfo - Show group details",
            "/admins - List group admins",
            "/stats @user - Show user activity and warnings"
        ]
    },
    "ai_features": {
        "title": "AI FEATURES",
        "description": "Interact with AI-powered tools",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/ask [question] - Ask AI a question",
            "/humanize [text] - Make text conversational"
        ]
    },
    "poll_system": {
        "title": "POLL SYSTEM",
        "description": "Create and manage polls in the group",
        "image": DEFAULT_WELCOME_IMAGE,
        "commands": [
            "/poll \"Question?\" option1 option2 [option3 ...] [timeout] - Create a poll (e.g., 5m)"
        ]
    }
}
