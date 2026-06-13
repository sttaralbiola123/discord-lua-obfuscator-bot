import os
import asyncio
import aiohttp
import io
import random
import threading
from flask import Flask

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OBFUSCATOR_API = "https://v0-sttar-lua-obfuscator.vercel.app/api/SttarAlbiola"

if not DISCORD_TOKEN:
    raise ValueError("Missing DISCORD_TOKEN")

# ---------------- FLASK (Render Web Service fix) ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run_flask():
    port = int(os.environ.get("PORT"))
    app.run(host="0.0.0.0", port=port)

# ---------------- DISCORD BOT ----------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Colors
COLOR_LOADING = discord.Color.blue()
COLOR_SUCCESS = discord.Color.green()
COLOR_ERROR = discord.Color.red()

SPINNERS = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

# ---------------- API REQUEST ----------------
async def obfuscate_lua(code: str):
    timeout = aiohttp.ClientTimeout(total=30)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(OBFUSCATOR_API, json={"code": code}) as resp:
                if resp.status != 200:
                    return {"success": False, "error": f"HTTP {resp.status}"}

                return await resp.json()

    except asyncio.TimeoutError:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------------- LOADING UPDATE ----------------
async def update_loading(message, i):
    spinner = SPINNERS[i % len(SPINNERS)]
    embed = discord.Embed(
        title=f"{spinner} Obfuscating Lua Code",
        description="Processing...",
        color=COLOR_LOADING
    )

    try:
        await message.edit(embed=embed)
    except:
        pass

    return i + 1

# ---------------- SLASH COMMAND ----------------
@bot.tree.command(name="obf", description="Obfuscate Lua code")
@app_commands.describe(
    code="Lua code",
    file="Lua file (.lua)"
)
async def obf(interaction: discord.Interaction, code: str = None, file: discord.Attachment = None):

    if not code and not file:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Error",
                description="Provide code or file",
                color=COLOR_ERROR
            ),
            ephemeral=True
        )
        return

    if file:
        if not file.filename.endswith(".lua"):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description="Only .lua files allowed",
                    color=COLOR_ERROR
                ),
                ephemeral=True
            )
            return

        code = (await file.read()).decode("utf-8")

    if len(code) > 50000:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Error",
                description="Code too large",
                color=COLOR_ERROR
            ),
            ephemeral=True
        )
        return

    # Loading message
    embed = discord.Embed(
        title=f"{SPINNERS[0]} Obfuscating...",
        description="Please wait",
        color=COLOR_LOADING
    )

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    task = asyncio.create_task(obfuscate_lua(code))
    i = 0

    while not task.done():
        i = await update_loading(msg, i)
        await asyncio.sleep(0.6)

    result = await task

    # Success
    if result.get("success"):
        obf_code = result.get("obfuscated", "")

        await msg.edit(
            embed=discord.Embed(
                title="Success",
                description="Lua code obfuscated successfully",
                color=COLOR_SUCCESS
            )
        )

        file_bytes = io.BytesIO(obf_code.encode("utf-8"))
        filename = f"obf-{random.randint(1000,9999)}.lua"

        await interaction.followup.send(
            file=discord.File(file_bytes, filename=filename)
        )

    else:
        await msg.edit(
            embed=discord.Embed(
                title="Failed",
                description=result.get("error", "Unknown error"),
                color=COLOR_ERROR
            )
        )

# ---------------- READY EVENT ----------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ---------------- START BOTH ----------------
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(DISCORD_TOKEN)
