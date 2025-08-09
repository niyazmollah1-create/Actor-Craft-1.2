import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import aiohttp
from utils.helpers import helpers

class ImageManipulationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_avatar_bytes(self, user):
        """Get user avatar as bytes"""
        if not user.avatar:
            # Use default avatar
            avatar_url = user.default_avatar.url
        else:
            avatar_url = user.avatar.url
        
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                if response.status == 200:
                    return await response.read()
                return None
    
    def create_beautiful_meme(self, avatar_bytes):
        """Create 'beautiful' meme effect"""
        try:
            # Open avatar
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA')
            avatar = avatar.resize((200, 200))
            
            # Create base image
            base = Image.new('RGBA', (500, 400), (255, 255, 255, 255))
            
            # Add avatar
            base.paste(avatar, (150, 50), avatar)
            
            # Add text (simplified version - in production you'd use proper fonts)
            draw = ImageDraw.Draw(base)
            try:
                # Try to use a nice font, fallback to default
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            text = "OH IT'S BEAUTIFUL"
            draw.text((100, 300), text, fill=(0, 0, 0), font=font)
            
            # Save to bytes
            output = io.BytesIO()
            base.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to create beautiful meme: {str(e)}")
    
    def create_triggered_effect(self, avatar_bytes):
        """Create triggered GIF effect (static version)"""
        try:
            # Open avatar
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA')
            avatar = avatar.resize((200, 200))
            
            # Create red tinted version
            red_overlay = Image.new('RGBA', avatar.size, (255, 0, 0, 100))
            triggered = Image.alpha_composite(avatar, red_overlay)
            
            # Create base image
            base = Image.new('RGBA', (300, 300), (255, 255, 255, 255))
            base.paste(triggered, (50, 50), triggered)
            
            # Add "TRIGGERED" text
            draw = ImageDraw.Draw(base)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            draw.text((75, 260), "TRIGGERED", fill=(255, 0, 0), font=font)
            
            output = io.BytesIO()
            base.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to create triggered effect: {str(e)}")
    
    def invert_colors(self, avatar_bytes):
        """Invert avatar colors"""
        try:
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGB')
            
            # Invert colors
            inverted = Image.eval(avatar, lambda x: 255 - x)
            
            output = io.BytesIO()
            inverted.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to invert colors: {str(e)}")
    
    def blur_image(self, avatar_bytes):
        """Apply blur effect"""
        try:
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA')
            
            # Apply Gaussian blur
            blurred = avatar.filter(ImageFilter.GaussianBlur(radius=5))
            
            output = io.BytesIO()
            blurred.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to blur image: {str(e)}")
    
    def create_wanted_poster(self, avatar_bytes):
        """Create wanted poster effect"""
        try:
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA')
            avatar = avatar.resize((200, 200))
            
            # Create wanted poster background
            poster = Image.new('RGBA', (400, 500), (222, 184, 135, 255))  # Burlywood color
            
            # Add avatar
            poster.paste(avatar, (100, 100), avatar)
            
            # Add wanted text
            draw = ImageDraw.Draw(poster)
            try:
                big_font = ImageFont.truetype("arial.ttf", 50)
                small_font = ImageFont.truetype("arial.ttf", 20)
            except:
                big_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            draw.text((150, 20), "WANTED", fill=(0, 0, 0), font=big_font)
            draw.text((100, 350), "DEAD OR ALIVE", fill=(0, 0, 0), font=small_font)
            draw.text((150, 400), "$50,000", fill=(0, 0, 0), font=small_font)
            
            output = io.BytesIO()
            poster.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to create wanted poster: {str(e)}")
    
    def grayscale_image(self, avatar_bytes):
        """Convert to grayscale"""
        try:
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('L')
            
            output = io.BytesIO()
            avatar.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to convert to grayscale: {str(e)}")
    
    def sharpen_image(self, avatar_bytes):
        """Sharpen image"""
        try:
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA')
            
            # Apply sharpening filter
            sharpened = avatar.filter(ImageFilter.SHARPEN)
            
            output = io.BytesIO()
            sharpened.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to sharpen image: {str(e)}")
    
    def sepia_effect(self, avatar_bytes):
        """Apply sepia tone effect"""
        try:
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGB')
            
            # Convert to sepia
            pixels = avatar.load()
            width, height = avatar.size
            
            for py in range(height):
                for px in range(width):
                    r, g, b = pixels[px, py]
                    
                    # Sepia formula
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    
                    # Clamp values
                    tr = min(255, tr)
                    tg = min(255, tg)
                    tb = min(255, tb)
                    
                    pixels[px, py] = (tr, tg, tb)
            
            output = io.BytesIO()
            avatar.save(output, format='PNG')
            output.seek(0)
            return output
            
        except Exception as e:
            raise Exception(f"Failed to apply sepia effect: {str(e)}")
    
    @app_commands.command(name="beautiful", description="Make a user's avatar 'beautiful'")
    @app_commands.describe(user="User to beautify")
    async def beautiful(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.create_beautiful_meme(avatar_bytes)
            
            file = discord.File(result, filename="beautiful.png")
            embed = helpers.create_embed(
                "✨ Beautiful!",
                f"Oh, {target.display_name} is beautiful! 💖",
                color=0xFF69B4
            )
            embed.set_image(url="attachment://beautiful.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to create beautiful meme: {str(e)}")
    
    @app_commands.command(name="triggered", description="Make a triggered version of user's avatar")
    @app_commands.describe(user="User to trigger")
    async def triggered(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.create_triggered_effect(avatar_bytes)
            
            file = discord.File(result, filename="triggered.png")
            embed = helpers.create_embed(
                "😡 TRIGGERED!",
                f"{target.display_name} has been triggered!",
                color=0xFF0000
            )
            embed.set_image(url="attachment://triggered.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to create triggered effect: {str(e)}")
    
    @app_commands.command(name="invert", description="Invert user's avatar colors")
    @app_commands.describe(user="User to invert")
    async def invert(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.invert_colors(avatar_bytes)
            
            file = discord.File(result, filename="inverted.png")
            embed = helpers.create_embed(
                "🔄 Color Inverted",
                f"Inverted {target.display_name}'s avatar colors!",
                color=0x9932CC
            )
            embed.set_image(url="attachment://inverted.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to invert colors: {str(e)}")
    
    @app_commands.command(name="blur", description="Apply blur effect to user's avatar")
    @app_commands.describe(user="User to blur")
    async def blur(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.blur_image(avatar_bytes)
            
            file = discord.File(result, filename="blurred.png")
            embed = helpers.create_embed(
                "🌫️ Blurred",
                f"Applied blur effect to {target.display_name}'s avatar!",
                color=0x87CEEB
            )
            embed.set_image(url="attachment://blurred.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to blur image: {str(e)}")
    
    @app_commands.command(name="wanted", description="Create a wanted poster with user's avatar")
    @app_commands.describe(user="User for wanted poster")
    async def wanted(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.create_wanted_poster(avatar_bytes)
            
            file = discord.File(result, filename="wanted.png")
            embed = helpers.create_embed(
                "🤠 WANTED",
                f"{target.display_name} is now wanted! 💰",
                color=0xDEB887
            )
            embed.set_image(url="attachment://wanted.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to create wanted poster: {str(e)}")
    
    @app_commands.command(name="grayscale", description="Convert user's avatar to grayscale")
    @app_commands.describe(user="User to convert")
    async def grayscale(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.grayscale_image(avatar_bytes)
            
            file = discord.File(result, filename="grayscale.png")
            embed = helpers.create_embed(
                "⚫ Grayscale",
                f"Converted {target.display_name}'s avatar to grayscale!",
                color=0x808080
            )
            embed.set_image(url="attachment://grayscale.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to convert to grayscale: {str(e)}")
    
    @app_commands.command(name="sharpen", description="Sharpen user's avatar")
    @app_commands.describe(user="User to sharpen")
    async def sharpen(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.sharpen_image(avatar_bytes)
            
            file = discord.File(result, filename="sharpened.png")
            embed = helpers.create_embed(
                "🔪 Sharpened",
                f"Sharpened {target.display_name}'s avatar!",
                color=0xC0C0C0
            )
            embed.set_image(url="attachment://sharpened.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to sharpen image: {str(e)}")
    
    @app_commands.command(name="sepia", description="Apply sepia tone to user's avatar")
    @app_commands.describe(user="User to apply sepia effect")
    async def sepia(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        
        await interaction.response.defer()
        
        try:
            avatar_bytes = await self.get_avatar_bytes(target)
            if not avatar_bytes:
                await interaction.followup.send("❌ Could not get user avatar.")
                return
            
            result = self.sepia_effect(avatar_bytes)
            
            file = discord.File(result, filename="sepia.png")
            embed = helpers.create_embed(
                "🟤 Sepia Tone",
                f"Applied sepia effect to {target.display_name}'s avatar!",
                color=0xDEB887
            )
            embed.set_image(url="attachment://sepia.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to apply sepia effect: {str(e)}")

async def setup(bot):
    await bot.add_cog(ImageManipulationCog(bot))
