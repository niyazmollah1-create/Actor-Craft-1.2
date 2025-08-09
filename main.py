import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os
from database import db
from config import *
from utils.gemini_client import gemini_client
from utils.helpers import helpers

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot intents
intents = discord.Intents.all()
intents.message_content = True

class GeminiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=DEFAULT_PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.start_time = discord.utils.utcnow()
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        # Initialize database
        await db.init_database()
        
        # Load all cogs
        cogs_to_load = [
            'cogs.ai_personality',
            'cogs.core_general',
            'cogs.moderation',
            'cogs.fun_engagement', 
            'cogs.utility_info',
            'cogs.server_management',
            'cogs.music',
            'cogs.image_manipulation',
            'cogs.economy'  # New economy system
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logging.info(f"Loaded cog: {cog}")
            except Exception as e:
                logging.error(f"Failed to load cog {cog}: {e}")
        
        # Sync slash commands globally
        try:
            synced = await self.tree.sync()
            logging.info(f"Synced {len(synced)} slash commands globally")
        except Exception as e:
            logging.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logging.info(f'{self.user} has connected to Discord!')
        logging.info(f'Connected to {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(type=discord.ActivityType.watching, name="for !ehelp | Token Economy")
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Process commands
        await self.process_commands(message)

# Create bot instance
bot = GeminiBot()

if __name__ == "__main__":
    # Get bot token
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logging.error("DISCORD_BOT_TOKEN environment variable not found!")
        logging.error("Please set your bot token in the environment variables or .env file")
    else:
        try:
            bot.run(token)
        except discord.LoginFailure:
            logging.error("Invalid bot token provided!")
        except Exception as e:
            logging.error(f"Failed to run bot: {e}")