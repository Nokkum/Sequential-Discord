<h1 align="center">Sequential-Bot</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue" alt="Python 3.11">
</p>
<p align="center">
 Sequential is a Discord bot framework that was built for modularity, database integration, and secure token handling.
</p>


## Recent Changes

**Rollback Update**
- Reverted the changes lf `credential_handler.py` back to `token_sidebar.py`

**November 1, 2025 (v2.1):** Minor Update
- Added the `token_sidebar.py` which adds a GUI for the placement of tokens, acts like the `secrets` in local storage
- Added the `.token` file which holds the encrypted bot tokens
- Added the `.token.key` file which is the encryption key to the `.token` file

**October 31, 2025 (v2.0):** Major feature update
- ✨ Added beautiful embed-based welcome and goodbye messages
- 💾 Implemented JSON-based database for persistent server settings
- 🎨 Added customizable welcome/goodbye messages with variable support
- 🔧 Implemented slash commands: `/help`, `/ping`, `/serverinfo`, `/userinfo`, `/config`
- 🛡️ Added Comprehensive error handling throughout the codebase
- 🗂️ Restructured code into modular files (bot.py, commands.py, events.py, database.py, utils.py, config.py)
- 👋 Added goodbye messages when members leave
- ⚙️ Added admin configuration command to customize bot behavior per server


## Project Structure
```
.
│
└─ sequential/
  ├── bot.py                  # Main bot file and initialization
  ├── commands.py             # Slash commands (help, ping, serverinfo, etc.)
  ├── events.py               # Event handlers (welcome, goodbye)
  ├── database.py             # JSON-based database manager
  ├── utils.py                # Utility functions for formatting and embeds
  ├── config.py               # Configuration constants
  ├── token_sidebar.py        # GUI tool for securely storing and encrypting discord token credentials
  └── server_settings.json    # Per-server settings storage (auto generated)
```

## Features

### 🎉 Welcome Messages
- **Beautiful Embeds:** Welcome messages are displayed in attractive Discord embeds
- **Customizable Text:** Admins can customize the welcome message with variables
- **User Thumbnail:** Shows the new member's avatar
- **Member Count:** Displays the current member number
- **Rules Reference:** Automatically links to the rules channel if it exists
- **Toggle:** Can be enabled/disabled per server

**Supported Variables:**
- `{mention}` - Mentions the new member
- `{username}` or `{user}` - Member's username
- `{server}` or `{server_name}` - Server name
- `{member_count}` - Current member count

### 👋 Goodbye Messages
- **Leave Notifications:** Announces when members leave the server
- **Customizable:** Admins can customize goodbye messages
- **User Thumbnail:** Shows the departing member's avatar
- **Toggle:** Can be enabled/disabled per server

### 🤖 Slash Commands

#### `/help`
Shows all available commands with descriptions.

#### `/ping`
Checks the bot's response time and displays both API and WebSocket latency.

#### `/serverinfo`
Displays comprehensive server information:
- Server owner
- Server ID
- Creation date
- Member count
- Role count
- Channel count
- Server icon

#### `/userinfo [user]`
Shows detailed user information (defaults to command user):
- Username and ID
- Nickname
- Account creation date
- Server join date
- Number of roles
- User avatar

#### `/config <setting> <value>` (Admin Only)
Configure bot settings for your server:
- `welcome_channel` - Channel name for welcome/goodbye messages
- `rules_channel` - Rules channel name to reference
- `welcome_message` - Custom welcome message template
- `goodbye_message` - Custom goodbye message template
- `welcome_enabled` - Enable/disable welcome messages (true/false)
- `goodbye_enabled` - Enable/disable goodbye messages (true/false)

**Example:**
```
/config setting:welcome_message value:Welcome {mention}! You're member #{member_count}!
/config setting:welcome_enabled value:true
```

### 💾 Persistent Storage
- **Server-Specific Settings:** Each server has its own configuration
- **JSON Database:** Lightweight, file-based storage
- **Default Values:** New servers get sensible defaults automatically
- **Thread-Safe:** Safe concurrent access to settings

### 🛡️ Error Handling
- Graceful handling of missing channels
- Permission error catching
- Command error messages
- Logging for debugging
- User-friendly error messages

## Configuration

### Server Setup
1. **Create channels:**
   - `#welcome` - For welcome and goodbye messages (optional)
   - `#rules` - For rules reference (optional)

2. **Invite the bot:**
   - Grant required permissions
   - Invite to your server

3. **Configure settings:**
   - Use `/config` command to customize messages and behavior
   - Messages support variables like `{mention}`, `{username}`, `{server}`, `{member_count}`

## Running the Bot

### Development
The bot runs automatically via the configured workflow:
- Connects to Discord using the TOKEN environment variable
- Loads all commands and event handlers
- Syncs slash commands with Discord
- Listens for member join/leave events
- Responds to slash commands
- This bot can now securely store and load your Discord bot token

### Deployment
Configured for continuous VM deployment, perfect for a Discord bot that needs 24/7 uptime.

#### 🧩 Token Setup
Before running `bot.py`, you must first run `token_sidebar.py` once to save your Discord token:

```bash
python token_sidebar.py
```

This will open up a small GUI where you can enter and encrypt your bot token
- The token is saved in `.token` (encrypted) and `.token.key` (encryption key)
- The bot automatically decrypts this token at startup.

Alternatively, you can still set the token as an environment variable:
```bash
export DISCORD_TOKEN="your-token-here"
```

Then start the bot:
```bash
python bot.py
```


## Default Settings

When a server first uses the bot, these defaults are applied:

```json
{
  "welcome_channel": "welcome",
  "rules_channel": "rules",
  "welcome_enabled": true,
  "goodbye_enabled": true,
  "welcome_message": "Welcome to {server}, {mention}! 🎉\n\nWe're glad to have you here. You're member #{member_count}!",
  "goodbye_message": "{username} has left the server. We'll miss you! 👋",
  "embed_color": 0x00ff00
}
```

## Dependencies
- **discord.py 2.6.4+** - Python library for Discord API
- **Cryptography** - Used for token encryption and decryption (required for `token_sidebar.py`)
- **Python 3.11** - Runtime environment

## Architecture

### Code Organization
The bot uses a modular architecture:
- **bot.py** - Main entry point, bot initialization, error handlers
- **commands.py** - Cog containing all slash commands
- **events.py** - Cog containing event handlers (join/leave)
- **database.py** - Database class for settings management
- **utils.py** - Utility functions for message formatting and embeds
- **config.py** - Configuration constants

### Intents
- Default intents
- Members intent (for join/leave events)
- Message content intent (for future features)

### Command System
- Uses Discord's modern slash command system
- Commands are registered via app_commands
- Auto-syncs on startup

### Event Handlers
- `on_ready` - Initialization and command syncing
- `on_member_join` - Welcome message handling
- `on_member_remove` - Goodbye message handling
- `on_command_error` - Error handling for text commands
- `on_app_command_error` - Error handling for slash commands


## Version History
- **v2.1** (Nov 1, 2025) - Minor update, adding token_sidebar.py and token encryption
- **v2.0** (Oct 31, 2025) - Major feature update with embeds, commands, and database
- **v1.0** (Oct 31, 2025) - Initial release with basic welcome functionality

**Current State:** 
- Fully functional with all features operational. Running version 2.1.
