import sqlite3
import logging
from threading import Lock
import atexit
from datetime import datetime
import json
from config import DEFAULT_WELCOME_IMAGE

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = Lock()
        self.init_tables()
        atexit.register(self.close)

    def init_tables(self):
        with self.lock:
            try:
                c = self.conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS welcome_messages (
                             chat_id INTEGER PRIMARY KEY,
                             message TEXT,
                             image_url TEXT DEFAULT ?)''', (DEFAULT_WELCOME_IMAGE,))
                c.execute('''CREATE TABLE IF NOT EXISTS goodbye_messages (
                             chat_id INTEGER PRIMARY KEY,
                             message TEXT)''')
                c.execute('''CREATE TABLE IF NOT EXISTS welcome_toggles (
                             chat_id INTEGER PRIMARY KEY,
                             enabled BOOLEAN DEFAULT 1)''')
                c.execute('''CREATE TABLE IF NOT EXISTS goodbye_toggles (
                             chat_id INTEGER PRIMARY KEY,
                             enabled BOOLEAN DEFAULT 1)''')
                c.execute('''CREATE TABLE IF NOT EXISTS auto_replies (
                             chat_id INTEGER,
                             trigger TEXT,
                             response TEXT,
                             PRIMARY KEY (chat_id, trigger))''')
                c.execute('''CREATE TABLE IF NOT EXISTS warnings (
                             chat_id INTEGER,
                             user_id INTEGER,
                             count INTEGER DEFAULT 0,
                             last_warn TIMESTAMP,
                             banned BOOLEAN DEFAULT 0,
                             PRIMARY KEY (chat_id, user_id))''')
                c.execute('''CREATE TABLE IF NOT EXISTS auto_management (
                             chat_id INTEGER PRIMARY KEY,
                             enabled BOOLEAN DEFAULT 1)''')
                c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
                             chat_id INTEGER,
                             user_id INTEGER,
                             message_count INTEGER DEFAULT 0,
                             PRIMARY KEY (chat_id, user_id))''')
                c.execute('''CREATE TABLE IF NOT EXISTS verified_users (
                             chat_id INTEGER,
                             user_id INTEGER,
                             PRIMARY KEY (chat_id, user_id))''')
                c.execute('''CREATE TABLE IF NOT EXISTS polls (
                             msg_id INTEGER PRIMARY KEY,
                             chat_id INTEGER,
                             question TEXT,
                             options TEXT,
                             votes TEXT,
                             voters TEXT,
                             created_at REAL)''')
                self.conn.commit()
                logger.info("Database tables initialized")
            except sqlite3.Error as e:
                logger.error(f"Database initialization error: {e}")
                raise

    def execute(self, query, params=()):
        with self.lock:
            try:
                c = self.conn.cursor()
                c.execute(query, params)
                self.conn.commit()
                return c
            except sqlite3.Error as e:
                logger.error(f"Database error: {query} - {e}")
                return None

    def fetchone(self, query, params=()):
        c = self.execute(query, params)
        return c.fetchone() if c else None

    def fetchall(self, query, params=()):
        c = self.execute(query, params)
        return c.fetchall() if c else []

    def close(self):
        with self.lock:
            self.conn.close()
            logger.info("Database connection closed")

# Database Functions
def get_welcome_message(db, chat_id):
    res = db.fetchone("SELECT message, image_url FROM welcome_messages WHERE chat_id=?", (chat_id,))
    return (res['message'], res['image_url']) if res else (None, DEFAULT_WELCOME_IMAGE)

def set_welcome_message(db, chat_id, msg, image_url=None):
    db.execute("INSERT OR REPLACE INTO welcome_messages VALUES (?, ?, ?)", (chat_id, msg, image_url or DEFAULT_WELCOME_IMAGE))

def delete_welcome_message(db, chat_id):
    db.execute("DELETE FROM welcome_messages WHERE chat_id=?", (chat_id,))

def get_goodbye_message(db, chat_id):
    res = db.fetchone("SELECT message FROM goodbye_messages WHERE chat_id=?", (chat_id,))
    return res['message'] if res else None

def set_goodbye_message(db, chat_id, msg):
    db.execute("INSERT OR REPLACE INTO goodbye_messages VALUES (?, ?)", (chat_id, msg))

