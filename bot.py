# bot.py
from discord.ext.commands import Bot
from dotenv import load_dotenv
import os
import discord

def main():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot = Bot(command_prefix="-")
    
    bot.load_extension("cog")
    bot.run(TOKEN)

if __name__ == "__main__":
    main()

