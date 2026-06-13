import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
import random
from dotenv import load_dotenv

load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OBFUSCATOR_API = "https://v0-sttar-lua-obfuscator.vercel.app/api/SttarAlbiola"

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env file")

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Embed colors
COLOR_LOADING = discord.Color.blue()
COLOR_SUCCESS = discord.Color.green()
COLOR_ERROR = discord.Color.red()

# Spinners for loading animation
SPINNERS = [
    "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
]


async def update_loading_embed(message: discord.Message, spinner_index: int) -> int:
    """
    Updates the loading embed with an animated spinner.
    Returns the next spinner index.
    """
    spinner = SPINNERS[spinner_index % len(SPINNERS)]
    embed = discord.Embed(
        title=f"{spinner} Obfuscating Lua Code",
        description="Processing your code through the obfuscator...",
        color=COLOR_LOADING
    )
    try:
        await message.edit(embed=embed)
    except discord.errors.NotFound:
        pass
    return spinner_index + 1


async def obfuscate_lua(code: str) -> dict:
    """
    Sends Lua code to the obfuscator API and returns the response.
    """
    async with aiohttp.ClientSession() as session:
        payload = {"code": code}
        try:
            async with session.post(OBFUSCATOR_API, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"success": False, "error": f"API returned status {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Request timed out. Please try again."}
        except aiohttp.ClientError as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}


@bot.event
async def on_ready():
    """Triggered when the bot is ready."""
    try:
        synced = await bot.tree.sync()
        print(f"✓ Bot is online as {bot.user}")
        print(f"✓ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"✗ Failed to sync commands: {e}")


@bot.tree.command(
    name="obf",
    description="Obfuscate Lua code using the Sttar obfuscator API"
)
@app_commands.describe(
    code="Lua code to obfuscate (optional if file is provided)",
    file="Lua file to obfuscate (optional if code is provided)"
)
async def obfuscate(
    interaction: discord.Interaction,
    code: str = None,
    file: discord.Attachment = None
):
    """
    Slash command to obfuscate Lua code.
    """
    # Validate inputs
    if not code and not file:
        embed = discord.Embed(
            title="❌ Missing Input",
            description="Please provide either `code` or upload a `file`.",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Get code from file if provided
    if file:
        if not file.filename.endswith('.lua'):
            embed = discord.Embed(
                title="❌ Invalid File Type",
                description="Please upload a `.lua` file.",
                color=COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            code = (await file.read()).decode('utf-8')
        except Exception as e:
            embed = discord.Embed(
                title="❌ File Read Error",
                description=f"Could not read the file: {str(e)}",
                color=COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    # Check code length
    if len(code) > 50000:
        embed = discord.Embed(
            title="❌ Code Too Large",
            description="Code must be under 50,000 characters.",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Send loading message
    loading_embed = discord.Embed(
        title=f"{SPINNERS[0]} Obfuscating Lua Code",
        description="Processing your code through the obfuscator...",
        color=COLOR_LOADING
    )
    await interaction.response.send_message(embed=loading_embed)
    message = await interaction.original_response()

    # Animate loading spinner
    spinner_index = 0
    obfuscator_task = asyncio.create_task(obfuscate_lua(code))

    while not obfuscator_task.done():
        spinner_index = await update_loading_embed(message, spinner_index)
        try:
            await asyncio.wait_for(asyncio.sleep(0.6), timeout=0.6)
        except asyncio.TimeoutError:
            pass

    # Get the result
    result = obfuscator_task.result()

    # Handle response
    if result.get("success"):
        obfuscated_code = result.get("obfuscated", "")
        metadata = result.get("metadata", {})
        original_size = metadata.get("original_size", len(code))
        obfuscated_size = metadata.get("obfuscated_size", len(obfuscated_code))
        compression_ratio = metadata.get("compression_ratio", "N/A")

        # Create success embed
        success_embed = discord.Embed(
            title="✓ Obfuscation Complete",
            description="Your Lua code has been successfully obfuscated!",
            color=COLOR_SUCCESS
        )
        success_embed.add_field(
            name="Original Size",
            value=f"{original_size:,} bytes",
            inline=True
        )
        success_embed.add_field(
            name="Obfuscated Size",
            value=f"{obfuscated_size:,} bytes",
            inline=True
        )
        success_embed.add_field(
            name="Compression Ratio",
            value=str(compression_ratio),
            inline=True
        )
        success_embed.set_footer(text="Powered by Sttar Obfuscator")

        await message.edit(embed=success_embed)

        # Send obfuscated code as file
        random_num = random.randint(100000, 999999)
        file_name = f"Obfuscated-{random_num}.lua"
        file_bytes = io.BytesIO(obfuscated_code.encode('utf-8'))
        await interaction.followup.send(
            file=discord.File(file_bytes, filename=file_name)
        )
    else:
        error_message = result.get("error", "Unknown error occurred")
        error_embed = discord.Embed(
            title="❌ Obfuscation Failed",
            description=f"Error: {error_message}",
            color=COLOR_ERROR
        )
        await message.edit(embed=error_embed)


# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
