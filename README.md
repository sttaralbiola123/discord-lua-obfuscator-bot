# Discord Lua Obfuscator Bot

A production-ready Discord bot that obfuscates Lua code using the Sttar Obfuscator API. Built with discord.py 2.x and slash commands.

## Features

- **Slash Command**: `/obf` - Obfuscate Lua code
- **Input Methods**:
  - Direct code input via `code` parameter
  - File upload via `file` parameter (`.lua` files)
  - Error handling for missing inputs
- **Loading Animation**: Animated spinner while processing
- **Success Response**:
  - Original and obfuscated code sizes
  - Compression ratio
  - Obfuscated code as `.lua` file attachment
- **Error Handling**: Comprehensive error messages for various failure scenarios

## Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Render account (for deployment)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/sttaralbiola123/discord-lua-obfuscator-bot.git
cd discord-lua-obfuscator-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Add your Discord Bot Token to `.env`:
```
DISCORD_TOKEN=your_token_here
```

6. Run the bot:
```bash
python main.py
```

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" tab and create a bot
4. Copy the token and add it to your `.env` file
5. Enable these **Privileged Gateway Intents**:
   - Message Content Intent
6. Under **OAuth2 > URL Generator**, select:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Read Message History`, `Attach Files`
7. Use the generated URL to invite the bot to your server

## Deployment on Render

1. Push your code to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Create a new "Background Worker"
4. Connect your GitHub repository
5. Set the following:
   - **Name**: `discord-lua-obfuscator-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment Variables**: Add `DISCORD_TOKEN` with your bot token
6. Click "Create Web Service"

## Usage

### Obfuscate from Code
```
/obf code:print("hello")
```

### Obfuscate from File
```
/obf file:[upload your .lua file]
```

## API Reference

The bot uses the Sttar Obfuscator API:
- **Endpoint**: `https://v0-sttar-lua-obfuscator.vercel.app/api/SttarAlbiola`
- **Method**: `POST`
- **Request Body**:
```json
{
  "code": "<lua code>"
}
```
- **Response**:
```json
{
  "success": true,
  "obfuscated": "<obfuscated code>",
  "metadata": {
    "original_size": 123,
    "obfuscated_size": 456,
    "compression_ratio": "3.7x"
  }
}
```

## Features Breakdown

### Loading Animation
While the API processes your code, the bot displays an animated spinner that updates every 0.6 seconds, providing visual feedback.

### Success Embed
- Blue title with checkmark
- Original and obfuscated code sizes
- Compression ratio
- Powered by Sttar Obfuscator footer

### Error Handling
- Invalid file types (non-.lua files)
- Missing inputs
- Code size limits (>50,000 characters)
- Network errors and timeouts
- API errors

## Code Structure

```
main.py
├── Configuration
├── Bot setup with intents
├── Helper functions
│   ├── update_loading_embed() - Animates spinner
│   └── obfuscate_lua() - API calls
├── Event handlers
│   └── on_ready() - Sync commands
└── Slash commands
    └── /obf - Main obfuscation command
```

## Performance

- **Request Timeout**: 30 seconds
- **Max Code Size**: 50,000 characters
- **Loading Animation**: 0.6 second updates
- **Async Operations**: Full async/await for non-blocking operations

## Troubleshooting

### Bot not responding to commands
- Ensure commands are synced (check console on bot startup)
- Verify bot has `applications.commands` scope in OAuth2
- Restart the bot after making permission changes

### API errors
- Check the Sttar Obfuscator API status
- Verify code is valid Lua syntax
- Check network connectivity

### File upload issues
- Ensure file has `.lua` extension
- Check file size (under 8MB)
- Try re-uploading the file

## License

MIT License - Feel free to modify and deploy!

## Support

For issues or questions, create an issue in the GitHub repository.
