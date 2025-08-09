import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
from utils.gemini_client import gemini_client
from utils.helpers import helpers
from database import db
from config import OWNER_ID

class AIPersonalityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="gemini_api", description="Set or update the Gemini AI API key")
    @app_commands.describe(api_key="Your Gemini API key")
    async def gemini_api(self, interaction: discord.Interaction, api_key: str):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can set API keys.", ephemeral=True)
            return
        
        # Update the API key (in production, this should update environment)
        gemini_client.client = gemini_client.client.__class__(api_key=api_key)
        
        embed = helpers.create_embed(
            "API Key Updated",
            "✅ Gemini API key has been successfully updated!",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="train", description="Enable or disable AI learning and memory")
    @app_commands.describe(enabled="Enable or disable training")
    async def train(self, interaction: discord.Interaction, enabled: bool):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to use this command.", ephemeral=True)
            return
        
        result = gemini_client.toggle_training(enabled)
        
        embed = helpers.create_embed(
            "Training Mode",
            f"✅ {result}",
            color=0x00ff00 if enabled else 0xffaa00
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="personality", description="Activate a specific personality")
    @app_commands.describe(name="Personality name (default, friendly, sarcastic, etc.)")
    async def personality(self, interaction: discord.Interaction, name: str):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to use this command.", ephemeral=True)
            return
        
        # Check if personality file exists
        personality_path = f"personality/{name.lower()}.json"
        if not os.path.exists(personality_path):
            embed = helpers.create_embed(
                "Personality Not Found",
                f"❌ Personality '{name}' not found. Available personalities: default, friendly, sarcastic",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        result = gemini_client.set_personality(name.lower())
        
        embed = helpers.create_embed(
            "Personality Changed",
            f"✅ {result}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="importpersonality", description="Import a personality file")
    @app_commands.describe(name="Name of the personality file to import")
    async def importpersonality(self, interaction: discord.Interaction, name: str):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can import personalities.", ephemeral=True)
            return
        
        personality_path = f"personality/{name.lower()}.json"
        if not os.path.exists(personality_path):
            embed = helpers.create_embed(
                "Import Failed",
                f"❌ Personality file '{name}.json' not found in /personality/ directory.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        try:
            with open(personality_path, 'r') as f:
                personality_data = json.load(f)
            
            # Validate personality file structure
            required_keys = ['name', 'traits', 'style']
            if not all(key in personality_data for key in required_keys):
                raise ValueError("Invalid personality file structure")
            
            embed = helpers.create_embed(
                "Personality Imported",
                f"✅ Successfully imported personality: **{personality_data['name']}**\n\n"
                f"**Traits:** {personality_data['traits']}\n"
                f"**Style:** {personality_data['style']}",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = helpers.create_embed(
                "Import Failed",
                f"❌ Failed to import personality: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ownerbehavior", description="Define how the bot should treat the owner")
    @app_commands.describe(mode="Behavior mode (loyal, casual, professional, playful)")
    async def ownerbehavior(self, interaction: discord.Interaction, mode: str):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can set owner behavior.", ephemeral=True)
            return
        
        valid_modes = ['loyal', 'casual', 'professional', 'playful', 'sarcastic']
        if mode.lower() not in valid_modes:
            embed = helpers.create_embed(
                "Invalid Mode",
                f"❌ Invalid behavior mode. Available modes: {', '.join(valid_modes)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        result = gemini_client.set_owner_behavior(mode.lower())
        
        embed = helpers.create_embed(
            "Owner Behavior Set",
            f"✅ {result}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aimood", description="Set the AI's current mood")
    @app_commands.describe(mood="Mood setting (friendly, sarcastic, professional, excited, calm)")
    async def aimood(self, interaction: discord.Interaction, mood: str):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to use this command.", ephemeral=True)
            return
        
        valid_moods = ['friendly', 'sarcastic', 'professional', 'excited', 'calm', 'helpful', 'playful']
        if mood.lower() not in valid_moods:
            embed = helpers.create_embed(
                "Invalid Mood",
                f"❌ Invalid mood. Available moods: {', '.join(valid_moods)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return
        
        result = gemini_client.set_mood(mood.lower())
        
        embed = helpers.create_embed(
            "AI Mood Set",
            f"✅ {result}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aiwhoami", description="Show the bot's current identity/personality")
    async def aiwhoami(self, interaction: discord.Interaction):
        identity = gemini_client.get_identity()
        
        embed = helpers.create_embed(
            "AI Identity",
            "Here's my current configuration:",
            color=0x0099ff
        )
        embed.add_field(
            name="🎭 Personality",
            value=identity['personality'].title(),
            inline=True
        )
        embed.add_field(
            name="😊 Mood", 
            value=identity['mood'].title(),
            inline=True
        )
        embed.add_field(
            name="👑 Owner Behavior",
            value=identity['owner_behavior'].title(),
            inline=True
        )
        embed.add_field(
            name="🧠 Training Mode",
            value="Enabled" if identity['training'] else "Disabled",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="smartsearch", description="AI-powered search with comprehensive results")
    @app_commands.describe(query="Your search query")
    async def smartsearch(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        
        try:
            # Use the enhanced smart response for search
            result = await gemini_client.generate_smart_response(
                query,
                interaction.user.id,
                interaction.guild.id,
                interaction.user.display_name,
                "search"
            )
            
            # Add helpful links
            search_links = []
            search_links.append(f"🌐 [Google Search](https://www.google.com/search?q={query.replace(' ', '+')})")
            if "youtube" in query.lower() or "video" in query.lower():
                search_links.append(f"🎥 [YouTube](https://www.youtube.com/results?search_query={query.replace(' ', '+')})")
            if "code" in query.lower() or "programming" in query.lower():
                search_links.append(f"💻 [GitHub](https://github.com/search?q={query.replace(' ', '+')})")
            
            embed = helpers.create_embed(
                f"🔍 Smart Search: {query}",
                helpers.clean_content(result, 1800),
                color=0x4285f4
            )
            
            embed.add_field(
                name="🔗 Additional Resources",
                value="\n".join(search_links),
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = helpers.create_embed(
                "Search Error",
                f"❌ Sorry, I couldn't process your search: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="restart", description="Restart the bot (admin only)")
    async def restart(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can restart the bot.", ephemeral=True)
            return
        
        embed = helpers.create_embed(
            "Restarting Bot",
            "🔄 Bot is restarting... Please wait a moment.",
            color=0xffaa00
        )
        await interaction.response.send_message(embed=embed)
        
        # Close database connections
        await asyncio.sleep(2)
        await self.bot.close()
    
    @app_commands.command(name="shutdown", description="Shutdown the bot (admin only)")
    async def shutdown(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can stop the bot.", ephemeral=True)
            return
        
        embed = helpers.create_embed(
            "Stopping Bot",
            "⏹️ Bot is shutting down... Goodbye!",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)
        
        await asyncio.sleep(2)
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(AIPersonalityCog(bot))
