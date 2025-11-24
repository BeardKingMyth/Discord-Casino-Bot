import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()  # Loads .env file
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # Required to read messages

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Load all cogs in /cogs/games
async def load_cogs():
    for folder in ["cogs", "cogs/games", "cogs/games/dice", "cogs/games/cards"]:
        for filename in os.listdir(folder):
            if filename.endswith(".py"):
                await bot.load_extension(f"{folder.replace('/', '.')}.{filename[:-3]}")


# Proper async main
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

# Run the bot
asyncio.run(main())
