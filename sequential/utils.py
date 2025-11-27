import discord
from datetime import datetime

def format_message(template: str, member: discord.Member, guild: discord.Guild) -> str:
    replacements = {
        "{mention}": member.mention,
        "{username}": member.name,
        "{user}": member.name,
        "{server}": guild.name,
        "{server_name}": guild.name,
        "{member_count}": str(guild.member_count)
    }
    
    message = template
    for key, value in replacements.items():
        message = message.replace(key, value)
    
    return message

def create_embed(title: str, description: str, color: int, footer: str = None) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed
