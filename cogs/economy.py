import discord
from discord.ext import commands
import random
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class TokenEconomyDatabase:
    def __init__(self):
        self.db_file = "token_economy.db"
        self.init_db()
    
    def init_db(self):
        """Initialize the token economy database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Users table for token balances and cooldowns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_users (
                user_id TEXT,
                guild_id TEXT,
                balance INTEGER DEFAULT 0,
                last_daily TEXT,
                last_quiz TEXT,
                PRIMARY KEY (user_id, guild_id)
            )
        ''')
        
        # Inventory table for purchased items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_inventory (
                user_id TEXT,
                guild_id TEXT,
                item_type TEXT,
                item_name TEXT,
                quantity INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, guild_id, item_type, item_name)
            )
        ''')
        
        # Quiz questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize quiz questions
        self.init_quiz_questions()
    
    def init_quiz_questions(self):
        """Initialize quiz questions if empty"""
        questions = [
            ("What is the capital of France?", "paris"),
            ("What is 15 x 8?", "120"),
            ("What year did World War II end?", "1945"),
            ("What is the largest planet in our solar system?", "jupiter"),
            ("Who painted the Mona Lisa?", "leonardo da vinci"),
            ("What is the chemical symbol for gold?", "au"),
            ("Who wrote Romeo and Juliet?", "william shakespeare"),
            ("What is the square root of 144?", "12"),
            ("What is the hardest natural substance on Earth?", "diamond"),
            ("In what year was the first iPhone released?", "2007"),
            ("What is the smallest country in the world?", "vatican city"),
            ("What gas do plants absorb from the atmosphere?", "carbon dioxide"),
            ("What is the currency of Japan?", "yen"),
            ("How many sides does a hexagon have?", "6"),
            ("What is the boiling point of water in Celsius?", "100"),
            ("Who developed the theory of relativity?", "albert einstein"),
            ("What is the largest ocean on Earth?", "pacific ocean"),
            ("What is 2 to the power of 10?", "1024"),
            ("What is the most abundant gas in Earth's atmosphere?", "nitrogen"),
            ("What planet is known as the Red Planet?", "mars")
        ]
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Check if questions already exist
        cursor.execute("SELECT COUNT(*) FROM quiz_questions")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.executemany("INSERT INTO quiz_questions (question, answer) VALUES (?, ?)", questions)
            conn.commit()
        
        conn.close()
    
    def get_balance(self, user_id: str, guild_id: str) -> int:
        """Get user's token balance"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT balance FROM token_users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else 0
    
    def update_balance(self, user_id: str, guild_id: str, amount: int):
        """Add/subtract tokens from user balance"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get current balance
        current_balance = self.get_balance(user_id, guild_id)
        new_balance = max(0, current_balance + amount)  # Don't allow negative balance
        
        cursor.execute('''
            INSERT OR REPLACE INTO token_users (user_id, guild_id, balance, last_daily, last_quiz)
            VALUES (?, ?, ?, 
                COALESCE((SELECT last_daily FROM token_users WHERE user_id = ? AND guild_id = ?), ''),
                COALESCE((SELECT last_quiz FROM token_users WHERE user_id = ? AND guild_id = ?), '')
            )
        ''', (user_id, guild_id, new_balance, user_id, guild_id, user_id, guild_id))
        
        conn.commit()
        conn.close()
        return new_balance
    
    def set_balance(self, user_id: str, guild_id: str, amount: int):
        """Set user balance to specific amount"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO token_users (user_id, guild_id, balance, last_daily, last_quiz)
            VALUES (?, ?, ?, 
                COALESCE((SELECT last_daily FROM token_users WHERE user_id = ? AND guild_id = ?), ''),
                COALESCE((SELECT last_quiz FROM token_users WHERE user_id = ? AND guild_id = ?), '')
            )
        ''', (user_id, guild_id, amount, user_id, guild_id, user_id, guild_id))
        
        conn.commit()
        conn.close()
    
    def can_daily(self, user_id: str, guild_id: str) -> bool:
        """Check if user can claim daily reward"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_daily FROM token_users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        result = cursor.fetchone()
        
        conn.close()
        
        if not result or not result[0]:
            return True
        
        try:
            last_daily = datetime.fromisoformat(result[0])
            return datetime.now() - last_daily >= timedelta(hours=24)
        except:
            return True
    
    def update_daily(self, user_id: str, guild_id: str):
        """Update last daily claim time"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO token_users (user_id, guild_id, balance, last_daily, last_quiz)
            VALUES (?, ?, 
                COALESCE((SELECT balance FROM token_users WHERE user_id = ? AND guild_id = ?), 0),
                ?,
                COALESCE((SELECT last_quiz FROM token_users WHERE user_id = ? AND guild_id = ?), '')
            )
        ''', (user_id, guild_id, user_id, guild_id, now, user_id, guild_id))
        
        conn.commit()
        conn.close()
    
    def can_quiz(self, user_id: str, guild_id: str) -> bool:
        """Check if user can start quiz"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_quiz FROM token_users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        result = cursor.fetchone()
        
        conn.close()
        
        if not result or not result[0]:
            return True
        
        try:
            last_quiz = datetime.fromisoformat(result[0])
            return datetime.now() - last_quiz >= timedelta(hours=1)  # Changed to 1 hour
        except:
            return True
    
    def update_quiz(self, user_id: str, guild_id: str):
        """Update last quiz time"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO token_users (user_id, guild_id, balance, last_daily, last_quiz)
            VALUES (?, ?, 
                COALESCE((SELECT balance FROM token_users WHERE user_id = ? AND guild_id = ?), 0),
                COALESCE((SELECT last_daily FROM token_users WHERE user_id = ? AND guild_id = ?), ''),
                ?
            )
        ''', (user_id, guild_id, user_id, guild_id, user_id, guild_id, now))
        
        conn.commit()
        conn.close()
    
    def get_random_quiz(self) -> tuple:
        """Get random quiz question"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT question, answer FROM quiz_questions ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        conn.close()
        return result if result else ("What is 2+2?", "4")
    
    def add_item(self, user_id: str, guild_id: str, item_type: str, item_name: str, quantity: int = 1):
        """Add item to inventory"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO token_inventory (user_id, guild_id, item_type, item_name, quantity)
            VALUES (?, ?, ?, ?, 
                COALESCE((SELECT quantity FROM token_inventory WHERE user_id = ? AND guild_id = ? AND item_type = ? AND item_name = ?), 0) + ?
            )
        ''', (user_id, guild_id, item_type, item_name, user_id, guild_id, item_type, item_name, quantity))
        
        conn.commit()
        conn.close()
    
    def get_inventory(self, user_id: str, guild_id: str) -> List[dict]:
        """Get user inventory"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT item_type, item_name, quantity FROM token_inventory WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        results = cursor.fetchall()
        
        conn.close()
        return [{"type": r[0], "name": r[1], "quantity": r[2]} for r in results]
    
    def get_leaderboard(self, guild_id: str, limit: int = 10) -> List[tuple]:
        """Get top users by balance"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, balance FROM token_users WHERE guild_id = ? ORDER BY balance DESC LIMIT ?", (guild_id, limit))
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def has_item(self, user_id: str, guild_id: str, item_type: str, item_name: str) -> bool:
        """Check if user has specific item"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT quantity FROM token_inventory WHERE user_id = ? AND guild_id = ? AND item_type = ? AND item_name = ?", 
                      (user_id, guild_id, item_type, item_name))
        result = cursor.fetchone()
        
        conn.close()
        return result and result[0] > 0

class TokenEconomy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TokenEconomyDatabase()
        self.active_quizzes = {}  # guild_id: {question, answer, starter}
        
        # Shop items exactly as specified
        self.shop_items = {
            "roles": {
                "High Roller": {
                    "price": 500000,
                    "description": "Gives you a special role to show off your wealth."
                },
                "Quiz Master": {
                    "price": 1000000,
                    "description": "A role for those who prove their intelligence."
                },
                "The Millionaire": {
                    "price": 2500000,
                    "description": "A role that signifies you've broken the bank."
                },
                "The Jackpot": {
                    "price": 5000000,
                    "description": "The ultimate role for the luckiest players."
                }
            },
            "titles": {
                "The Lucky": {
                    "price": 100000,
                    "description": "A title for the fortunate ones."
                },
                "The Unlucky": {
                    "price": 150000,
                    "description": "A title for those with bad luck."
                },
                "The All-In": {
                    "price": 1000000,
                    "description": "For those who risk everything."
                },
                "The Risk Taker": {
                    "price": 750000,
                    "description": "For the brave gamblers."
                },
                "High Stakes": {
                    "price": 500000,
                    "description": "For high-stakes players."
                }
            },
            "pets": {
                "Rabbit's Foot": {
                    "price": 200000,
                    "description": "Grants a small luck boost to your coin flips."
                },
                "Golden Dragon": {
                    "price": 1500000,
                    "description": "Grants a daily bonus of 10,000 T."
                },
                "Fortune Cat": {
                    "price": 3000000,
                    "description": "Grants a large daily bonus of 50,000 T."
                },
                "Phoenix": {
                    "price": 10000000,
                    "description": "Grants a massive daily bonus of 100,000 T."
                }
            },
            "artifacts": {
                "Lucky Coin": {
                    "price": 50000,
                    "description": "Guarantees a win on your next !flip."
                },
                "The Cheat": {
                    "price": 250000,
                    "description": "Guarantees a win on your next !gamble."
                },
                "Insurance": {
                    "price": 1000000,
                    "description": "Refunds your money if you lose your bet (10% refund rate)."
                }
            }
        }
    
    def format_tokens(self, amount: int) -> str:
        """Format token amount"""
        return f"{amount:,} T"
    
    @commands.command(name='bal', aliases=['balance'])
    async def balance(self, ctx, user: discord.Member = None):
        """Shows your current Token balance"""
        target = user or ctx.author
        balance = self.db.get_balance(str(target.id), str(ctx.guild.id))
        
        embed = discord.Embed(
            title=f"💰 {target.display_name}'s Balance",
            description=f"**{self.format_tokens(balance)}**",
            color=0xFFD700
        )
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='daily')
    async def daily(self, ctx):
        """Claim your daily Token reward"""
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        if not self.db.can_daily(user_id, guild_id):
            embed = discord.Embed(
                title="⏰ Daily Already Claimed",
                description="You've already claimed your daily reward! Come back in 24 hours.",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
        
        # Check for pet bonuses
        inventory = self.db.get_inventory(user_id, guild_id)
        daily_bonus = 0
        
        for item in inventory:
            if item["type"] == "pets":
                if item["name"] == "Golden Dragon":
                    daily_bonus += 10000
                elif item["name"] == "Fortune Cat":
                    daily_bonus += 50000
                elif item["name"] == "Phoenix":
                    daily_bonus += 100000
        
        # Base daily amount
        daily_amount = random.randint(1000, 5000) + daily_bonus
        
        self.db.update_balance(user_id, guild_id, daily_amount)
        self.db.update_daily(user_id, guild_id)
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received **{self.format_tokens(daily_amount)}**!",
            color=0x4CAF50
        )
        
        if daily_bonus > 0:
            embed.add_field(
                name="🐾 Pet Bonus",
                value=f"Extra **{self.format_tokens(daily_bonus)}** from your pets!",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='quiz')
    async def quiz(self, ctx):
        """Start a trivia quiz for 50,000 T reward"""
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        # Check if user is owner (bypass cooldown)
        is_owner = await self.bot.is_owner(ctx.author)
        
        if not is_owner and not self.db.can_quiz(user_id, guild_id):
            embed = discord.Embed(
                title="⏰ Quiz Cooldown",
                description="You can only start a quiz every 1 hour!",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
        
        # Check if there's already an active quiz
        if guild_id in self.active_quizzes:
            embed = discord.Embed(
                title="🧠 Quiz Already Active",
                description="There's already a quiz running in this server!",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
        
        question, answer = self.db.get_random_quiz()
        
        self.active_quizzes[guild_id] = {
            "question": question,
            "answer": answer.lower(),
            "starter": user_id
        }
        
        embed = discord.Embed(
            title="🧠 Trivia Quiz - 50,000 T Prize!",
            description=f"**Question:** {question}\n\nFirst correct answer wins **50,000 T**!",
            color=0x2196F3
        )
        embed.set_footer(text="You have 30 seconds to answer!")
        
        await ctx.send(embed=embed)
        
        # Wait 30 seconds then end quiz if no winner
        await asyncio.sleep(30)
        
        if guild_id in self.active_quizzes:
            embed = discord.Embed(
                title="⏰ Quiz Ended",
                description=f"Time's up! The correct answer was: **{answer.title()}**",
                color=0xFF9800
            )
            await ctx.send(embed=embed)
            del self.active_quizzes[guild_id]
    
    @commands.command(name='flip')
    async def flip(self, ctx, amount: int):
        """Bet tokens on a coin flip"""
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        balance = self.db.get_balance(user_id, guild_id)
        
        if balance < amount:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description=f"You only have **{self.format_tokens(balance)}** but tried to bet **{self.format_tokens(amount)}**!",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
        
        # Check for lucky coin or rabbit's foot
        inventory = self.db.get_inventory(user_id, guild_id)
        guaranteed_win = False
        luck_boost = 0
        
        for item in inventory:
            if item["type"] == "artifacts" and item["name"] == "Lucky Coin":
                guaranteed_win = True
                break
            elif item["type"] == "pets" and item["name"] == "Rabbit's Foot":
                luck_boost = 5  # 5% better odds
        
        # Coin flip
        if guaranteed_win:
            won = True
        else:
            win_chance = 50 + luck_boost
            won = random.randint(1, 100) <= win_chance
        
        if won:
            self.db.update_balance(user_id, guild_id, amount)
            new_balance = self.db.get_balance(user_id, guild_id)
            
            embed = discord.Embed(
                title="🪙 Coin Flip - You Won!",
                description=f"🎉 **Heads!** You won **{self.format_tokens(amount)}**!\n\nNew balance: **{self.format_tokens(new_balance)}**",
                color=0x4CAF50
            )
        else:
            # Check for insurance
            insurance_refund = 0
            for item in inventory:
                if item["type"] == "artifacts" and item["name"] == "Insurance":
                    insurance_refund = amount // 10  # 10% refund
                    break
            
            self.db.update_balance(user_id, guild_id, -amount + insurance_refund)
            new_balance = self.db.get_balance(user_id, guild_id)
            
            embed = discord.Embed(
                title="🪙 Coin Flip - You Lost!",
                description=f"😢 **Tails!** You lost **{self.format_tokens(amount)}**!\n\nNew balance: **{self.format_tokens(new_balance)}**",
                color=0xFF6B6B
            )
            
            if insurance_refund > 0:
                embed.add_field(
                    name="🛡️ Insurance",
                    value=f"Your insurance refunded **{self.format_tokens(insurance_refund)}**!",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='shop')
    async def shop(self, ctx, category: str = None):
        """Display the Token shop"""
        if not category:
            embed = discord.Embed(
                title="🛒 Token Shop",
                description="Welcome to the Token shop! Choose a category:",
                color=0x9C27B0
            )
            
            embed.add_field(
                name="📋 Categories",
                value="• `!shop roles` - Prestigious server roles\n• `!shop titles` - Profile titles\n• `!shop pets` - Daily bonus pets\n• `!shop artifacts` - Special items",
                inline=False
            )
            
            embed.set_footer(text="Use !buy <category> <item> to purchase items")
            await ctx.send(embed=embed)
            return
        
        category = category.lower()
        if category not in self.shop_items:
            await ctx.send("❌ Invalid category! Use `!shop` to see available categories.")
            return
        
        embed = discord.Embed(
            title=f"🛒 {category.title()} Shop",
            color=0x9C27B0
        )
        
        for item_name, item_data in self.shop_items[category].items():
            embed.add_field(
                name=f"{item_name}",
                value=f"**{self.format_tokens(item_data['price'])}**\n{item_data['description']}",
                inline=True
            )
        
        embed.set_footer(text=f"Use !buy {category} <item_name> to purchase")
        await ctx.send(embed=embed)
    
    @commands.command(name='buy')
    async def buy(self, ctx, category: str, *, item_name: str):
        """Buy an item from the shop"""
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        category = category.lower()
        if category not in self.shop_items:
            await ctx.send("❌ Invalid category!")
            return
        
        # Find item (case insensitive)
        item_data = None
        actual_item_name = None
        for shop_item_name, data in self.shop_items[category].items():
            if shop_item_name.lower() == item_name.lower():
                item_data = data
                actual_item_name = shop_item_name
                break
        
        if not item_data:
            await ctx.send(f"❌ Item '{item_name}' not found in {category} category!")
            return
        
        balance = self.db.get_balance(user_id, guild_id)
        
        if balance < item_data["price"]:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description=f"You need **{self.format_tokens(item_data['price'])}** but only have **{self.format_tokens(balance)}**!",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
        
        # Purchase item
        self.db.update_balance(user_id, guild_id, -item_data["price"])
        self.db.add_item(user_id, guild_id, category, actual_item_name)
        
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You bought **{actual_item_name}** for **{self.format_tokens(item_data['price'])}**!",
            color=0x4CAF50
        )
        
        new_balance = self.db.get_balance(user_id, guild_id)
        embed.add_field(name="Remaining Balance", value=self.format_tokens(new_balance), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='inv', aliases=['inventory'])
    async def inventory(self, ctx, user: discord.Member = None):
        """Show your inventory"""
        target = user or ctx.author
        user_id = str(target.id)
        guild_id = str(ctx.guild.id)
        
        inventory = self.db.get_inventory(user_id, guild_id)
        
        if not inventory:
            embed = discord.Embed(
                title=f"📦 {target.display_name}'s Inventory",
                description="Inventory is empty!",
                color=0x607D8B
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📦 {target.display_name}'s Inventory",
            color=0x607D8B
        )
        
        # Group items by category
        categories = {}
        for item in inventory:
            category = item["type"]
            if category not in categories:
                categories[category] = []
            if item["quantity"] > 1:
                categories[category].append(f"{item['name']} (x{item['quantity']})")
            else:
                categories[category].append(item['name'])
        
        for category, items in categories.items():
            embed.add_field(
                name=f"{category.title()}",
                value="\n".join(items),
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='give')
    async def give(self, ctx, user: discord.Member, amount: int):
        """Transfer tokens to another user"""
        if user.bot:
            await ctx.send("❌ You can't give tokens to bots!")
            return
        
        if user == ctx.author:
            await ctx.send("❌ You can't give tokens to yourself!")
            return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        user_id = str(ctx.author.id)
        target_id = str(user.id)
        guild_id = str(ctx.guild.id)
        
        balance = self.db.get_balance(user_id, guild_id)
        
        if balance < amount:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description=f"You only have **{self.format_tokens(balance)}** but tried to give **{self.format_tokens(amount)}**!",
                color=0xFF6B6B
            )
            await ctx.send(embed=embed)
            return
        
        # Transfer tokens
        self.db.update_balance(user_id, guild_id, -amount)
        self.db.update_balance(target_id, guild_id, amount)
        
        embed = discord.Embed(
            title="💸 Transfer Successful!",
            description=f"{ctx.author.mention} gave **{self.format_tokens(amount)}** to {user.mention}!",
            color=0x4CAF50
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    async def leaderboard(self, ctx):
        """Display the top 10 richest users"""
        guild_id = str(ctx.guild.id)
        top_users = self.db.get_leaderboard(guild_id, 10)
        
        if not top_users:
            embed = discord.Embed(
                title="🏆 Token Leaderboard",
                description="No users found!",
                color=0xFFD700
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🏆 Token Leaderboard - Top 10",
            color=0xFFD700
        )
        
        leaderboard_text = ""
        for i, (user_id, balance) in enumerate(top_users, 1):
            try:
                user = self.bot.get_user(int(user_id))
                if user:
                    name = user.display_name
                else:
                    name = f"Unknown User"
            except:
                name = f"Unknown User"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard_text += f"{medal} **{name}** - {self.format_tokens(balance)}\n"
        
        embed.description = leaderboard_text
        await ctx.send(embed=embed)
    
    @commands.command(name='get_tokens')
    @commands.is_owner()
    async def get_tokens(self, ctx, amount: int = 1000000):
        """Owner only command to get tokens"""
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        self.db.update_balance(user_id, guild_id, amount)
        
        embed = discord.Embed(
            title="💰 Tokens Added",
            description=f"Added **{self.format_tokens(amount)}** to your balance!",
            color=0x4CAF50
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='work')
    async def work(self, ctx):
        """Work to earn some tokens"""
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        # Random work reward
        work_amount = random.randint(100, 1000)
        self.db.update_balance(user_id, guild_id, work_amount)
        
        work_messages = [
            f"You worked hard and earned **{self.format_tokens(work_amount)}**!",
            f"Good job! You made **{self.format_tokens(work_amount)}** today!",
            f"Your work paid off with **{self.format_tokens(work_amount)}**!",
            f"Nice work! You earned **{self.format_tokens(work_amount)}**!"
        ]
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=random.choice(work_messages),
            color=0x4CAF50
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help_economy', aliases=['ehelp'])
    async def help_economy(self, ctx):
        """Show economy help"""
        embed = discord.Embed(
            title="💰 Token Economy Help",
            description="Here are all the economy commands:",
            color=0x9C27B0
        )
        
        embed.add_field(
            name="💳 Basic Commands",
            value="• `!bal` - Check your balance\n• `!daily` - Daily reward (24h cooldown)\n• `!work` - Work to earn tokens",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Games & Earning",
            value="• `!quiz` - Trivia quiz (50,000 T prize, 1h cooldown)\n• `!flip <amount>` - Coin flip gambling",
            inline=False
        )
        
        embed.add_field(
            name="🛒 Shop & Trading",
            value="• `!shop` - Browse shop categories\n• `!buy <category> <item>` - Buy items\n• `!inv` - View your inventory",
            inline=False
        )
        
        embed.add_field(
            name="👥 Social",
            value="• `!give <@user> <amount>` - Transfer tokens\n• `!leaderboard` - Top 10 richest users",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for quiz answers"""
        if message.author.bot:
            return
        
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        # Check if there's an active quiz
        if guild_id not in self.active_quizzes:
            return
        
        quiz_data = self.active_quizzes[guild_id]
        
        # Check if answer is correct (multiple variations)
        user_answer = message.content.lower().strip()
        correct_answer = quiz_data["answer"].lower()
        
        # Check for exact match or if answer contains the correct answer
        is_correct = (user_answer == correct_answer or 
                     correct_answer in user_answer or
                     user_answer in correct_answer)
        
        if is_correct:
            # Winner!
            self.db.update_balance(user_id, guild_id, 50000)
            self.db.update_quiz(quiz_data["starter"], guild_id)  # Update cooldown for starter
            
            embed = discord.Embed(
                title="🎉 Quiz Winner!",
                description=f"{message.author.mention} answered correctly and won **50,000 T**!\n\n**Answer:** {quiz_data['answer'].title()}",
                color=0x4CAF50
            )
            
            await message.channel.send(embed=embed)
            del self.active_quizzes[guild_id]

async def setup(bot):
    await bot.add_cog(TokenEconomy(bot))