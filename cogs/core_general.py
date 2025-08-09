import discord
from discord.ext import commands
from discord import app_commands
import time
from utils.helpers import helpers
from database import db
from config import *

class CoreGeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    
    @app_commands.command(name="help", description="Show all commands or info about a specific command")
    @app_commands.describe(command="Specific command to get help with")
    async def help(self, interaction: discord.Interaction, command: str = None):
        if command:
            # Get help for specific command
            cmd = self.bot.tree.get_command(command)
            if cmd:
                embed = helpers.create_embed(
                    f"Help: /{command}",
                    cmd.description or "No description available",
                    color=BOT_COLOR
                )
                if hasattr(cmd, 'parameters') and cmd.parameters:
                    params = []
                    for param in cmd.parameters:
                        params.append(f"`{param.name}`: {param.description or 'No description'}")
                    embed.add_field(name="Parameters", value="\n".join(params), inline=False)
                
                await interaction.response.send_message(embed=embed)
            else:
                embed = helpers.create_embed(
                    "Command Not Found",
                    f"❌ Command `/{command}` not found.",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed)
        else:
            # Show all command categories
            embed = helpers.create_embed(
                f"{BOT_NAME} - Command Help",
                "Here are all available command categories:",
                color=BOT_COLOR
            )
            
            categories = [
                ("🤖 AI & Personality", "/gemini_api, /train, /personality, /aimood, /aiwhoami, /smartsearch"),
                ("⚙️ Core & General", "/help, /ping, /invite, /botinfo, /userinfo, /serverinfo"),
                ("🛡️ Moderation", "/kick, /ban, /mute, /purge, /warn, /lock, /slowmode"),
                ("🎉 Fun & Games", "/8ball, /roll, /meme, /cat, /dog, /rps, /joke, /hug"),
                ("📡 Utility", "/avatar, /weather, /translate, /remindme, /dm, /wikipedia"),
                ("🛠️ Server Management", "/autorole, /welcomechannel, /addrole, /createrole"),
                ("🎵 Music", "/play, /pause, /skip, /queue, /volume, /shuffle, /loop"),
                ("🎨 Image Effects", "/beautiful, /triggered, /invert, /blur, /grayscale"),
                ("💰 Economy", "!bal, !daily, !work, !quiz, !flip, !shop, !buy, !inv, !give, !leaderboard, !ehelp")
            ]
            
            for category, commands in categories:
                embed.add_field(
                    name=category,
                    value=commands,
                    inline=False
                )
            
            embed.set_footer(text="Use /help <command> for detailed information about a specific command")
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="Show bot latency and response time")
    async def ping(self, interaction: discord.Interaction):
        start = time.time()
        
        embed = helpers.create_embed(
            "🏓 Pong!",
            "Calculating latency...",
            color=BOT_COLOR
        )
        
        await interaction.response.send_message(embed=embed)
        
        end = time.time()
        response_time = round((end - start) * 1000, 2)
        websocket_latency = round(self.bot.latency * 1000, 2)
        
        embed = helpers.create_embed(
            "🏓 Pong!",
            f"🔗 **WebSocket Latency:** {websocket_latency}ms\n"
            f"⚡ **Response Time:** {response_time}ms",
            color=BOT_COLOR
        )
        
        await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="invite", description="Generate bot invite link")
    async def invite(self, interaction: discord.Interaction):
        permissions = discord.Permissions(
            administrator=True,
            manage_guild=True,
            manage_channels=True,
            manage_roles=True,
            manage_messages=True,
            kick_members=True,
            ban_members=True,
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            use_external_emojis=True,
            add_reactions=True,
            connect=True,
            speak=True,
            use_voice_activation=True
        )
        
        invite_url = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        
        embed = helpers.create_embed(
            "📨 Bot Invite Link",
            f"Click [here]({invite_url}) to invite me to your server!",
            color=BOT_COLOR
        )
        embed.add_field(
            name="Permissions Included",
            value="Administrator permissions for full functionality",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="support", description="Get support server link and information")
    async def support(self, interaction: discord.Interaction):
        embed = helpers.create_embed(
            "🆘 Support & Information",
            "Need help with the bot? Here's how to get support:",
            color=BOT_COLOR
        )
        embed.add_field(
            name="Documentation",
            value="Use `/help` to see all available commands",
            inline=False
        )
        embed.add_field(
            name="Bug Reports",
            value="Report issues to the bot administrator",
            inline=False
        )
        embed.add_field(
            name="Feature Requests",
            value="Suggest new features via the bot owner",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="botinfo", description="Show bot information and statistics")
    async def botinfo(self, interaction: discord.Interaction):
        uptime = discord.utils.utcnow() - self.bot.start_time
        uptime_str = helpers.format_time(int(uptime.total_seconds()))
        
        embed = helpers.create_embed(
            f"🤖 {BOT_NAME} Information",
            f"Version {BOT_VERSION}",
            color=BOT_COLOR
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"**Servers:** {len(self.bot.guilds)}\n"
                  f"**Users:** {len(self.bot.users)}\n"
                  f"**Commands:** {len(self.bot.tree.get_commands())}\n"
                  f"**Uptime:** {uptime_str}",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Technical",
            value=f"**Python:** 3.11+\n"
                  f"**discord.py:** {discord.__version__}\n"
                  f"**Latency:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Features",
            value="• Gemini AI Integration\n"
                  "• Advanced Moderation\n"
                  "• Music System\n"
                  "• Economy System\n"
                  "• Image Manipulation\n"
                  "• Custom Triggers",
            inline=False
        )
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="userinfo", description="Show detailed information about a user")
    @app_commands.describe(user="User to get information about")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        embed = helpers.create_embed(
            f"👤 User Information",
            f"Information about {target.mention}",
            color=BOT_COLOR
        )
        
        # Basic info
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Username:** {target.name}\n"
                  f"**Display Name:** {target.display_name}\n"
                  f"**ID:** {target.id}\n"
                  f"**Bot:** {'Yes' if target.bot else 'No'}",
            inline=True
        )
        
        # Account dates
        embed.add_field(
            name="📅 Dates",
            value=f"**Created:** <t:{int(target.created_at.timestamp())}:F>\n"
                  f"**Joined:** <t:{int(target.joined_at.timestamp())}:F>",
            inline=True
        )
        
        # Status and activity
        status_emoji = helpers.get_member_status_emoji(target)
        embed.add_field(
            name="🟢 Status",
            value=f"{status_emoji} {target.status.name.title()}",
            inline=True
        )
        
        # Roles
        if target.roles[1:]:  # Skip @everyone role
            roles = [role.mention for role in target.roles[1:]]
            roles_text = ", ".join(roles[:10])  # Limit to 10 roles
            if len(target.roles) > 11:
                roles_text += f" and {len(target.roles) - 11} more..."
            embed.add_field(
                name=f"🎭 Roles ({len(target.roles)-1})",
                value=roles_text,
                inline=False
            )
        
        # Permissions
        perms = []
        if target.guild_permissions.administrator:
            perms.append("Administrator")
        elif target.guild_permissions.manage_guild:
            perms.append("Manage Server")
        if target.guild_permissions.manage_channels:
            perms.append("Manage Channels")
        if target.guild_permissions.manage_roles:
            perms.append("Manage Roles")
        if target.guild_permissions.kick_members:
            perms.append("Kick Members")
        if target.guild_permissions.ban_members:
            perms.append("Ban Members")
        
        if perms:
            embed.add_field(
                name="🔐 Key Permissions",
                value=", ".join(perms[:5]),
                inline=False
            )
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Show detailed information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        embed = helpers.create_embed(
            f"🏰 Server Information",
            f"Information about **{guild.name}**",
            color=BOT_COLOR
        )
        
        # Basic info
        embed.add_field(
            name="📋 Basic Info",
            value=f"**Name:** {guild.name}\n"
                  f"**ID:** {guild.id}\n"
                  f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n"
                  f"**Created:** <t:{int(guild.created_at.timestamp())}:F>",
            inline=True
        )
        
        # Member counts
        members = guild.members
        humans = [m for m in members if not m.bot]
        bots = [m for m in members if m.bot]
        online = [m for m in members if m.status != discord.Status.offline]
        
        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {guild.member_count}\n"
                  f"**Humans:** {len(humans)}\n"
                  f"**Bots:** {len(bots)}\n"
                  f"**Online:** {len(online)}",
            inline=True
        )
        
        # Server stats
        embed.add_field(
            name="📊 Server Stats",
            value=f"**Text Channels:** {len(guild.text_channels)}\n"
                  f"**Voice Channels:** {len(guild.voice_channels)}\n"
                  f"**Categories:** {len(guild.categories)}\n"
                  f"**Roles:** {len(guild.roles)}",
            inline=True
        )
        
        # Server features
        features = []
        if "VERIFIED" in guild.features:
            features.append("✅ Verified")
        if "PARTNERED" in guild.features:
            features.append("🤝 Partnered")
        if "COMMUNITY" in guild.features:
            features.append("🏘️ Community")
        if "BOOST_TIER_1" in guild.features or guild.premium_tier >= 1:
            features.append(f"⚡ Boost Level {guild.premium_tier}")
        
        if features:
            embed.add_field(
                name="✨ Features",
                value="\n".join(features),
                inline=False
            )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="me", description="Send an action-style message")
    @app_commands.describe(text="Action text")
    async def me(self, interaction: discord.Interaction, text: str):
        message = f"*{interaction.user.display_name} {text}*"
        await interaction.response.send_message(message)
    
    @app_commands.command(name="shrug", description="Send ¯\\_(ツ)_/¯")
    async def shrug(self, interaction: discord.Interaction):
        await interaction.response.send_message("¯\\_(ツ)_/¯")
    
    @app_commands.command(name="tableflip", description="Send (╯°□°）╯︵ ┻━┻")
    async def tableflip(self, interaction: discord.Interaction):
        await interaction.response.send_message("(╯°□°）╯︵ ┻━┻")
    
    @app_commands.command(name="unflip", description="Send ┬─┬ ノ( ゜-゜ノ)")
    async def unflip(self, interaction: discord.Interaction):
        await interaction.response.send_message("┬─┬ ノ( ゜-゜ノ)")
    
    @app_commands.command(name="tts", description="Send a text-to-speech message")
    @app_commands.describe(text="Text to convert to speech")
    async def tts(self, interaction: discord.Interaction, text: str):
        if len(text) > 200:
            await interaction.response.send_message("❌ TTS message must be 200 characters or less.", ephemeral=True)
            return
        
        await interaction.response.send_message(text, tts=True)
    
    @app_commands.command(name="spoiler", description="Mark text as spoiler")
    @app_commands.describe(text="Text to mark as spoiler")
    async def spoiler(self, interaction: discord.Interaction, text: str):
        spoiler_text = f"||{text}||"
        await interaction.response.send_message(spoiler_text)
    
    @app_commands.command(name="nick", description="Change your nickname")
    @app_commands.describe(nickname="New nickname (leave empty to reset)")
    async def nick(self, interaction: discord.Interaction, nickname: str = None):
        try:
            await interaction.user.edit(nick=nickname)
            
            if nickname:
                embed = helpers.create_embed(
                    "Nickname Changed",
                    f"✅ Your nickname has been changed to **{nickname}**",
                    color=0x00ff00
                )
            else:
                embed = helpers.create_embed(
                    "Nickname Reset",
                    "✅ Your nickname has been reset",
                    color=0x00ff00
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            embed = helpers.create_embed(
                "Permission Error",
                "❌ I don't have permission to change your nickname",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # Essential Economy Commands (added to ensure they work within Discord's 100 command limit)
    @app_commands.command(name="balance", description="Check your balance")
    @app_commands.describe(user="User to check balance for")
    async def balance(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        try:
            balance = await db.get_balance(target.id, interaction.guild.id)
            embed = helpers.create_embed(
                f"💰 {target.display_name}'s Balance",
                helpers.format_currency(balance),
                color=0xFFD700
            )
            if target.avatar:
                embed.set_thumbnail(url=target.avatar.url)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to get balance: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="daily", description="Claim your daily coins")
    async def daily(self, interaction: discord.Interaction):
        try:
            from config import DAILY_REWARD
            can_claim = await db.can_daily(interaction.user.id, interaction.guild.id)
            if not can_claim:
                embed = helpers.create_embed(
                    "⏰ Daily Already Claimed",
                    "You've already claimed your daily reward! Come back tomorrow.",
                    color=0xFFAA00
                )
                await interaction.response.send_message(embed=embed)
                return
            await db.update_daily(interaction.user.id, interaction.guild.id)
            embed = helpers.create_embed(
                "🎁 Daily Reward Claimed",
                f"You received {helpers.format_currency(DAILY_REWARD)}!",
                color=0x00FF00
            )
            embed.add_field(name="Next Daily", value="Available in 24 hours", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to claim daily reward: {str(e)}", ephemeral=True)

    @app_commands.command(name="beg", description="Beg for money")
    async def beg(self, interaction: discord.Interaction):
        try:
            import random
            from config import BEG_MIN, BEG_MAX
            # Random chance of getting money
            if random.random() < 0.7:  # 70% success rate
                amount = random.randint(BEG_MIN, BEG_MAX)
                await db.update_balance(interaction.user.id, interaction.guild.id, amount)
                
                responses = [
                    f"A kind stranger gave you {helpers.format_currency(amount)}!",
                    f"You found {helpers.format_currency(amount)} on the ground!",
                    f"Someone felt sorry for you and gave you {helpers.format_currency(amount)}!",
                    f"A generous person donated {helpers.format_currency(amount)}!"
                ]
                
                embed = helpers.create_embed(
                    "🙏 Begging Success",
                    random.choice(responses),
                    color=0x00FF00
                )
            else:
                responses = [
                    "Nobody gave you anything. Try again later!",
                    "People ignored you completely.",
                    "A dog stole your cardboard sign!",
                    "Security chased you away!"
                ]
                
                embed = helpers.create_embed(
                    "🙏 Begging Failed",
                    random.choice(responses),
                    color=0xFF0000
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to beg: {str(e)}", ephemeral=True)

    @app_commands.command(name="shop", description="View the economy shop")
    async def shop(self, interaction: discord.Interaction):
        shop_items = {
            "cookie": {"price": 50, "description": "A delicious chocolate chip cookie 🍪"},
            "coffee": {"price": 100, "description": "Premium energizing coffee ☕"},
            "pizza": {"price": 250, "description": "Hot pepperoni pizza slice 🍕"},
            "burger": {"price": 200, "description": "Juicy cheeseburger with fries 🍔"},
            "phone": {"price": 1500, "description": "Latest smartphone with AI assistant 📱"},
            "car": {"price": 50000, "description": "Luxury sports car with turbo engine 🚗"},
            "mansion": {"price": 2000000, "description": "Luxury mansion with pool and garden 🏰"},
            "rocket": {"price": 50000000, "description": "Space rocket for interstellar travel 🚀"}
        }
        
        embed = helpers.create_embed(
            "🛒 Economy Shop",
            "Available items for purchase:",
            color=0x0099FF
        )
        
        for item_name, item_data in shop_items.items():
            embed.add_field(
                name=f"{item_name.title()}",
                value=f"{item_data['description']}\n**Price:** {helpers.format_currency(item_data['price'])}",
                inline=True
            )
        
        embed.set_footer(text="Buy items using the economy bot commands")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="give", description="Give coins to a user (Owner only)")
    @app_commands.describe(user="User to give coins to", amount="Amount to give")
    async def give(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        # Check if user is owner
        from config import OWNER_ID
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ You can't give coins to bots.", ephemeral=True)
            return
        
        try:
            # Owner can give unlimited coins
            await db.update_balance(user.id, interaction.guild.id, amount)
            
            embed = helpers.create_embed(
                "💰 Owner Gift",
                f"**{user.display_name}** received {helpers.format_currency(amount)} from the bot owner!",
                color=0x00FF00
            )
            embed.add_field(
                name="New Balance", 
                value=f"{helpers.format_currency(await db.get_balance(user.id, interaction.guild.id))}", 
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to give coins: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CoreGeneralCog(bot))
