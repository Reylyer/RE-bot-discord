# system side
import sys, os
import importlib
from dotenv import load_dotenv

# discord side
import discord
from discord.ext import commands


# utility
# parsers
from Cogs.CoreCommands import CoreCommands

load_dotenv('.env')
TOKEN : str = os.getenv('TOKEN')               #type: ignore
PREFIX: list = os.getenv('PREFIX').split(',')  #type: ignore
print(PREFIX)
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents().all())


@client.event
async def on_ready():
    await client.add_cog(CoreCommands(client))
    print("its ready!! let the message in!")

client.run(TOKEN)