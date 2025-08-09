import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp
from utils.helpers import helpers
from database import db
from config import *

class FunEngagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eight_ball_responses = [
            "🎱 It is certain", "🎱 It is decidedly so", "🎱 Without a doubt",
            "🎱 Yes definitely", "🎱 You may rely on it", "🎱 As I see it, yes",
            "🎱 Most likely", "🎱 Outlook good", "🎱 Yes", "🎱 Signs point to yes",
            "🎱 Reply hazy, try again", "🎱 Ask again later", "🎱 Better not tell you now",
            "🎱 Cannot predict now", "🎱 Concentrate and ask again",
            "🎱 Don't count on it", "🎱 My reply is no", "🎱 My sources say no",
            "🎱 Outlook not so good", "🎱 Very doubtful"
        ]
    
    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="Your question for the magic 8-ball")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        if not question.endswith('?'):
            await interaction.response.send_message("❓ Please ask a proper question (ending with '?')", ephemeral=True)
            return
        
        response = random.choice(self.eight_ball_responses)
        
        embed = helpers.create_embed(
            "🎱 Magic 8-Ball",
            f"**Question:** {question}\n**Answer:** {response}",
            color=helpers.get_random_color()
        )
        embed.set_thumbnail(url="https://i.imgur.com/kKXx9Kn.png")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roll", description="Roll a die")
    @app_commands.describe(sides="Number of sides on the die (default: 6)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        if sides < 2 or sides > 1000:
            await interaction.response.send_message("❌ Die must have between 2 and 1000 sides.", ephemeral=True)
            return
        
        result = random.randint(1, sides)
        
        embed = helpers.create_embed(
            "🎲 Dice Roll",
            f"**Rolled a d{sides}:** {result}",
            color=helpers.get_random_color()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="flipcoin", description="Flip a coin")
    async def flipcoin(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        emoji = "🟡" if result == "Heads" else "⚪"
        
        embed = helpers.create_embed(
            "🪙 Coin Flip",
            f"{emoji} **{result}**",
            color=0xFFD700 if result == "Heads" else 0xC0C0C0
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="meme", description="Get a random meme")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            data = await helpers.fetch_json(MEME_API)
            if data and 'url' in data:
                embed = helpers.create_embed(
                    f"😂 {data.get('title', 'Random Meme')}",
                    f"**Subreddit:** r/{data.get('subreddit', 'unknown')}\n"
                    f"**Author:** u/{data.get('author', 'unknown')}",
                    color=helpers.get_random_color()
                )
                embed.set_image(url=data['url'])
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Could not fetch a meme right now. Please try again later.")
                
        except Exception as e:
            await interaction.followup.send("❌ Failed to get meme. Please try again later.")
    
    @app_commands.command(name="cat", description="Get a random cat picture")
    async def cat(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            data = await helpers.fetch_json(CAT_API)
            if data and isinstance(data, list) and len(data) > 0:
                cat_url = data[0]['url']
                
                embed = helpers.create_embed(
                    "🐱 Random Cat",
                    "Here's a cute cat for you!",
                    color=0xFF6B35
                )
                embed.set_image(url=cat_url)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Could not fetch a cat picture right now.")
                
        except Exception as e:
            await interaction.followup.send("❌ Failed to get cat picture. Please try again later.")
    
    @app_commands.command(name="dog", description="Get a random dog picture")
    async def dog(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            data = await helpers.fetch_json(DOG_API)
            if data and isinstance(data, list) and len(data) > 0:
                dog_url = data[0]['url']
                
                embed = helpers.create_embed(
                    "🐶 Random Dog",
                    "Here's a good boy/girl for you!",
                    color=0x8B4513
                )
                embed.set_image(url=dog_url)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Could not fetch a dog picture right now.")
                
        except Exception as e:
            await interaction.followup.send("❌ Failed to get dog picture. Please try again later.")
    
    @app_commands.command(name="rps", description="Play Rock, Paper, Scissors")
    @app_commands.describe(choice="Your choice: rock, paper, or scissors")
    async def rps(self, interaction: discord.Interaction, choice: str):
        choices = ['rock', 'paper', 'scissors']
        emojis = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
        
        if choice.lower() not in choices:
            await interaction.response.send_message("❌ Please choose: rock, paper, or scissors", ephemeral=True)
            return
        
        user_choice = choice.lower()
        bot_choice = random.choice(choices)
        
        # Determine winner
        if user_choice == bot_choice:
            result = "It's a tie! 🤝"
            color = 0xFFFF00
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'paper' and bot_choice == 'rock') or \
             (user_choice == 'scissors' and bot_choice == 'paper'):
            result = "You win! 🎉"
            color = 0x00FF00
        else:
            result = "I win! 🤖"
            color = 0xFF0000
        
        embed = helpers.create_embed(
            "🎮 Rock, Paper, Scissors",
            f"**You:** {emojis[user_choice]} {user_choice.title()}\n"
            f"**Me:** {emojis[bot_choice]} {bot_choice.title()}\n\n"
            f"**Result:** {result}",
            color=color
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.describe(question="Poll question", option1="First option", option2="Second option")
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str):
        embed = helpers.create_embed(
            "📊 Poll",
            f"**{question}**\n\n🇦 {option1}\n🇧 {option2}",
            color=0x0099FF
        )
        embed.set_footer(text="React with 🇦 or 🇧 to vote!")
        
        await interaction.response.send_message(embed=embed)
        
        # Get the message and add reactions
        message = await interaction.original_response()
        await message.add_reaction('🇦')
        await message.add_reaction('🇧')
    
    @app_commands.command(name="wouldyourather", description="Get a would you rather question")
    async def wouldyourather(self, interaction: discord.Interaction):
        questions = [
            "Would you rather have the ability to fly or be invisible?",
            "Would you rather always be 10 minutes late or 20 minutes early?",
            "Would you rather have more time or more money?",
            "Would you rather be able to read minds or predict the future?",
            "Would you rather live without music or without movies?",
            "Would you rather be famous or be the best friend of someone famous?",
            "Would you rather have super strength or super speed?",
            "Would you rather live in the past or the future?",
            "Would you rather never use social media again or never watch another movie?",
            "Would you rather have the ability to change the past or see into the future?"
        ]
        
        question = random.choice(questions)
        
        embed = helpers.create_embed(
            "🤔 Would You Rather",
            question,
            color=0xFF6B9D
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="fact", description="Get a random fact")
    async def fact(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            data = await helpers.fetch_json(FACT_API)
            if data and 'text' in data:
                embed = helpers.create_embed(
                    "🧠 Random Fact",
                    data['text'],
                    color=0x4A90E2
                )
                
                await interaction.followup.send(embed=embed)
            else:
                # Fallback facts
                facts = [
                    "Octopuses have three hearts and blue blood.",
                    "Bananas are berries, but strawberries aren't.",
                    "A group of flamingos is called a 'flamboyance'.",
                    "Honey never spoils - you could eat 3000-year-old honey!",
                    "There are more possible chess games than atoms in the observable universe."
                ]
                fact = random.choice(facts)
                
                embed = helpers.create_embed(
                    "🧠 Random Fact",
                    fact,
                    color=0x4A90E2
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            await interaction.followup.send("❌ Could not fetch a fact right now.")
    
    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            data = await helpers.fetch_json(JOKE_API)
            if data and 'setup' in data and 'punchline' in data:
                embed = helpers.create_embed(
                    "😂 Random Joke",
                    f"**{data['setup']}**\n\n||{data['punchline']}||",
                    color=0xFFA500
                )
                
                await interaction.followup.send(embed=embed)
            else:
                # Fallback jokes
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "Why did the scarecrow win an award? He was outstanding in his field!",
                    "Why don't eggs tell jokes? They'd crack each other up!",
                    "What do you call a fake noodle? An impasta!",
                    "Why did the coffee file a police report? It got mugged!"
                ]
                joke = random.choice(jokes)
                
                embed = helpers.create_embed(
                    "😂 Random Joke",
                    joke,
                    color=0xFFA500
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            await interaction.followup.send("❌ Could not fetch a joke right now.")
    
    # Interaction GIF commands (these would normally use tenor/giphy APIs)
    @app_commands.command(name="hug", description="Hug someone")
    @app_commands.describe(user="User to hug")
    async def hug(self, interaction: discord.Interaction, user: discord.Member):
        embed = helpers.create_embed(
            "🤗 Hug",
            f"**{interaction.user.display_name}** hugs **{user.display_name}**! 💕",
            color=0xFF69B4
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pat", description="Pat someone")
    @app_commands.describe(user="User to pat")
    async def pat(self, interaction: discord.Interaction, user: discord.Member):
        embed = helpers.create_embed(
            "👋 Pat",
            f"**{interaction.user.display_name}** pats **{user.display_name}**! 😊",
            color=0x87CEEB
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="slap", description="Slap someone (playfully)")
    @app_commands.describe(user="User to slap")
    async def slap(self, interaction: discord.Interaction, user: discord.Member):
        embed = helpers.create_embed(
            "👋 Slap",
            f"**{interaction.user.display_name}** slaps **{user.display_name}**! 😤",
            color=0xFF4500
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="kiss", description="Kiss someone")
    @app_commands.describe(user="User to kiss")
    async def kiss(self, interaction: discord.Interaction, user: discord.Member):
        embed = helpers.create_embed(
            "💋 Kiss",
            f"**{interaction.user.display_name}** kisses **{user.display_name}**! 💕",
            color=0xFF1493
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="trigger", description="Create a custom auto-reply trigger")
    @app_commands.describe(word="Trigger word/phrase", response="Bot response")
    async def trigger(self, interaction: discord.Interaction, word: str, response: str):
        if not helpers.has_permission(interaction.user, 'manage_messages'):
            await interaction.response.send_message("❌ You need Manage Messages permission to create triggers.", ephemeral=True)
            return
        
        if len(word) > 100 or len(response) > 500:
            await interaction.response.send_message("❌ Trigger word must be ≤100 chars, response ≤500 chars.", ephemeral=True)
            return
        
        try:
            await db.add_trigger(interaction.guild.id, word.lower(), response, interaction.user.id)
            
            embed = helpers.create_embed(
                "✅ Trigger Created",
                f"**Trigger:** {word}\n**Response:** {response}",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to create trigger: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.describe(message="Message for the bot to say")
    async def say(self, interaction: discord.Interaction, message: str):
        if not helpers.has_permission(interaction.user, 'manage_messages'):
            await interaction.response.send_message("❌ You need Manage Messages permission to use this command.", ephemeral=True)
            return
        
        # Clean the message to prevent abuse
        clean_message = helpers.clean_content(message, 1000)
        
        await interaction.response.send_message("✅ Message sent!", ephemeral=True)
        await interaction.channel.send(clean_message)
    
    @app_commands.command(name="textreverse", description="Reverse text")
    @app_commands.describe(text="Text to reverse")
    async def textreverse(self, interaction: discord.Interaction, text: str):
        reversed_text = text[::-1]
        
        embed = helpers.create_embed(
            "🔄 Reversed Text",
            f"**Original:** {text}\n**Reversed:** {reversed_text}",
            color=helpers.get_random_color()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ascii", description="Convert text to ASCII art (simple)")
    @app_commands.describe(text="Text to convert (max 10 chars)")
    async def ascii(self, interaction: discord.Interaction, text: str):
        if len(text) > 10:
            await interaction.response.send_message("❌ Text must be 10 characters or less.", ephemeral=True)
            return
        
        # Simple ASCII art conversion (this is basic - you could integrate with figlet)
        ascii_art = f"```\n{text.upper()}\n{'='*len(text)}\n```"
        
        embed = helpers.create_embed(
            "🎨 ASCII Art",
            ascii_art,
            color=helpers.get_random_color()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="quote", description="Quote a message by ID")
    @app_commands.describe(message_id="ID of the message to quote")
    async def quote(self, interaction: discord.Interaction, message_id: str):
        try:
            message_id = int(message_id)
            message = await interaction.channel.fetch_message(message_id)
            
            embed = helpers.create_embed(
                f"💬 Quote from {message.author.display_name}",
                message.content or "*[No text content]*",
                color=0x0099FF
            )
            embed.set_footer(text=f"Message sent at {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if message.author.avatar:
                embed.set_thumbnail(url=message.author.avatar.url)
            
            if message.attachments:
                embed.add_field(
                    name="Attachments",
                    value=f"{len(message.attachments)} file(s) attached",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.NotFound:
            await interaction.response.send_message("❌ Message not found in this channel.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid message ID.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to quote message: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(FunEngagementCog(bot))
