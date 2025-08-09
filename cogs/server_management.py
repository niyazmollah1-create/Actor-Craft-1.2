import discord
from discord.ext import commands
from discord import app_commands
from utils.helpers import helpers
from database import db

class ServerManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="setprefix", description="Change command prefix (if used)")
    @app_commands.describe(prefix="New command prefix")
    async def setprefix(self, interaction: discord.Interaction, prefix: str):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to change the prefix.", ephemeral=True)
            return
        
        if len(prefix) > 5:
            await interaction.response.send_message("❌ Prefix must be 5 characters or less.", ephemeral=True)
            return
        
        try:
            await db.set_setting(interaction.guild.id, 'prefix', prefix)
            
            embed = helpers.create_embed(
                "Prefix Changed",
                f"✅ Server prefix changed to: `{prefix}`",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to change prefix: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="autorole", description="Auto-assign role to new members")
    @app_commands.describe(role="Role to automatically assign to new members")
    async def autorole(self, interaction: discord.Interaction, role: discord.Role):
        if not helpers.has_permission(interaction.user, 'manage_roles'):
            await interaction.response.send_message("❌ You need Manage Roles permission to set autorole.", ephemeral=True)
            return
        
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message("❌ I cannot assign a role that is higher than or equal to my highest role.", ephemeral=True)
            return
        
        try:
            await db.set_setting(interaction.guild.id, 'autorole', str(role.id))
            
            embed = helpers.create_embed(
                "Autorole Set",
                f"✅ New members will automatically receive the {role.mention} role.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to set autorole: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="welcomechannel", description="Set welcome message channel")
    @app_commands.describe(channel="Channel for welcome messages")
    async def welcomechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to set welcome channel.", ephemeral=True)
            return
        
        try:
            await db.set_setting(interaction.guild.id, 'welcome_channel', str(channel.id))
            
            embed = helpers.create_embed(
                "Welcome Channel Set",
                f"✅ Welcome messages will be sent to {channel.mention}.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to set welcome channel: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="goodbyechannel", description="Set goodbye message channel")
    @app_commands.describe(channel="Channel for goodbye messages")
    async def goodbyechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to set goodbye channel.", ephemeral=True)
            return
        
        try:
            await db.set_setting(interaction.guild.id, 'goodbye_channel', str(channel.id))
            
            embed = helpers.create_embed(
                "Goodbye Channel Set",
                f"✅ Goodbye messages will be sent to {channel.mention}.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to set goodbye channel: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="welcomemessage", description="Set custom welcome message")
    @app_commands.describe(message="Welcome message (use {user} for mention, {server} for server name)")
    async def welcomemessage(self, interaction: discord.Interaction, message: str):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to set welcome message.", ephemeral=True)
            return
        
        if len(message) > 1000:
            await interaction.response.send_message("❌ Welcome message must be 1000 characters or less.", ephemeral=True)
            return
        
        try:
            await db.set_setting(interaction.guild.id, 'welcome_message', message)
            
            # Show preview
            preview = message.replace('{user}', interaction.user.mention).replace('{server}', interaction.guild.name)
            
            embed = helpers.create_embed(
                "Welcome Message Set",
                f"✅ Welcome message updated!\n\n**Preview:**\n{preview}",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to set welcome message: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="goodbyemessage", description="Set custom goodbye message")
    @app_commands.describe(message="Goodbye message (use {user} for username, {server} for server name)")
    async def goodbyemessage(self, interaction: discord.Interaction, message: str):
        if not helpers.has_permission(interaction.user, 'manage_guild'):
            await interaction.response.send_message("❌ You need Manage Server permission to set goodbye message.", ephemeral=True)
            return
        
        if len(message) > 1000:
            await interaction.response.send_message("❌ Goodbye message must be 1000 characters or less.", ephemeral=True)
            return
        
        try:
            await db.set_setting(interaction.guild.id, 'goodbye_message', message)
            
            # Show preview
            preview = message.replace('{user}', interaction.user.display_name).replace('{server}', interaction.guild.name)
            
            embed = helpers.create_embed(
                "Goodbye Message Set",
                f"✅ Goodbye message updated!\n\n**Preview:**\n{preview}",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to set goodbye message: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="addrole", description="Add a role to a user")
    @app_commands.describe(user="User to add role to", role="Role to add")
    async def addrole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if not helpers.has_permission(interaction.user, 'manage_roles'):
            await interaction.response.send_message("❌ You need Manage Roles permission to add roles.", ephemeral=True)
            return
        
        if role.position >= interaction.user.top_role.position and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot assign a role higher than or equal to your highest role.", ephemeral=True)
            return
        
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message("❌ I cannot assign a role higher than or equal to my highest role.", ephemeral=True)
            return
        
        if role in user.roles:
            await interaction.response.send_message(f"❌ {user.mention} already has the {role.mention} role.", ephemeral=True)
            return
        
        try:
            await user.add_roles(role, reason=f"Added by {interaction.user}")
            
            embed = helpers.create_embed(
                "Role Added",
                f"✅ Added {role.mention} to {user.mention}.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to add this role.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to add role: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="removerole", description="Remove a role from a user")
    @app_commands.describe(user="User to remove role from", role="Role to remove")
    async def removerole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        if not helpers.has_permission(interaction.user, 'manage_roles'):
            await interaction.response.send_message("❌ You need Manage Roles permission to remove roles.", ephemeral=True)
            return
        
        if role.position >= interaction.user.top_role.position and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot remove a role higher than or equal to your highest role.", ephemeral=True)
            return
        
        if role not in user.roles:
            await interaction.response.send_message(f"❌ {user.mention} doesn't have the {role.mention} role.", ephemeral=True)
            return
        
        try:
            await user.remove_roles(role, reason=f"Removed by {interaction.user}")
            
            embed = helpers.create_embed(
                "Role Removed",
                f"✅ Removed {role.mention} from {user.mention}.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to remove this role.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to remove role: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="createrole", description="Create a new role")
    @app_commands.describe(name="Role name", color="Hex color code (optional)")
    async def createrole(self, interaction: discord.Interaction, name: str, color: str = None):
        if not helpers.has_permission(interaction.user, 'manage_roles'):
            await interaction.response.send_message("❌ You need Manage Roles permission to create roles.", ephemeral=True)
            return
        
        if len(name) > 100:
            await interaction.response.send_message("❌ Role name must be 100 characters or less.", ephemeral=True)
            return
        
        # Parse color
        role_color = discord.Color.default()
        if color:
            try:
                if color.startswith('#'):
                    color = color[1:]
                role_color = discord.Color(int(color, 16))
            except ValueError:
                await interaction.response.send_message("❌ Invalid color format. Use hex format like #FF5733", ephemeral=True)
                return
        
        try:
            new_role = await interaction.guild.create_role(
                name=name,
                color=role_color,
                reason=f"Created by {interaction.user}"
            )
            
            embed = helpers.create_embed(
                "Role Created",
                f"✅ Created role {new_role.mention}",
                color=role_color if role_color != discord.Color.default() else 0x00ff00
            )
            embed.add_field(
                name="Details",
                value=f"**Name:** {name}\n**ID:** {new_role.id}\n**Color:** {str(role_color)}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create roles.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to create role: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="deleterole", description="Delete a role")
    @app_commands.describe(role="Role to delete")
    async def deleterole(self, interaction: discord.Interaction, role: discord.Role):
        if not helpers.has_permission(interaction.user, 'manage_roles'):
            await interaction.response.send_message("❌ You need Manage Roles permission to delete roles.", ephemeral=True)
            return
        
        if role.position >= interaction.user.top_role.position and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot delete a role higher than or equal to your highest role.", ephemeral=True)
            return
        
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message("❌ I cannot delete a role higher than or equal to my highest role.", ephemeral=True)
            return
        
        if role == interaction.guild.default_role:
            await interaction.response.send_message("❌ You cannot delete the @everyone role.", ephemeral=True)
            return
        
        # Confirmation
        confirm = await helpers.confirm_action(
            interaction, 
            f"Are you sure you want to delete the role **{role.name}**? This action cannot be undone."
        )
        
        if not confirm:
            await interaction.response.send_message("❌ Role deletion cancelled.", ephemeral=True)
            return
        
        try:
            role_name = role.name
            await role.delete(reason=f"Deleted by {interaction.user}")
            
            embed = helpers.create_embed(
                "Role Deleted",
                f"✅ Deleted role **{role_name}**.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to delete this role.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to delete role: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="setnickname", description="Change another user's nickname")
    @app_commands.describe(user="User to change nickname", nickname="New nickname (leave empty to reset)")
    async def setnickname(self, interaction: discord.Interaction, user: discord.Member, nickname: str = None):
        if not helpers.has_permission(interaction.user, 'manage_nicknames'):
            await interaction.response.send_message("❌ You need Manage Nicknames permission to change nicknames.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ You cannot change the nickname of someone with a higher or equal role.", ephemeral=True)
            return
        
        if user.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ I cannot change the nickname of someone with a higher or equal role than me.", ephemeral=True)
            return
        
        try:
            old_nick = user.display_name
            await user.edit(nick=nickname, reason=f"Changed by {interaction.user}")
            
            if nickname:
                embed = helpers.create_embed(
                    "Nickname Changed",
                    f"✅ Changed {user.mention}'s nickname from **{old_nick}** to **{nickname}**.",
                    color=0x00ff00
                )
            else:
                embed = helpers.create_embed(
                    "Nickname Reset",
                    f"✅ Reset {user.mention}'s nickname (was **{old_nick}**).",
                    color=0x00ff00
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to change this user's nickname.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to change nickname: {str(e)}", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle new member joins"""
        guild = member.guild
        
        # Auto-assign role if set
        autorole_id = await db.get_setting(guild.id, 'autorole')
        if autorole_id:
            try:
                role = guild.get_role(int(autorole_id))
                if role and role.position < guild.me.top_role.position:
                    await member.add_roles(role, reason="Autorole")
            except:
                pass
        
        # Send welcome message if channel is set
        welcome_channel_id = await db.get_setting(guild.id, 'welcome_channel')
        if welcome_channel_id:
            try:
                channel = guild.get_channel(int(welcome_channel_id))
                if channel:
                    welcome_msg = await db.get_setting(guild.id, 'welcome_message')
                    if not welcome_msg:
                        welcome_msg = "Welcome to {server}, {user}! 🎉"
                    
                    message = welcome_msg.replace('{user}', member.mention).replace('{server}', guild.name)
                    
                    embed = helpers.create_embed(
                        "Welcome!",
                        message,
                        color=0x00ff00
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                    
                    await channel.send(embed=embed)
            except:
                pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Handle member leaves"""
        guild = member.guild
        
        # Send goodbye message if channel is set
        goodbye_channel_id = await db.get_setting(guild.id, 'goodbye_channel')
        if goodbye_channel_id:
            try:
                channel = guild.get_channel(int(goodbye_channel_id))
                if channel:
                    goodbye_msg = await db.get_setting(guild.id, 'goodbye_message')
                    if not goodbye_msg:
                        goodbye_msg = "Goodbye {user}! Thanks for being part of {server}. 👋"
                    
                    message = goodbye_msg.replace('{user}', member.display_name).replace('{server}', guild.name)
                    
                    embed = helpers.create_embed(
                        "Goodbye",
                        message,
                        color=0xff6600
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                    
                    await channel.send(embed=embed)
            except:
                pass

async def setup(bot):
    await bot.add_cog(ServerManagementCog(bot))
