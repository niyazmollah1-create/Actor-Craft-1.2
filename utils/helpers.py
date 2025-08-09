import discord
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import random
import re
from config import *

class Helpers:
    @staticmethod
    def create_embed(title, description, color=BOT_COLOR, fields=None, footer=None, thumbnail=None, image=None):
        """Create a formatted embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', 'Field'),
                    value=field.get('value', 'Value'),
                    inline=field.get('inline', False)
                )
        
        if footer:
            embed.set_footer(text=footer)
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        return embed
    
    @staticmethod
    def format_time(seconds):
        """Format seconds into readable time"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m {seconds % 60}s"
    
    @staticmethod
    def parse_time(time_str):
        """Parse time string (e.g., '1h30m', '45s', '2d') into seconds"""
        if not time_str:
            return 0
        
        time_regex = re.compile(r'(\d+)([smhdw])')
        matches = time_regex.findall(time_str.lower())
        
        total_seconds = 0
        for amount, unit in matches:
            amount = int(amount)
            if unit == 's':
                total_seconds += amount
            elif unit == 'm':
                total_seconds += amount * 60
            elif unit == 'h':
                total_seconds += amount * 3600
            elif unit == 'd':
                total_seconds += amount * 86400
            elif unit == 'w':
                total_seconds += amount * 604800
        
        return total_seconds
    
    @staticmethod
    async def fetch_json(url, headers=None):
        """Fetch JSON data from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    @staticmethod
    async def fetch_image(url):
        """Fetch image bytes from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    return None
        except Exception as e:
            print(f"Error fetching image {url}: {e}")
            return None
    
    @staticmethod
    def get_random_color():
        """Get random hex color"""
        return random.randint(0, 0xffffff)
    
    @staticmethod
    def clean_content(content, max_length=2000):
        """Clean and truncate content for Discord"""
        if len(content) > max_length:
            return content[:max_length-3] + "..."
        return content
    
    @staticmethod
    def format_currency(amount):
        """Format currency amount"""
        return f"💰 {amount:,} coins"
    
    @staticmethod
    async def send_dm_safe(user, content=None, embed=None):
        """Safely send DM to user"""
        try:
            if embed:
                await user.send(embed=embed)
            else:
                await user.send(content)
            return True
        except discord.Forbidden:
            return False
        except Exception:
            return False
    
    @staticmethod
    def has_permission(member, permission):
        """Check if member has specific permission"""
        return getattr(member.guild_permissions, permission, False)
    
    @staticmethod
    def get_member_status_emoji(member):
        """Get emoji for member status"""
        status_emojis = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡",
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        return status_emojis.get(member.status, "⚫")
    
    @staticmethod
    async def confirm_action(ctx, message, timeout=30):
        """Ask for confirmation with reactions"""
        embed = Helpers.create_embed("Confirmation", message, color=0xffaa00)
        confirm_msg = await ctx.send(embed=embed)
        
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")
        
        def check(reaction, user):
            return (user == ctx.author and 
                   str(reaction.emoji) in ["✅", "❌"] and 
                   reaction.message.id == confirm_msg.id)
        
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=timeout, check=check)
            await confirm_msg.delete()
            return str(reaction.emoji) == "✅"
        except asyncio.TimeoutError:
            await confirm_msg.delete()
            return False

# Global helpers instance
helpers = Helpers()
