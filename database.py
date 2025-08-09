import aiosqlite
import json
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    async def init_database(self):
        """Initialize all database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Auto-reply triggers table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    trigger_word TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User economy table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS economy (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    balance INTEGER DEFAULT 0,
                    daily_last TIMESTAMP,
                    total_earned INTEGER DEFAULT 0
                )
            ''')
            
            # User warnings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    reason TEXT,
                    moderator_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    guild_id INTEGER,
                    setting_key TEXT,
                    setting_value TEXT,
                    PRIMARY KEY (guild_id, setting_key)
                )
            ''')
            
            # AI training data table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ai_training (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    message TEXT,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # DM logs table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS dm_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER,
                    recipient_id INTEGER,
                    message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Music queue table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS music_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    url TEXT,
                    title TEXT,
                    requested_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
    
    # Trigger methods
    async def add_trigger(self, guild_id, trigger_word, response, created_by):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO triggers (guild_id, trigger_word, response, created_by) VALUES (?, ?, ?, ?)',
                (guild_id, trigger_word.lower(), response, created_by)
            )
            await db.commit()
    
    async def get_triggers(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT trigger_word, response FROM triggers WHERE guild_id = ?',
                (guild_id,)
            )
            return await cursor.fetchall()
    
    async def remove_trigger(self, guild_id, trigger_word):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'DELETE FROM triggers WHERE guild_id = ? AND trigger_word = ?',
                (guild_id, trigger_word.lower())
            )
            await db.commit()
            return cursor.rowcount > 0
    
    # Economy methods
    async def get_balance(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT balance FROM economy WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def update_balance(self, user_id, guild_id, amount):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO economy (user_id, guild_id, balance, total_earned)
                VALUES (?, ?, 
                    COALESCE((SELECT balance FROM economy WHERE user_id = ? AND guild_id = ?), 0) + ?,
                    COALESCE((SELECT total_earned FROM economy WHERE user_id = ? AND guild_id = ?), 0) + ?)
            ''', (user_id, guild_id, user_id, guild_id, amount, user_id, guild_id, max(0, amount)))
            await db.commit()
    
    async def can_daily(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT daily_last FROM economy WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            )
            result = await cursor.fetchone()
            if not result or not result[0]:
                return True
            
            last_daily = datetime.fromisoformat(result[0])
            now = datetime.now()
            return (now - last_daily).days >= 1
    
    async def update_daily(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO economy (user_id, guild_id, balance, daily_last, total_earned)
                VALUES (?, ?, 
                    COALESCE((SELECT balance FROM economy WHERE user_id = ? AND guild_id = ?), 0) + 100,
                    ?, 
                    COALESCE((SELECT total_earned FROM economy WHERE user_id = ? AND guild_id = ?), 0) + 100)
            ''', (user_id, guild_id, user_id, guild_id, datetime.now().isoformat(), user_id, guild_id))
            await db.commit()
    
    # Warning methods
    async def add_warning(self, user_id, guild_id, reason, moderator_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO warnings (user_id, guild_id, reason, moderator_id) VALUES (?, ?, ?, ?)',
                (user_id, guild_id, reason, moderator_id)
            )
            await db.commit()
    
    async def get_warnings(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT reason, moderator_id, created_at FROM warnings WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            )
            return await cursor.fetchall()
    
    async def clear_warnings(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM warnings WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            )
            await db.commit()
    
    # Settings methods
    async def get_setting(self, guild_id, key):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT setting_value FROM settings WHERE guild_id = ? AND setting_key = ?',
                (guild_id, key)
            )
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async def set_setting(self, guild_id, key, value):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO settings (guild_id, setting_key, setting_value) VALUES (?, ?, ?)',
                (guild_id, key, str(value))
            )
            await db.commit()
    
    # AI training methods
    async def add_training_data(self, user_id, guild_id, message, response):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO ai_training (user_id, guild_id, message, response) VALUES (?, ?, ?, ?)',
                (user_id, guild_id, message, response)
            )
            await db.commit()
    
    async def get_training_data(self, guild_id, limit=100):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT message, response FROM ai_training WHERE guild_id = ? ORDER BY created_at DESC LIMIT ?',
                (guild_id, limit)
            )
            return await cursor.fetchall()
    
    # DM log methods
    async def log_dm(self, sender_id, recipient_id, message):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO dm_logs (sender_id, recipient_id, message) VALUES (?, ?, ?)',
                (sender_id, recipient_id, message)
            )
            await db.commit()

# Global database instance
db = Database()
