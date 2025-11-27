import discord
import os
import asyncio
import logging
from discord.ext import commands
from database import Database
from config import DEFAULT_PREFIX
from cryptography.fernet import Fernet

BASE_DIR = os.path.join(os.getcwd(), ".sequential")
CATEGORIES = ["tokens", "apis"]


def ensure_dirs():
    """Ensure that the folder structure exists."""
    for category in CATEGORIES:
        for sub in ["encrypted", "key"]:
            os.makedirs(os.path.join(BASE_DIR, category, sub), exist_ok=True)


def get_paths(category: str, provider: str):
    """
    Get the paths for encrypted token/key files.
    Args:
        category (str): 'tokens' or 'apis'
        provider (str): e.g., 'discord', 'handler', 'google'
    Returns:
        (token_file, key_file)
    """
    ensure_dirs()
    category = category.lower()
    provider = provider.lower()

    if category not in CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Must be one of {CATEGORIES}.")

    enc_dir = os.path.join(BASE_DIR, category, "encrypted")
    key_dir = os.path.join(BASE_DIR, category, "key")

    token_file = os.path.join(enc_dir, f".{provider}.token")
    key_file = os.path.join(key_dir, f".{provider}.key")

    return token_file, key_file


def generate_key(key_file: str) -> bytes:
    """Generate a new Fernet key if missing, otherwise load existing one."""
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    with open(key_file, "rb") as f:
        return f.read()


def get_cipher(key_file: str) -> Fernet:
    """Return a Fernet cipher object for the given key file."""
    key = generate_key(key_file)
    return Fernet(key)


def save_secret(value: str, category: str, provider: str):
    """
    Encrypt and save a secret (token/API key).
    Args:
        value (str): the secret value
        category (str): 'tokens' or 'apis'
        provider (str): provider name (e.g., Discord, Handler, Google)
    """
    token_file, key_file = get_paths(category, provider)
    cipher = get_cipher(key_file)
    encrypted = cipher.encrypt(value.strip().encode("utf-8"))
    with open(token_file, "wb") as f:
        f.write(encrypted)


def load_secret(category: str, provider: str) -> str:
    """
    Decrypt and load a saved secret (token/API key).
    Args:
        category (str): 'tokens' or 'apis'
        provider (str): provider name
    Returns:
        str: decrypted secret
    Raises:
        RuntimeError: if no secret found or decryption fails
    """
    token_file, key_file = get_paths(category, provider)

    env_var = f"{provider.upper()}_{category[:-1].upper()}"  # e.g., DISCORD_TOKEN or HANDLER_TOKEN
    env_value = os.getenv(env_var)
    if env_value:
        return env_value.strip()

    if os.path.exists(token_file):
        try:
            cipher = get_cipher(key_file)
            with open(token_file, "rb") as f:
                encrypted = f.read()
            return cipher.decrypt(encrypted).decode("utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to decrypt {provider} {category[:-1]}: {e}")

    raise RuntimeError(
        f"{provider.capitalize()} {category[:-1]} not found. "
        f"Please save it first via the GUI or set {env_var} environment variable."
    )

def get_token(provider: str = "discord") -> str:
    """Retrieve a Discord or other bot token."""
    return load_secret("tokens", provider)


def get_api_key(provider: str = "handler") -> str:
    """Retrieve an API key (for Handler, Google, OpenAI, etc.)."""
    return load_secret("apis", provider)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=DEFAULT_PREFIX, intents=intents)
db = Database()

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")
    
    try:
        await load_extensions()
        await sync_commands()
        logger.info("Bot is ready!")
        print(f"Logged in as {bot.user}")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

async def load_extensions():
    try:
        import commands as bot_commands
        import events as bot_events
        
        await bot_commands.setup(bot, db)
        await bot_events.setup(bot, db)
        
        logger.info("Successfully loaded all extensions")
    except Exception as e:
        logger.error(f"Failed to load extensions: {e}")
        raise

async def sync_commands():
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    else:
        logger.error(f"Unhandled error: {error}")
        await ctx.send(f"❌ An error occurred: {str(error)}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
    else:
        logger.error(f"Unhandled app command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"❌ An error occurred: {str(error)}",
                ephemeral=True
            )

async def main():
    async with bot:
        token = get_token()
        if not token:
            logger.error("No TOKEN found in environment variables!")
            return
        
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.error("Invalid token provided!")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
