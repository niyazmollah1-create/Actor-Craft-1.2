import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from utils.helpers import helpers
from database import db

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(user="User to kick", reason="Reason for kick")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        if not helpers.has_permission(interaction.user, 'kick_members'):
            await interaction.response.send_message("❌ You don't have permission to kick members.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.send_message("❌ I don't have permission to kick members.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot kick someone with a higher or equal role.", ephemeral=True)
            return
        
        if user.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ I cannot kick someone with a higher or equal role than me.", ephemeral=True)
            return
        
        try:
            # Send DM to user before kicking
            dm_embed = helpers.create_embed(
                f"Kicked from {interaction.guild.name}",
                f"**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=0xff6600
            )
            await helpers.send_dm_safe(user, embed=dm_embed)
            
            # Kick the user
            await user.kick(reason=f"{reason} (by {interaction.user})")
            
            # Log the action
            await db.add_warning(user.id, interaction.guild.id, f"KICKED: {reason}", interaction.user.id)
            
            embed = helpers.create_embed(
                "User Kicked",
                f"✅ **{user}** has been kicked.\n**Reason:** {reason}",
                color=0xff6600
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick this user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to kick user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(user="User to ban", reason="Reason for ban")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        if not helpers.has_permission(interaction.user, 'ban_members'):
            await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("❌ I don't have permission to ban members.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot ban someone with a higher or equal role.", ephemeral=True)
            return
        
        if user.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ I cannot ban someone with a higher or equal role than me.", ephemeral=True)
            return
        
        try:
            # Send DM to user before banning
            dm_embed = helpers.create_embed(
                f"Banned from {interaction.guild.name}",
                f"**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=0xff0000
            )
            await helpers.send_dm_safe(user, embed=dm_embed)
            
            # Ban the user
            await user.ban(reason=f"{reason} (by {interaction.user})", delete_message_days=1)
            
            # Log the action
            await db.add_warning(user.id, interaction.guild.id, f"BANNED: {reason}", interaction.user.id)
            
            embed = helpers.create_embed(
                "User Banned",
                f"✅ **{user}** has been banned.\n**Reason:** {reason}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban this user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to ban user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unban", description="Unban a user by ID")
    @app_commands.describe(user_id="User ID to unban")
    async def unban(self, interaction: discord.Interaction, user_id: str):
        if not helpers.has_permission(interaction.user, 'ban_members'):
            await interaction.response.send_message("❌ You don't have permission to unban members.", ephemeral=True)
            return
        
        try:
            user_id = int(user_id)
            user = await self.bot.fetch_user(user_id)
            
            await interaction.guild.unban(user)
            
            embed = helpers.create_embed(
                "User Unbanned",
                f"✅ **{user}** has been unbanned.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.NotFound:
            await interaction.response.send_message("❌ User is not banned or doesn't exist.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unban user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="tempban", description="Temporarily ban a user")
    @app_commands.describe(user="User to ban", duration="Duration (e.g., 1h, 30m, 1d)", reason="Reason for ban")
    async def tempban(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        if not helpers.has_permission(interaction.user, 'ban_members'):
            await interaction.response.send_message("❌ You don't have permission to ban members.", ephemeral=True)
            return
        
        # Parse duration
        ban_seconds = helpers.parse_time(duration)
        if ban_seconds == 0:
            await interaction.response.send_message("❌ Invalid duration format. Use formats like: 1h, 30m, 1d", ephemeral=True)
            return
        
        if ban_seconds > 2592000:  # 30 days max
            await interaction.response.send_message("❌ Maximum ban duration is 30 days.", ephemeral=True)
            return
        
        try:
            # Ban the user first
            dm_embed = helpers.create_embed(
                f"Temporarily Banned from {interaction.guild.name}",
                f"**Duration:** {duration}\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=0xff6600
            )
            await helpers.send_dm_safe(user, embed=dm_embed)
            
            await user.ban(reason=f"TEMPBAN ({duration}): {reason} (by {interaction.user})")
            
            embed = helpers.create_embed(
                "User Temporarily Banned",
                f"✅ **{user}** has been banned for {duration}.\n**Reason:** {reason}",
                color=0xff6600
            )
            await interaction.response.send_message(embed=embed)
            
            # Schedule unban
            await asyncio.sleep(ban_seconds)
            try:
                await interaction.guild.unban(user)
                
                # Send unban notification
                unban_embed = helpers.create_embed(
                    "Temporary Ban Expired",
                    f"**{user}** has been automatically unbanned after {duration}.",
                    color=0x00ff00
                )
                if interaction.channel:
                    await interaction.channel.send(embed=unban_embed)
                    
            except:
                pass  # User might have been manually unbanned
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to temporarily ban user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.describe(user="User to mute", duration="Duration (e.g., 10m, 1h)", reason="Reason for mute")
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        if not helpers.has_permission(interaction.user, 'manage_roles'):
            await interaction.response.send_message("❌ You don't have permission to mute members.", ephemeral=True)
            return
        
        # Parse duration
        mute_seconds = helpers.parse_time(duration)
        if mute_seconds == 0:
            await interaction.response.send_message("❌ Invalid duration format. Use formats like: 10m, 1h, 2h", ephemeral=True)
            return
        
        if mute_seconds > 2419200:  # 28 days max (Discord limit)
            await interaction.response.send_message("❌ Maximum mute duration is 28 days.", ephemeral=True)
            return
        
        try:
            # Use Discord's timeout feature
            until = discord.utils.utcnow() + timedelta(seconds=mute_seconds)
            await user.timeout(until, reason=f"{reason} (by {interaction.user})")
            
            # Send DM to user
            dm_embed = helpers.create_embed(
                f"Muted in {interaction.guild.name}",
                f"**Duration:** {duration}\n**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=0xffaa00
            )
            await helpers.send_dm_safe(user, embed=dm_embed)
            
            embed = helpers.create_embed(
                "User Muted",
                f"✅ **{user}** has been muted for {duration}.\n**Reason:** {reason}",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to mute this user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to mute user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.describe(user="User to unmute")
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        if not helpers.has_permission(interaction.user, 'manage_roles'):
            await interaction.response.send_message("❌ You don't have permission to unmute members.", ephemeral=True)
            return
        
        try:
            await user.timeout(None, reason=f"Unmuted by {interaction.user}")
            
            embed = helpers.create_embed(
                "User Unmuted",
                f"✅ **{user}** has been unmuted.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unmute this user.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unmute user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="purge", description="Bulk delete messages")
    @app_commands.describe(amount="Number of messages to delete (max 100)")
    async def purge(self, interaction: discord.Interaction, amount: int):
        if not helpers.has_permission(interaction.user, 'manage_messages'):
            await interaction.response.send_message("❌ You don't have permission to manage messages.", ephemeral=True)
            return
        
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
            return
        
        try:
            deleted = await interaction.channel.purge(limit=amount)
            
            embed = helpers.create_embed(
                "Messages Purged",
                f"✅ Deleted {len(deleted)} messages.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, delete_after=5)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to delete messages.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to purge messages: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="lock", description="Lock a channel")
    @app_commands.describe(channel="Channel to lock (optional)")
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not helpers.has_permission(interaction.user, 'manage_channels'):
            await interaction.response.send_message("❌ You don't have permission to manage channels.", ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        
        try:
            overwrite = target_channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = False
            await target_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            
            embed = helpers.create_embed(
                "Channel Locked",
                f"🔒 {target_channel.mention} has been locked.",
                color=0xff6600
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to manage this channel.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to lock channel: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unlock", description="Unlock a channel")
    @app_commands.describe(channel="Channel to unlock (optional)")
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not helpers.has_permission(interaction.user, 'manage_channels'):
            await interaction.response.send_message("❌ You don't have permission to manage channels.", ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        
        try:
            overwrite = target_channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = None
            await target_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            
            embed = helpers.create_embed(
                "Channel Unlocked",
                f"🔓 {target_channel.mention} has been unlocked.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to manage this channel.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unlock channel: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="slowmode", description="Set slowmode for a channel")
    @app_commands.describe(channel="Channel to set slowmode", duration="Duration in seconds (0 to disable)")
    async def slowmode(self, interaction: discord.Interaction, channel: discord.TextChannel, duration: int):
        if not helpers.has_permission(interaction.user, 'manage_channels'):
            await interaction.response.send_message("❌ You don't have permission to manage channels.", ephemeral=True)
            return
        
        if duration < 0 or duration > 21600:  # Discord's max is 6 hours
            await interaction.response.send_message("❌ Duration must be between 0 and 21600 seconds (6 hours).", ephemeral=True)
            return
        
        try:
            await channel.edit(slowmode_delay=duration)
            
            if duration == 0:
                embed = helpers.create_embed(
                    "Slowmode Disabled",
                    f"✅ Slowmode disabled in {channel.mention}.",
                    color=0x00ff00
                )
            else:
                embed = helpers.create_embed(
                    "Slowmode Enabled",
                    f"✅ Slowmode set to {duration} seconds in {channel.mention}.",
                    color=0xffaa00
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to manage this channel.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to set slowmode: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(user="User to warn", reason="Reason for warning")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not helpers.has_permission(interaction.user, 'manage_messages'):
            await interaction.response.send_message("❌ You don't have permission to warn members.", ephemeral=True)
            return
        
        try:
            await db.add_warning(user.id, interaction.guild.id, reason, interaction.user.id)
            
            # Send DM to user
            dm_embed = helpers.create_embed(
                f"Warning in {interaction.guild.name}",
                f"**Reason:** {reason}\n**Moderator:** {interaction.user}",
                color=0xffaa00
            )
            await helpers.send_dm_safe(user, embed=dm_embed)
            
            embed = helpers.create_embed(
                "User Warned",
                f"✅ **{user}** has been warned.\n**Reason:** {reason}",
                color=0xffaa00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to warn user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="warnings", description="View warnings for a user")
    @app_commands.describe(user="User to check warnings for")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        if not helpers.has_permission(interaction.user, 'manage_messages'):
            await interaction.response.send_message("❌ You don't have permission to view warnings.", ephemeral=True)
            return
        
        try:
            warnings = await db.get_warnings(user.id, interaction.guild.id)
            
            if not warnings:
                embed = helpers.create_embed(
                    "No Warnings",
                    f"**{user}** has no warnings.",
                    color=0x00ff00
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = helpers.create_embed(
                f"Warnings for {user}",
                f"Total warnings: {len(warnings)}",
                color=0xffaa00
            )
            
            for i, (reason, moderator_id, created_at) in enumerate(warnings[:10], 1):
                moderator = self.bot.get_user(moderator_id)
                mod_name = moderator.name if moderator else "Unknown"
                
                embed.add_field(
                    name=f"Warning #{i}",
                    value=f"**Reason:** {reason}\n**Moderator:** {mod_name}\n**Date:** {created_at}",
                    inline=False
                )
            
            if len(warnings) > 10:
                embed.set_footer(text=f"Showing 10 of {len(warnings)} warnings")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to get warnings: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="clearwarnings", description="Clear all warnings for a user")
    @app_commands.describe(user="User to clear warnings for")
    async def clearwarnings(self, interaction: discord.Interaction, user: discord.Member):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to clear warnings.", ephemeral=True)
            return
        
        try:
            await db.clear_warnings(user.id, interaction.guild.id)
            
            embed = helpers.create_embed(
                "Warnings Cleared",
                f"✅ All warnings cleared for **{user}**.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to clear warnings: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
