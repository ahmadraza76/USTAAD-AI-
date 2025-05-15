import re
import aiohttp
import asyncio
import logging
from config import DEEPSEEK_API_KEY

logger = logging.getLogger(__name__)

api_semaphore = asyncio.Semaphore(5)

async def ask_deepseek(question):
    async with api_semaphore:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500,
            "temperature": 0.7
        }
        try:
            async with aiohttp.ClientSession().post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"DeepSeek API success: {question[:50]}...")
                    return data['choices'][0]['message']['content'].strip()
                logger.error(f"DeepSeek API status {response.status}")
                return "Sorry, I couldn't process your question."
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return "AI service error."

async def is_toxic_message(message_text):
    prompt = f"Is the following text toxic, inappropriate, or offensive? Respond with 'Yes' or 'No':\n{message_text}"
    response = await ask_deepseek(prompt)
    return response.strip().lower() == "yes"

async def generate_welcome_message(username):
    prompt = f"Generate a friendly, casual welcome message in Hindi for a user named {username}. Include a fun tone and emojis."
    return await ask_deepseek(prompt)

def is_hindi(text):
    return bool(re.search(r'[\u0900-\u097F]', text))

def humanize_text(text):
    text = text.strip()
    if not text:
        return "अरे, तुमने कुछ कहा ही नहीं! 😅" if is_hindi(text) else "Hey, you didn't say anything! 😅"
    replacements = {
        r'\bI Ascending': 'I\'m',
        r'\bwill not\b': 'won\'t',
        r'\bcan not\b': 'can\'t',
        r'\bplease\b': 'pretty please',
        r'\btherefore\b': 'so',
        r'\bhowever\b': 'but',
        r'\bcommence\b': 'start',
        r'\bterminate\b': 'end',
        r'\butilize\b': 'use',
        r'\bregarding\b': 'about',
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    if len(text.split()) > 10:
        text = f"You know, {text.lower()[0]}{text[1:]}"
    elif len(text.split()) > 5:
        text = f"Like, {text.lower()[0]}{text[1:]}"
    if not text.endswith('!') and not text.endswith('?'):
        text += ", alright?"
    text = text[0].upper() + text[1:]
    return text

def sanitize_input(text, max_length=500):
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    return re.sub(r'[^\w\s.,!?@]', '', text)