def delete_goodbye_message(db, chat_id):
    db.execute("DELETE FROM goodbye_messages WHERE chat_id=?", (chat_id,))

def toggle_welcome(db, chat_id, status):
    db.execute("INSERT OR REPLACE INTO welcome_toggles VALUES (?, ?)", (chat_id, status))

def is_welcome_enabled(db, chat_id):
    res = db.fetchone("SELECT enabled FROM welcome_toggles WHERE chat_id=?", (chat_id,))
    return bool(res['enabled']) if res else True

def toggle_goodbye(db, chat_id, status):
    db.execute("INSERT OR REPLACE INTO goodbye_toggles VALUES (?, ?)", (chat_id, status))

def is_goodbye_enabled(db, chat_id):
    res = db.fetchone("SELECT enabled FROM goodbye_toggles WHERE chat_id=?", (chat_id,))
    return bool(res['enabled']) if res else True

def toggle_auto_management(db, chat_id, status):
    db.execute("INSERT OR REPLACE INTO auto_management VALUES (?, ?)", (chat_id, status))

def is_auto_management_enabled(db, chat_id):
    res = db.fetchone("SELECT enabled FROM auto_management WHERE chat_id=?", (chat_id,))
    return bool(res['enabled']) if res else True

def add_warning(db, user_id, chat_id, reason):
    res = db.fetchone("SELECT count, banned FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    count = res['count'] + 1 if res else 1
    banned = res['banned'] if res else False
    db.execute("INSERT OR REPLACE INTO warnings VALUES (?, ?, ?, ?, ?)", (chat_id, user_id, count, datetime.now(), banned))
    return count, banned

def set_ban_status(db, user_id, chat_id, banned):
    res = db.fetchone("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    count = res['count'] if res else 0
    db.execute("INSERT OR REPLACE INTO warnings VALUES (?, ?, ?, ?, ?)", (chat_id, user_id, count, datetime.now(), banned))

def increment_message_count(db, user_id, chat_id):
    res = db.fetchone("SELECT message_count FROM user_stats WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    count = res['message_count'] + 1 if res else 1
    db.execute("INSERT OR REPLACE INTO user_stats VALUES (?, ?, ?)", (chat_id, user_id, count))
    return count

def get_user_stats(db, user_id, chat_id):
    msg_res = db.fetchone("SELECT message_count FROM user_stats WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    warn_res = db.fetchone("SELECT count, banned FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    message_count = msg_res['message_count'] if msg_res else 0
    warn_count = warn_res['count'] if warn_res else 0
    banned = bool(warn_res['banned']) if warn_res else False
    return message_count, warn_count, banned

def add_verified_user(db, user_id, chat_id):
    db.execute("INSERT OR REPLACE INTO verified_users VALUES (?, ?)", (chat_id, user_id))

def is_verified_user(db, user_id, chat_id):
    res = db.fetchone("SELECT 1 FROM verified_users WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    return bool(res)

def get_auto_replies(db, chat_id):
    replies = db.fetchall("SELECT trigger, response FROM auto_replies WHERE chat_id=?", (chat_id,))
    return {row['trigger']: row['response'] for row in replies}

def add_auto_reply(db, chat_id, trigger, response):
    db.execute("INSERT OR REPLACE INTO auto_replies VALUES (?, ?, ?)", (chat_id, trigger.lower(), response))

def remove_auto_reply(db, chat_id, trigger):
    db.execute("DELETE FROM auto_replies WHERE chat_id=? AND trigger=?", (chat_id, trigger.lower()))

def save_poll(db, msg_id, poll_data):
    db.execute("INSERT OR REPLACE INTO polls VALUES (?, ?, ?, ?, ?, ?, ?)",
               (msg_id, poll_data['chat_id'], poll_data['question'], json.dumps(poll_data['options']),
                json.dumps(dict(poll_data['votes'])), json.dumps(list(poll_data['voters'])), poll_data['created_at']))

def load_polls(db):
    polls = db.fetchall("SELECT * FROM polls")
    return {
        poll['msg_id']: {
            'chat_id': poll['chat_id'],
            'question': poll['question'],
            'options': json.loads(poll['options']),
            'votes': defaultdict(int, json.loads(poll['votes'])),
            'voters': set(json.loads(poll['voters'])),
            'created_at': poll['created_at']
        } for poll in polls
    }
