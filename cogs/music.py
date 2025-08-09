import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import os
from utils.helpers import helpers
from database import db
from config import MUSIC_VOLUME, MAX_QUEUE_SIZE

# yt-dlp options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog
        
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        
        self.current = None
        self.volume = MUSIC_VOLUME
        self.loop_mode = 'off'  # 'off', 'track', 'queue'
        self.is_playing = False
        
        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Main player loop"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            self.next.clear()
            
            try:
                # Wait for next song with 5 minute timeout
                async with asyncio.timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                # Disconnect if no song for 5 minutes
                if self.guild.voice_client:
                    await self.guild.voice_client.disconnect()
                return

            if not isinstance(source, YTDLSource):
                continue

            source.volume = self.volume
            self.current = source
            self.is_playing = True
            
            if self.guild.voice_client:
                self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                
                embed = helpers.create_embed(
                    "🎵 Now Playing",
                    f"**{source.title}**",
                    color=0x00ff00
                )
                if source.uploader:
                    embed.add_field(name="Uploader", value=source.uploader, inline=True)
                if source.duration:
                    embed.add_field(name="Duration", value=helpers.format_time(source.duration), inline=True)
                
                await self.channel.send(embed=embed)
                
                await self.next.wait()
                
                # Handle loop modes
                if self.loop_mode == 'track':
                    # Re-add current track to queue
                    await self.queue.put(source)
                elif self.loop_mode == 'queue':
                    # Re-add current track to end of queue
                    await self.queue.put(source)
                
                source.cleanup()
                self.current = None
                self.is_playing = False

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, ctx):
        """Get music player for guild"""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    @app_commands.command(name="play", description="Play music from YouTube or Spotify")
    @app_commands.describe(song="Song name, YouTube URL, or Spotify URL")
    async def play(self, interaction: discord.Interaction, song: str):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel to use music commands.", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        
        # Check bot permissions
        permissions = voice_channel.permissions_for(interaction.guild.me)
        if not permissions.connect or not permissions.speak:
            await interaction.response.send_message("❌ I need permission to connect and speak in that voice channel.", ephemeral=True)
            return

        await interaction.response.defer()

        # Connect to voice channel
        if not interaction.guild.voice_client:
            try:
                await voice_channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ Failed to connect to voice channel: {str(e)}")
                return
        elif interaction.guild.voice_client.channel != voice_channel:
            await interaction.guild.voice_client.move_to(voice_channel)

        try:
            # Get player
            player = self.get_player(interaction)
            
            # Check queue size
            if player.queue.qsize() >= MAX_QUEUE_SIZE:
                await interaction.followup.send(f"❌ Queue is full! Maximum {MAX_QUEUE_SIZE} songs allowed.")
                return

            # Create source
            source = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
            
            # Add to queue
            await player.queue.put(source)
            
            if player.is_playing:
                embed = helpers.create_embed(
                    "🎵 Added to Queue",
                    f"**{source.title}** has been added to the queue.",
                    color=0x00ff00
                )
                embed.add_field(name="Position", value=f"{player.queue.qsize()}", inline=True)
                if source.duration:
                    embed.add_field(name="Duration", value=helpers.format_time(source.duration), inline=True)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("🎵 Starting playback...")

        except Exception as e:
            await interaction.followup.send(f"❌ Failed to play song: {str(e)}")

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await interaction.response.send_message("❌ Nothing is currently playing.", ephemeral=True)
            return

        interaction.guild.voice_client.pause()
        
        embed = helpers.create_embed(
            "⏸️ Paused",
            "Music has been paused.",
            color=0xffaa00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_paused():
            await interaction.response.send_message("❌ Music is not paused.", ephemeral=True)
            return

        interaction.guild.voice_client.resume()
        
        embed = helpers.create_embed(
            "▶️ Resumed",
            "Music has been resumed.",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="skip", description="Skip the current track")
    async def skip(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await interaction.response.send_message("❌ Nothing is currently playing.", ephemeral=True)
            return

        interaction.guild.voice_client.stop()
        
        embed = helpers.create_embed(
            "⏭️ Skipped",
            "Current track has been skipped.",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop", description="Stop music and clear queue")
    async def stop(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Bot is not connected to a voice channel.", ephemeral=True)
            return

        # Clear queue and stop
        if interaction.guild.id in self.players:
            player = self.players[interaction.guild.id]
            # Clear queue
            while not player.queue.empty():
                try:
                    player.queue.get_nowait()
                except:
                    break

        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()

        await interaction.guild.voice_client.disconnect()
        
        embed = helpers.create_embed(
            "⏹️ Stopped",
            "Music stopped and queue cleared.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="View the current song queue")
    async def queue(self, interaction: discord.Interaction):
        if interaction.guild.id not in self.players:
            await interaction.response.send_message("❌ No music player active.", ephemeral=True)
            return

        player = self.players[interaction.guild.id]
        
        if player.queue.empty() and not player.current:
            await interaction.response.send_message("❌ Queue is empty.", ephemeral=True)
            return

        embed = helpers.create_embed(
            "🎵 Music Queue",
            f"Showing queue for {interaction.guild.name}",
            color=0x0099ff
        )

        # Current song
        if player.current:
            embed.add_field(
                name="🎵 Currently Playing",
                value=f"**{player.current.title}**",
                inline=False
            )

        # Queue
        if not player.queue.empty():
            queue_list = list(player.queue._queue)
            queue_text = ""
            
            for i, song in enumerate(queue_list[:10], 1):
                queue_text += f"{i}. **{song.title}**\n"
            
            if len(queue_list) > 10:
                queue_text += f"...and {len(queue_list) - 10} more songs"
            
            embed.add_field(
                name=f"📜 Up Next ({player.queue.qsize()} songs)",
                value=queue_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📜 Up Next",
                value="Queue is empty",
                inline=False
            )

        # Loop mode
        embed.add_field(
            name="🔄 Loop Mode",
            value=player.loop_mode.title(),
            inline=True
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="Set music volume")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, interaction: discord.Interaction, volume: int):
        if volume < 0 or volume > 100:
            await interaction.response.send_message("❌ Volume must be between 0 and 100.", ephemeral=True)
            return

        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Bot is not connected to a voice channel.", ephemeral=True)
            return

        if interaction.guild.id in self.players:
            player = self.players[interaction.guild.id]
            player.volume = volume / 100
            
            if player.current:
                player.current.volume = player.volume

        embed = helpers.create_embed(
            "🔊 Volume Changed",
            f"Volume set to {volume}%",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle", description="Shuffle the queue")
    async def shuffle(self, interaction: discord.Interaction):
        if interaction.guild.id not in self.players:
            await interaction.response.send_message("❌ No music player active.", ephemeral=True)
            return

        player = self.players[interaction.guild.id]
        
        if player.queue.empty():
            await interaction.response.send_message("❌ Queue is empty.", ephemeral=True)
            return

        # Get queue items and shuffle
        import random
        queue_items = []
        while not player.queue.empty():
            try:
                queue_items.append(player.queue.get_nowait())
            except:
                break

        random.shuffle(queue_items)

        # Put items back
        for item in queue_items:
            await player.queue.put(item)

        embed = helpers.create_embed(
            "🔀 Queue Shuffled",
            f"Shuffled {len(queue_items)} songs in the queue.",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="Set loop mode")
    @app_commands.describe(mode="Loop mode: off, track, or queue")
    async def loop(self, interaction: discord.Interaction, mode: str):
        valid_modes = ['off', 'track', 'queue']
        if mode.lower() not in valid_modes:
            await interaction.response.send_message(f"❌ Invalid loop mode. Choose from: {', '.join(valid_modes)}", ephemeral=True)
            return

        if interaction.guild.id not in self.players:
            await interaction.response.send_message("❌ No music player active.", ephemeral=True)
            return

        player = self.players[interaction.guild.id]
        player.loop_mode = mode.lower()

        mode_emojis = {'off': '❌', 'track': '🔂', 'queue': '🔁'}
        
        embed = helpers.create_embed(
            f"{mode_emojis[mode.lower()]} Loop Mode Changed",
            f"Loop mode set to: **{mode.title()}**",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="voice_channel", description="Set the default voice channel for music")
    @app_commands.describe(channel="Voice channel to set as default for music")
    async def voice_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Set the voice channel to play music in"""
        if not helpers.has_permission(interaction.user, 'manage_channels'):
            await interaction.response.send_message("❌ You need Manage Channels permission to set the voice channel.", ephemeral=True)
            return
        
        try:
            # Store the voice channel setting in database
            await db.set_setting(interaction.guild.id, 'music_voice_channel', str(channel.id))
            
            embed = helpers.create_embed(
                "🎵 Voice Channel Set",
                f"Music voice channel set to **{channel.name}**\n"
                f"The bot will now automatically join this channel when playing music.",
                color=0x00ff00
            )
            embed.add_field(
                name="Channel Info", 
                value=f"ID: `{channel.id}`\nCategory: {channel.category.name if channel.category else 'None'}", 
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = helpers.create_embed(
                "❌ Error",
                f"Failed to set voice channel: {str(e)}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Auto-disconnect when alone in voice channel"""
        if member == self.bot.user:
            return

        voice_client = member.guild.voice_client
        if voice_client and voice_client.channel:
            # Check if bot is alone
            members = [m for m in voice_client.channel.members if not m.bot]
            if len(members) == 0:
                # Wait 30 seconds then disconnect if still alone
                await asyncio.sleep(30)
                members = [m for m in voice_client.channel.members if not m.bot]
                if len(members) == 0 and voice_client.is_connected():
                    await voice_client.disconnect()

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
