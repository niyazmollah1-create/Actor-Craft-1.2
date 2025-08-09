import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiohttp
import wikipedia
from datetime import datetime, timedelta
from github import Github
# Translation functionality using Gemini AI instead of googletrans
from utils.helpers import helpers
from database import db
from config import *

class UtilityInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Using Gemini AI for translation instead of googletrans
        self.github = Github(GITHUB_TOKEN)
        self.reminders = {}
    
    @app_commands.command(name="avatar", description="View user's avatar")
    @app_commands.describe(user="User to get avatar from")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        embed = helpers.create_embed(
            f"🖼️ {target.display_name}'s Avatar",
            f"[Download Link]({target.avatar.url})" if target.avatar else "No avatar set",
            color=BOT_COLOR
        )
        
        if target.avatar:
            embed.set_image(url=target.avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="banner", description="View user's banner")
    @app_commands.describe(user="User to get banner from")
    async def banner(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        # Fetch full user data to get banner
        try:
            full_user = await self.bot.fetch_user(target.id)
            
            if full_user.banner:
                embed = helpers.create_embed(
                    f"🎨 {target.display_name}'s Banner",
                    f"[Download Link]({full_user.banner.url})",
                    color=BOT_COLOR
                )
                embed.set_image(url=full_user.banner.url)
            else:
                embed = helpers.create_embed(
                    f"🎨 {target.display_name}'s Banner",
                    "This user doesn't have a banner set.",
                    color=BOT_COLOR
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message("❌ Could not fetch user banner.", ephemeral=True)
    
    @app_commands.command(name="remindme", description="Set a reminder")
    @app_commands.describe(time="Time until reminder (e.g., 10m, 1h, 2d)", message="Reminder message")
    async def remindme(self, interaction: discord.Interaction, time: str, message: str):
        # Parse time
        reminder_seconds = helpers.parse_time(time)
        if reminder_seconds == 0:
            await interaction.response.send_message("❌ Invalid time format. Use formats like: 10m, 1h, 2d", ephemeral=True)
            return
        
        if reminder_seconds > 2592000:  # 30 days max
            await interaction.response.send_message("❌ Maximum reminder time is 30 days.", ephemeral=True)
            return
        
        # Set reminder
        reminder_time = datetime.utcnow() + timedelta(seconds=reminder_seconds)
        
        embed = helpers.create_embed(
            "⏰ Reminder Set",
            f"I'll remind you in **{time}** about:\n{message}",
            color=0x00FF00
        )
        embed.add_field(
            name="Reminder Time",
            value=f"<t:{int(reminder_time.timestamp())}:F>",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Wait for reminder time
        await asyncio.sleep(reminder_seconds)
        
        # Send reminder
        reminder_embed = helpers.create_embed(
            "⏰ Reminder",
            f"You asked me to remind you about:\n**{message}**",
            color=0xFFAA00
        )
        
        try:
            await interaction.user.send(embed=reminder_embed)
        except discord.Forbidden:
            # If DM fails, try to send in the channel
            try:
                await interaction.channel.send(f"{interaction.user.mention}", embed=reminder_embed)
            except:
                pass
    
    @app_commands.command(name="weather", description="Get weather information for a location")
    @app_commands.describe(location="City name or location")
    async def weather(self, interaction: discord.Interaction, location: str):
        await interaction.response.defer()
        
        try:
            # OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        temp = data['main']['temp']
                        feels_like = data['main']['feels_like']
                        humidity = data['main']['humidity']
                        description = data['weather'][0]['description'].title()
                        city = data['name']
                        country = data['sys']['country']
                        
                        embed = helpers.create_embed(
                            f"🌤️ Weather in {city}, {country}",
                            f"**{description}**",
                            color=0x87CEEB
                        )
                        
                        embed.add_field(
                            name="🌡️ Temperature",
                            value=f"{temp}°C (feels like {feels_like}°C)",
                            inline=True
                        )
                        embed.add_field(
                            name="💧 Humidity",
                            value=f"{humidity}%",
                            inline=True
                        )
                        
                        await interaction.followup.send(embed=embed)
                        
                    elif response.status == 404:
                        await interaction.followup.send("❌ Location not found. Please check the spelling and try again.")
                    else:
                        await interaction.followup.send("❌ Could not fetch weather data. Please try again later.")
                        
        except Exception as e:
            await interaction.followup.send("❌ Failed to get weather information.")
    
    @app_commands.command(name="translate", description="Translate text to another language")
    @app_commands.describe(language="Target language (e.g., 'Spanish', 'French', 'German')", text="Text to translate")
    async def translate(self, interaction: discord.Interaction, language: str, text: str):
        await interaction.response.defer()
        
        try:
            # Use Gemini AI for translation
            from utils.gemini_client import gemini_client
            
            prompt = f"Translate the following text to {language}. Only respond with the translation, no additional text:\n\n{text}"
            translation = await gemini_client.generate_response(prompt)
            
            embed = helpers.create_embed(
                "🌐 Translation",
                f"**Original:** {text}\n**Translated to {language}:** {translation}",
                color=0x0099FF
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send("❌ Translation failed. Please try again.")
    
    @app_commands.command(name="time", description="Get current time for a location")
    @app_commands.describe(location="City or timezone")
    async def time(self, interaction: discord.Interaction, location: str):
        # This is a simplified version - you'd want to use a proper timezone API
        embed = helpers.create_embed(
            f"🕐 Current Time",
            f"**Location:** {location}\n**UTC Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            color=0x4A90E2
        )
        embed.add_field(
            name="Note",
            value="This shows UTC time. For accurate local time, use a timezone-specific service.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="define", description="Get dictionary definition of a word")
    @app_commands.describe(word="Word to define")
    async def define(self, interaction: discord.Interaction, word: str):
        await interaction.response.defer()
        
        try:
            # Using a dictionary API (you'd want to implement with a real dictionary API)
            embed = helpers.create_embed(
                f"📖 Definition: {word.title()}",
                "Dictionary lookup functionality would be implemented here with a proper dictionary API.",
                color=0x8B4513
            )
            embed.add_field(
                name="Note",
                value="This is a placeholder. In a full implementation, this would connect to a dictionary API.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send("❌ Could not find definition for that word.")
    
    @app_commands.command(name="urban", description="Urban Dictionary search")
    @app_commands.describe(word="Word to search")
    async def urban(self, interaction: discord.Interaction, word: str):
        await interaction.response.defer()
        
        try:
            # Urban Dictionary API (unofficial)
            url = f"https://api.urbandictionary.com/v0/define?term={word}"
            data = await helpers.fetch_json(url)
            
            if data and 'list' in data and len(data['list']) > 0:
                definition = data['list'][0]
                
                embed = helpers.create_embed(
                    f"🏙️ Urban Dictionary: {word.title()}",
                    helpers.clean_content(definition['definition'], 1500),
                    color=0xFF4500
                )
                
                if definition.get('example'):
                    embed.add_field(
                        name="Example",
                        value=helpers.clean_content(definition['example'], 500),
                        inline=False
                    )
                
                embed.add_field(
                    name="Votes",
                    value=f"👍 {definition.get('thumbs_up', 0)} | 👎 {definition.get('thumbs_down', 0)}",
                    inline=True
                )
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ No definitions found for that term.")
                
        except Exception as e:
            await interaction.followup.send("❌ Could not search Urban Dictionary.")
    
    @app_commands.command(name="youtube", description="Search YouTube and get video recommendations")
    @app_commands.describe(query="What to search for on YouTube")
    async def youtube_search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        
        try:
            # Use Gemini AI to provide YouTube search assistance
            from utils.gemini_client import gemini_client
            
            prompt = f"""The user wants to search YouTube for: "{query}"

Provide a helpful response that includes:
1. The best search terms to use on YouTube
2. Types of videos they might find
3. Popular channels or creators for this topic
4. Any relevant tips for finding good content

Be conversational and helpful. Format your response nicely for Discord."""
            
            ai_response = await gemini_client.generate_response(prompt, use_pro=True)
            
            embed = helpers.create_embed(
                f"🎥 YouTube Search Help: {query}",
                ai_response,
                color=0xFF0000
            )
            
            embed.add_field(
                name="🔍 Quick Search",
                value=f"[Search YouTube for '{query}'](https://www.youtube.com/results?search_query={query.replace(' ', '+')})",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send("❌ Failed to get YouTube search assistance.")
    
    @app_commands.command(name="wikipedia", description="Search Wikipedia")
    @app_commands.describe(term="Search term")
    async def wikipedia_search(self, interaction: discord.Interaction, term: str):
        await interaction.response.defer()
        
        try:
            # Set language to English
            wikipedia.set_lang("en")
            
            # Search for the term
            summary = wikipedia.summary(term, sentences=3)
            page = wikipedia.page(term)
            
            embed = helpers.create_embed(
                f"📚 Wikipedia: {page.title}",
                helpers.clean_content(summary, 1500),
                color=0x000000
            )
            
            embed.add_field(
                name="🔗 Full Article",
                value=f"[Read more on Wikipedia]({page.url})",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Multiple results found
            options = e.options[:5]  # Show first 5 options
            embed = helpers.create_embed(
                "📚 Wikipedia - Multiple Results",
                f"Multiple articles found for '{term}'. Did you mean:\n" + "\n".join(f"• {option}" for option in options),
                color=0xFFAA00
            )
            await interaction.followup.send(embed=embed)
            
        except wikipedia.exceptions.PageError:
            await interaction.followup.send(f"❌ No Wikipedia article found for '{term}'.")
            
        except Exception as e:
            await interaction.followup.send("❌ Failed to search Wikipedia.")
    
    @app_commands.command(name="github", description="Get GitHub repository information")
    @app_commands.describe(repository="Repository in format 'username/repo'")
    async def github_repo(self, interaction: discord.Interaction, repository: str):
        await interaction.response.defer()
        
        try:
            repo = self.github.get_repo(repository)
            
            embed = helpers.create_embed(
                f"🐙 GitHub: {repo.full_name}",
                helpers.clean_content(repo.description or "No description", 500),
                color=0x24292e
            )
            
            embed.add_field(
                name="📊 Stats",
                value=f"⭐ {repo.stargazers_count:,} stars\n"
                      f"🍴 {repo.forks_count:,} forks\n"
                      f"📝 {repo.open_issues_count:,} issues",
                inline=True
            )
            
            embed.add_field(
                name="💻 Details",
                value=f"**Language:** {repo.language or 'N/A'}\n"
                      f"**License:** {repo.license.name if repo.license else 'None'}\n"
                      f"**Created:** {repo.created_at.strftime('%Y-%m-%d')}",
                inline=True
            )
            
            embed.add_field(
                name="🔗 Links",
                value=f"[Repository]({repo.html_url})",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send("❌ Repository not found or API error.")
    
    @app_commands.command(name="roleinfo", description="Show detailed information about a role")
    @app_commands.describe(role="Role to get information about")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = helpers.create_embed(
            f"🎭 Role Information: {role.name}",
            f"Information about the role {role.mention}",
            color=role.color if role.color != discord.Color.default() else BOT_COLOR
        )
        
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Name:** {role.name}\n"
                  f"**ID:** {role.id}\n"
                  f"**Color:** {str(role.color)}\n"
                  f"**Position:** {role.position}",
            inline=True
        )
        
        embed.add_field(
            name="👥 Members",
            value=f"{len(role.members)} members",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Settings",
            value=f"**Mentionable:** {'Yes' if role.mentionable else 'No'}\n"
                  f"**Hoisted:** {'Yes' if role.hoist else 'No'}\n"
                  f"**Managed:** {'Yes' if role.managed else 'No'}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Created",
            value=f"<t:{int(role.created_at.timestamp())}:F>",
            inline=False
        )
        
        # Show key permissions
        perms = []
        if role.permissions.administrator:
            perms.append("Administrator")
        if role.permissions.manage_guild:
            perms.append("Manage Server")
        if role.permissions.manage_channels:
            perms.append("Manage Channels")
        if role.permissions.manage_roles:
            perms.append("Manage Roles")
        if role.permissions.kick_members:
            perms.append("Kick Members")
        if role.permissions.ban_members:
            perms.append("Ban Members")
        
        if perms:
            embed.add_field(
                name="🔐 Key Permissions",
                value=", ".join(perms[:8]),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="channelinfo", description="Show detailed information about a channel")
    @app_commands.describe(channel="Channel to get information about")
    async def channelinfo(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        target_channel = channel or interaction.channel
        
        embed = helpers.create_embed(
            f"📺 Channel Information: #{target_channel.name}",
            f"Information about {target_channel.mention}",
            color=BOT_COLOR
        )
        
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Name:** {target_channel.name}\n"
                  f"**ID:** {target_channel.id}\n"
                  f"**Type:** {str(target_channel.type).title()}\n"
                  f"**Position:** {target_channel.position}",
            inline=True
        )
        
        if target_channel.category:
            embed.add_field(
                name="📁 Category",
                value=target_channel.category.name,
                inline=True
            )
        
        embed.add_field(
            name="⚙️ Settings",
            value=f"**NSFW:** {'Yes' if target_channel.nsfw else 'No'}\n"
                  f"**Slowmode:** {target_channel.slowmode_delay}s\n"
                  f"**News:** {'Yes' if hasattr(target_channel, 'is_news') and target_channel.is_news() else 'No'}",
            inline=True
        )
        
        if target_channel.topic:
            embed.add_field(
                name="📝 Topic",
                value=helpers.clean_content(target_channel.topic, 500),
                inline=False
            )
        
        embed.add_field(
            name="📅 Created",
            value=f"<t:{int(target_channel.created_at.timestamp())}:F>",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for trigger words and respond only for exact matches"""
        if message.author.bot:
            return
        
        # Define trigger responses - only exact word matches
        triggers = {
            "ip": "Madaripur",
            "hello": "Hello there!",
            "ping": "Pong!",
            "test": "Test successful!",
            "gm": "Good morning!",
            "gn": "Good night!",
            "thanks": "You're welcome!",
            "ty": "You're welcome!",
            "bot": "Yes, I'm Actor-Craft bot! Use !help for commands.",
        }
        
        # Convert message to lowercase and split into words
        words = message.content.lower().split()
        
        # Check if any word is an exact trigger match
        for word in words:
            if word in triggers:
                await message.channel.send(triggers[word])
                break  # Only respond to the first trigger found

async def setup(bot):
    await bot.add_cog(UtilityInfoCog(bot))
