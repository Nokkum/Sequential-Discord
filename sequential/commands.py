import discord
from discord import app_commands
from discord.ext import commands
import time
from datetime import datetime
from database import Database
from utils import create_embed
from config import DEFAULT_EMBED_COLOR, BOT_VERSION

class BotCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database):
        self.bot = bot
        self.db = db
    
    @app_commands.command(name="ping", description="Check the bot's response time")
    async def ping(self, interaction: discord.Interaction):
        try:
            start = time.time()
            await interaction.response.defer()
            end = time.time()
            
            latency = round((end - start) * 1000, 2)
            ws_latency = round(self.bot.latency * 1000, 2)
            
            embed = create_embed(
                title="🏓 Pong!",
                description=f"**API Latency:** {latency}ms\n**WebSocket Latency:** {ws_latency}ms",
                color=DEFAULT_EMBED_COLOR
            )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        try:
            embed = create_embed(
                title="📚 Bot Commands",
                description="Here are all the commands you can use:",
                color=DEFAULT_EMBED_COLOR
            )
            
            embed.add_field(
                name="/ping",
                value="Check the bot's response time",
                inline=False
            )
            embed.add_field(
                name="/help",
                value="Show this help message",
                inline=False
            )
            embed.add_field(
                name="/serverinfo",
                value="Display information about this server",
                inline=False
            )
            embed.add_field(
                name="/userinfo [user]",
                value="Show information about a user (or yourself)",
                inline=False
            )
            embed.add_field(
                name="/setchannel",
                value="Set which channel to use for welcome/goodbye messages (Admin only)",
                inline=False
            )
            embed.add_field(
                name="/config",
                value="Configure bot messages and toggles (Admin only)",
                inline=False
            )
            
            embed.set_footer(text=f"Bot Version {BOT_VERSION}")
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="serverinfo", description="Display information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            
            embed = create_embed(
                title=f"📊 {guild.name}",
                description=f"Information about this server",
                color=DEFAULT_EMBED_COLOR
            )
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
            embed.add_field(name="Server ID", value=str(guild.id), inline=True)
            embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Members", value=str(guild.member_count), inline=True)
            embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
            embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="userinfo", description="Display information about a user")
    @app_commands.describe(user="The user to get information about (leave empty for yourself)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        try:
            target_user = user or interaction.user
            
            embed = create_embed(
                title=f"👤 {target_user.name}",
                description=f"Information about {target_user.mention}",
                color=target_user.color if target_user.color.value != 0 else DEFAULT_EMBED_COLOR
            )
            
            embed.set_thumbnail(url=target_user.display_avatar.url)
            
            embed.add_field(name="Username", value=str(target_user), inline=True)
            embed.add_field(name="User ID", value=str(target_user.id), inline=True)
            embed.add_field(name="Nickname", value=target_user.nick or "None", inline=True)
            embed.add_field(name="Account Created", value=f"<t:{int(target_user.created_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Joined Server", value=f"<t:{int(target_user.joined_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Roles", value=str(len(target_user.roles) - 1), inline=True)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="setchannel", description="Set which channel to use for welcome/goodbye messages")
    @app_commands.describe(
        channel_type="Which channel you want to set",
        channel="The channel to use"
    )
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Welcome/Goodbye Channel", value="welcome_channel"),
        app_commands.Choice(name="Rules Channel", value="rules_channel")
    ])
    @app_commands.default_permissions(administrator=True)
    async def setchannel(self, interaction: discord.Interaction, channel_type: str, channel: discord.TextChannel):
        try:
            self.db.update_server_setting(interaction.guild.id, channel_type, channel.name)
            
            channel_name = "Welcome/Goodbye" if channel_type == "welcome_channel" else "Rules"
            
            embed = create_embed(
                title="✅ Channel Updated",
                description=f"**{channel_name} channel** set to {channel.mention}",
                color=DEFAULT_EMBED_COLOR
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="config", description="Configure bot settings for this server")
    @app_commands.describe(
        setting="The setting to configure",
        value="The new value for the setting"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="Welcome Message", value="welcome_message"),
        app_commands.Choice(name="Goodbye Message", value="goodbye_message"),
        app_commands.Choice(name="Welcome Enabled", value="welcome_enabled"),
        app_commands.Choice(name="Goodbye Enabled", value="goodbye_enabled")
    ])
    @app_commands.default_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction, setting: str, value: str):
        try:
            if setting in ["welcome_enabled", "goodbye_enabled"]:
                value_bool = value.lower() in ["true", "yes", "1", "on", "enabled"]
                self.db.update_server_setting(interaction.guild.id, setting, value_bool)
                await interaction.response.send_message(
                    f"✅ Updated **{setting}** to **{value_bool}**",
                    ephemeral=True
                )
            else:
                self.db.update_server_setting(interaction.guild.id, setting, value)
                await interaction.response.send_message(
                    f"✅ Updated **{setting}** to **{value}**",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot, db: Database):
    await bot.add_cog(BotCommands(bot, db))
