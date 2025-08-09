import discord
from discord.ext import commands
from discord import app_commands
from utils.helpers import helpers
from database import db
from config import OWNER_ID

class DMSystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dm_channel_cache = {}  # Guild ID -> Channel ID for DM replies
    
    @app_commands.command(name="dm", description="Send a private DM to a user")
    @app_commands.describe(user="User to send DM to", message="Message to send")
    async def dm(self, interaction: discord.Interaction, user: discord.Member, message: str):
        if not helpers.has_permission(interaction.user, 'manage_messages'):
            await interaction.response.send_message("❌ You need Manage Messages permission to send DMs.", ephemeral=True)
            return
        
        if len(message) > 1500:
            await interaction.response.send_message("❌ DM message must be 1500 characters or less.", ephemeral=True)
            return
        
        try:
            # Create DM embed
            embed = helpers.create_embed(
                f"📨 Message from {interaction.guild.name}",
                message,
                color=0x0099FF
            )
            embed.add_field(
                name="Sent by",
                value=f"{interaction.user.display_name} ({interaction.user})",
                inline=True
            )
            embed.add_field(
                name="Server",
                value=interaction.guild.name,
                inline=True
            )
            embed.set_footer(text="Reply using /dmreply if available")
            
            # Try to send DM
            dm_sent = await helpers.send_dm_safe(user, embed=embed)
            
            if dm_sent:
                # Log the DM
                await db.log_dm(interaction.user.id, user.id, message)
                
                # Confirm to sender
                confirm_embed = helpers.create_embed(
                    "✅ DM Sent",
                    f"Successfully sent DM to {user.mention}",
                    color=0x00FF00
                )
                confirm_embed.add_field(
                    name="Message Preview",
                    value=helpers.clean_content(message, 200),
                    inline=False
                )
                
                await interaction.response.send_message(embed=confirm_embed)
            else:
                await interaction.response.send_message(
                    f"❌ Could not send DM to {user.mention}. They may have DMs disabled or have blocked the bot.",
                    ephemeral=True
                )
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send DM: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="dmall", description="DM all users in current server")
    @app_commands.describe(message="Message to send to all users")
    async def dmall(self, interaction: discord.Interaction, message: str):
        if not helpers.has_permission(interaction.user, 'administrator'):
            await interaction.response.send_message("❌ You need Administrator permission to DM all users.", ephemeral=True)
            return
        
        if len(message) > 1500:
            await interaction.response.send_message("❌ DM message must be 1500 characters or less.", ephemeral=True)
            return
        
        # Confirmation
        confirm = await helpers.confirm_action(
            interaction,
            f"Are you sure you want to DM all {len(interaction.guild.members)} members in this server? This action cannot be undone."
        )
        
        if not confirm:
            await interaction.response.send_message("❌ DM broadcast cancelled.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Create DM embed
            embed = helpers.create_embed(
                f"📢 Announcement from {interaction.guild.name}",
                message,
                color=0xFF6600
            )
            embed.add_field(
                name="Sent by",
                value=f"{interaction.user.display_name} ({interaction.user})",
                inline=True
            )
            embed.add_field(
                name="Server",
                value=interaction.guild.name,
                inline=True
            )
            embed.set_footer(text="This is a server-wide announcement")
            
            # Send DMs to all members
            success_count = 0
            fail_count = 0
            
            for member in interaction.guild.members:
                if not member.bot and member != interaction.user:
                    dm_sent = await helpers.send_dm_safe(member, embed=embed)
                    if dm_sent:
                        success_count += 1
                        # Log the DM
                        await db.log_dm(interaction.user.id, member.id, f"[BROADCAST] {message}")
                    else:
                        fail_count += 1
            
            # Report results
            result_embed = helpers.create_embed(
                "📊 DM Broadcast Complete",
                f"**Successfully sent:** {success_count} DMs\n"
                f"**Failed to send:** {fail_count} DMs\n"
                f"**Total attempted:** {success_count + fail_count}",
                color=0x00FF00 if fail_count == 0 else 0xFFAA00
            )
            
            await interaction.followup.send(embed=result_embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to broadcast DMs: {str(e)}")
    
    @app_commands.command(name="dmallservers", description="DM all users across all servers (Owner only)")
    @app_commands.describe(message="Message to send to all users")
    async def dmallservers(self, interaction: discord.Interaction, message: str):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
            return
        
        if len(message) > 1500:
            await interaction.response.send_message("❌ DM message must be 1500 characters or less.", ephemeral=True)
            return
        
        # Count total users
        total_users = sum(len([m for m in guild.members if not m.bot]) for guild in self.bot.guilds)
        
        # Confirmation
        confirm = await helpers.confirm_action(
            interaction,
            f"Are you sure you want to DM {total_users} users across all {len(self.bot.guilds)} servers? This is a major action!"
        )
        
        if not confirm:
            await interaction.response.send_message("❌ Global DM broadcast cancelled.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Create DM embed
            embed = helpers.create_embed(
                "📢 Global Bot Announcement",
                message,
                color=0xFF0000
            )
            embed.add_field(
                name="From",
                value=f"Bot Owner: {interaction.user}",
                inline=True
            )
            embed.set_footer(text="This is a global announcement to all bot users")
            
            # Send DMs to all users across all guilds
            success_count = 0
            fail_count = 0
            processed_users = set()  # Avoid sending multiple DMs to same user
            
            for guild in self.bot.guilds:
                for member in guild.members:
                    if (not member.bot and 
                        member.id not in processed_users and 
                        member.id != interaction.user.id):
                        
                        processed_users.add(member.id)
                        dm_sent = await helpers.send_dm_safe(member, embed=embed)
                        
                        if dm_sent:
                            success_count += 1
                            # Log the DM
                            await db.log_dm(interaction.user.id, member.id, f"[GLOBAL] {message}")
                        else:
                            fail_count += 1
            
            # Report results
            result_embed = helpers.create_embed(
                "📊 Global DM Broadcast Complete",
                f"**Successfully sent:** {success_count} DMs\n"
                f"**Failed to send:** {fail_count} DMs\n"
                f"**Total unique users:** {success_count + fail_count}\n"
                f"**Servers reached:** {len(self.bot.guilds)}",
                color=0x00FF00 if fail_count == 0 else 0xFFAA00
            )
            
            await interaction.followup.send(embed=result_embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to broadcast global DMs: {str(e)}")
    
    @app_commands.command(name="setchannel", description="Set channel for DM replies to show")
    @app_commands.describe(channel="Channel where DM replies will be posted")
    async def setchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to set DM channel.", ephemeral=True)
            return
        
        try:
            # Check bot permissions in target channel
            permissions = channel.permissions_for(interaction.guild.me)
            if not permissions.send_messages or not permissions.embed_links:
                await interaction.response.send_message("❌ I need Send Messages and Embed Links permissions in that channel.", ephemeral=True)
                return
            
            # Save channel setting
            await db.set_setting(interaction.guild.id, 'dm_reply_channel', str(channel.id))
            self.dm_channel_cache[interaction.guild.id] = channel.id
            
            embed = helpers.create_embed(
                "✅ DM Channel Set",
                f"DM replies will now be posted in {channel.mention}",
                color=0x00FF00
            )
            embed.add_field(
                name="Note",
                value="When users reply to bot DMs, their messages will appear in this channel.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to set DM channel: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="dmreply", description="Reply to a DM (for users who received DMs)")
    @app_commands.describe(message="Your reply message")
    async def dmreply(self, interaction: discord.Interaction, message: str):
        # This command allows users to reply to DMs they received from the bot
        # The reply will be posted in the designated channel of the server
        
        if len(message) > 1000:
            await interaction.response.send_message("❌ Reply message must be 1000 characters or less.", ephemeral=True)
            return
        
        try:
            # Find which servers this user is in and try to post reply
            posted_count = 0
            
            for guild in self.bot.guilds:
                if interaction.user in guild.members:
                    # Get DM reply channel for this guild
                    dm_channel_id = await db.get_setting(guild.id, 'dm_reply_channel')
                    
                    if dm_channel_id:
                        try:
                            channel = guild.get_channel(int(dm_channel_id))
                            if channel:
                                embed = helpers.create_embed(
                                    "💬 DM Reply",
                                    message,
                                    color=0x0099FF
                                )
                                embed.add_field(
                                    name="From",
                                    value=f"{interaction.user.display_name} ({interaction.user})",
                                    inline=True
                                )
                                embed.add_field(
                                    name="User ID",
                                    value=str(interaction.user.id),
                                    inline=True
                                )
                                
                                if interaction.user.avatar:
                                    embed.set_thumbnail(url=interaction.user.avatar.url)
                                
                                await channel.send(embed=embed)
                                posted_count += 1
                        except:
                            continue
            
            if posted_count > 0:
                embed = helpers.create_embed(
                    "✅ Reply Sent",
                    f"Your reply has been posted to {posted_count} server(s).",
                    color=0x00FF00
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    "❌ No DM reply channels found. Ask a server admin to set up DM replies with `/setchannel`.",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send reply: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="dmlogs", description="View recent DM logs (Admin only)")
    @app_commands.describe(limit="Number of recent DMs to show (max 20)")
    async def dmlogs(self, interaction: discord.Interaction, limit: int = 10):
        if not helpers.has_permission(interaction.user, 'administrator'):
            await interaction.response.send_message("❌ You need Administrator permission to view DM logs.", ephemeral=True)
            return
        
        if limit < 1 or limit > 20:
            await interaction.response.send_message("❌ Limit must be between 1 and 20.", ephemeral=True)
            return
        
        try:
            # This would require additional database methods to get recent DMs
            # For now, show a placeholder
            embed = helpers.create_embed(
                "📊 DM Logs",
                "Recent DM activity (last 24 hours):",
                color=0x0099FF
            )
            embed.add_field(
                name="Note",
                value="DM logging system is active. Detailed logs would be shown here in a full implementation.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to get DM logs: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DMSystemCog(bot))
