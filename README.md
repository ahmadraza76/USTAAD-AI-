# USTAAD-AI- Ustaad AI - Advanced Telegram Group Management Bot
Ustaad AI is a powerful Telegram bot built with Pyrogram and integrated with DeepSeek AI for advanced group management, AI-powered conversations, and text humanization. It offers a modular, extensible architecture with a rich set of features for Telegram group administrators and users.

Table of Contents

Features
Installation
Configuration
Commands
Directory Structure
Usage
Testing
Contributing
License
Contact


Features
Ustaad AI provides a comprehensive suite of tools for Telegram group management and AI interactions:

Group Management:

Promote/demote admins, ban/unban users, mute/unmute, and set read-only restrictions.
Automated welcome/goodbye messages with customizable text and images.
Auto-replies for specific keywords and spam/flood detection.
Warning system with automatic bans after 3 warnings.
User verification for special permissions.


AI Integration:

Powered by DeepSeek AI for answering questions (/ask).
Text humanization to make formal text conversational (/humanize).
Language detection (Hindi/English) for tailored responses.


Message Controls:

Pin/unpin messages, delete messages, purge recent messages, and clean spam/bot messages.
Auto-moderation to detect and remove toxic/inappropriate content.


Poll System:

Create polls with multiple options and customizable timeouts.
Real-time vote tracking and automatic result announcement.


User Interface (UI/UX):

Interactive inline keyboards for easy navigation.
Categorized help menus with detailed command descriptions.
Visually appealing welcome messages with images.


Analytics:

Track user message counts, warnings, and ban status.
Display group and user information (/chatinfo, /userinfo).


Reliability:

Flask-based keep-alive server to ensure continuous operation.
SQLite database for persistent storage of settings and user data.
Comprehensive logging for debugging and monitoring.




Installation
Prerequisites

Python 3.8 or higher
Telegram Bot Token
DeepSeek API Key
SQLite (included with Python)

Steps

Clone the Repository:
git clone https://github.com/your-username/ustaad-ai.git
cd ustaad-ai


Install Dependencies:
pip install -r requirements.txt


Set Up Environment Variables:

Copy the .env.example file to .env:
cp .env.example .env


Edit .env with your credentials:
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_USERNAME=@YourBotUsername
DEEPSEEK_API_KEY=your_deepseek_key




Run the Bot:
python main.py




Configuration

Database: The bot uses SQLite (group_manager.db) to store group settings, user stats, warnings, and polls.
Logging: Logs are saved to bot.log for debugging and monitoring.
Customization:
Edit config.py to modify COMMAND_DETAILS, default images, or other settings.
Set custom welcome/goodbye messages using /setwelcome and /setgoodbye.




Commands
Ustaad AI organizes commands into categories for easy access. Use the /start command in private chat to explore the interactive menu.
Admin Management



Command
Description



/promote @user
Promote a user to admin with permissions


/demote @user
Remove admin rights


/ban @user
Ban a user from the group


/unban @user
Unban a user


/verify @user
Verify a user for special permissions


User Controls



Command
Description



/kick @user
Kick a user from the group


/mute @user [duration]
Mute a user (e.g., 24h)


/unmute @user
Unmute a user


/ro @user [duration]
Set read-only mode (e.g., 1h)


/unro @user
Remove read-only restriction


/warn @user [reason]
Issue a warning (3 warnings = ban)


Message Controls



Command
Description



/pin [reply]
Pin a message


/unpin [reply]
Unpin a message


/del [reply]
Delete a message


/purge N
Delete last N messages (max 100)


/clean
Remove bot messages or spam


Welcome/Goodbye



Command
Description



/setwelcome [text]
Set custom welcome message (supports {name})


/delwelcome
Delete welcome message


/setgoodbye [text]
Set custom goodbye message


/delgoodbye
Delete goodbye message


/welcome on/off
Toggle welcome messages


/goodbye on/off
Toggle goodbye messages


/setwelcomeimage [url]
Set welcome image URL


Automation



Command
Description



/filter word response
Add auto-reply for a word


/stop word
Remove auto-reply


/filters
List active auto-replies


/toggleauto on/off
Toggle automatic management


Info Commands



Command
Description



/id
Show user/chat ID


/userinfo @user
Show user details (messages, warnings, etc.)


/chatinfo
Show group details


/admins
List group admins


/stats @user
Show user activity and warnings


AI Features



Command
Description



/ask [question]
Ask DeepSeek AI a question


/humanize [text]
Make text conversational


Poll System



Command
Description



/poll "Question?" option1 option2 [option3 ...] [timeout]
Create a poll (e.g., /poll "Best color?" Red Blue 5m)



Directory Structure
ustaad-ai/
├── main.py              # Main entry point and bot startup
├── config.py           # Configuration and command details
├── database.py         # SQLite database operations
├── commands.py         # Command handlers
├── ui.py               # UI/UX (keyboards, callbacks)
├── ai.py               # DeepSeek AI and text processing
├── moderation.py       # Auto-moderation and warnings
├── polls.py            # Poll system
├── keep_alive.py       # Flask keep-alive server
├── tests.py            # Unit tests
├── requirements.txt    # Dependencies
├── .env.example        # Environment variables template
├── bot.log             # Log file (generated)
├── group_manager.db    # SQLite database (generated)


Usage

Start the Bot:

Run python main.py to start the bot.
Check bot.log for startup messages.


Interact in Telegram:

In private chat, use /start to access the main menu.
In groups, add the bot and use commands like /promote, /ask, or /poll.
Admins can configure settings using /setwelcome, /filter, etc.


Monitor Activity:

Use /userinfo and /stats to track user activity.
Check bot.log for errors or moderation actions.




Testing
The bot includes unit tests to ensure reliability.
Running Tests
python -m unittest tests.py

Manual Testing

Setup:

Ensure .env is configured and dependencies are installed.
Start the bot with python main.py.


Test Cases:

Main Menu: Send /start in private chat. Verify all buttons (INFO, HELP, AI Chat) appear.
Help Menu: Click "HELP" and check all command categories.
AI Features:
Run /ask What is a solar eclipse? and verify a response from DeepSeek AI.
Run /humanize I am commencing the utilization of this bot. and check for conversational output.


Group Management:
In a test group, use /promote @user, /ban @user, and /warn @user.
Verify warnings are tracked (/stats @user) and bans are enforced after 3 warnings.


Welcome/Goodbye:
Set a welcome message with /setwelcome Welcome {name}! and add a new member to test.
Toggle welcome messages with /welcome off and verify they stop.


Polls:
Create a poll with /poll "Favorite color?" Red Blue 10s and vote using buttons.
Verify results are posted after the timeout.


Auto-Moderation:
Send a toxic message (e.g., inappropriate text) and check if it’s deleted with a warning.
Test flood detection by sending multiple messages quickly.




Logs:

Check bot.log for errors or unexpected behavior.




Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make changes and commit (git commit -m "Add your feature").
Push to your branch (git push origin feature/your-feature).
Open a Pull Request.

Please ensure your code follows the existing style and includes tests.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact

Developer: @Mrnick66
Telegram: Contact Developer
Issues: GitHub Issues

For custom bot development or support, reach out via Telegram.

Powered by Ustaad AIBuilt with ❤️ using Pyrogram and DeepSeek AI
