import discord
from discord.ext import commands
from database import Database
from utils import format_message, create_embed
import logging

logger = logging.getLogger('discord')

class BotEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database):
        self.bot = bot
        self.db = db
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            settings = self.db.get_server_settings(member.guild.id)
            
            if not settings.get("welcome_enabled", True):
                return
            
            welcome_channel_name = settings.get("welcome_channel", "welcome")
            channel = discord.utils.get(member.guild.text_channels, name=welcome_channel_name)
            
            if not channel:
                logger.warning(f"Welcome channel '{welcome_channel_name}' not found in {member.guild.name}")
                return
            
            welcome_message = settings.get(
                "welcome_message",
                "Welcome to {server}, {mention}! 🎉"
            )
            embed_color = settings.get("embed_color", 0x00ff00)
            
            formatted_message = format_message(welcome_message, member, member.guild)
            
            embed = create_embed(
                title="👋 Welcome!",
                description=formatted_message,
                color=embed_color
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            
            rules_channel_name = settings.get("rules_channel", "rules")
            rules_channel = discord.utils.get(member.guild.text_channels, name=rules_channel_name)
            
            if rules_channel:
                embed.add_field(
                    name="📜 Server Rules",
                    value=f"Please read {rules_channel.mention} to get started!",
                    inline=False
                )
            
            await channel.send(embed=embed)
            logger.info(f"Sent welcome message for {member.name} in {member.guild.name}")
            
        except discord.Forbidden:
            logger.error(f"Missing permissions to send welcome message in {member.guild.name}")
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try:
            settings = self.db.get_server_settings(member.guild.id)
            
            if not settings.get("goodbye_enabled", True):
                return
            
            welcome_channel_name = settings.get("welcome_channel", "welcome")
            channel = discord.utils.get(member.guild.text_channels, name=welcome_channel_name)
            
            if not channel:
                logger.warning(f"Goodbye channel '{welcome_channel_name}' not found in {member.guild.name}")
                return
            
            goodbye_message = settings.get(
                "goodbye_message",
                "{username} has left the server. We'll miss you! 👋"
            )
            embed_color = settings.get("embed_color", 0xff0000)
            
            formatted_message = format_message(goodbye_message, member, member.guild)
            
            embed = create_embed(
                title="👋 Goodbye",
                description=formatted_message,
                color=0xff6b6b
            )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await channel.send(embed=embed)
            logger.info(f"Sent goodbye message for {member.name} in {member.guild.name}")
            
        except discord.Forbidden:
            logger.error(f"Missing permissions to send goodbye message in {member.guild.name}")
        except Exception as e:
            logger.error(f"Error sending goodbye message: {str(e)}")

async def setup(bot: commands.Bot, db: Database):
    await bot.add_cog(BotEvents(bot, db))
