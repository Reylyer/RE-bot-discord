from __future__ import unicode_literals, annotations
from types import SimpleNamespace
#%%
import discord, asyncio
import json
import os
from env import *

#import time
from discord.ext import commands
from dotenv import load_dotenv
# command prefix s-
client = commands.Bot(command_prefix="s-")

# environment variable
load_dotenv('.env')
TOKEN = os.getenv('TOKEN')

class Server():
  def __init__(self, id):
    self.id = id
    
  nhSession = []
  savedCodes = []
  
try:
  f = open("servers.json")
  f.close()
except:
  with open("servers.json", "w") as f:
    f.write(json.dumps([]))
    f.close()
    
# @client.event
# async def on_message(message):
#   with open("servers.json", "r+") as f:
#     content = f.read()
#     try:
#       servers = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
#     except Exception as e:
#       await message.reply(e)
#     for server in servers:
#       if server.id is message.guild.id:
#         pass
#     else:
#       newClass = Server(message.guild.id)
#       servers.append(newClass)
#       f.seek(0)
#       f.write(servers)
#       f.truncate()
#     f.close()
    

# event
@client.event # bot online (saat .py ini dijalankan)
async def on_ready():
    print("its ready!! let the message in!")

@client.event # saat ada member yang masuk
async def on_join(member):
    print(f"{member} has joined the chat! Welcome!")
    await member.send(f"{member} has joined the chat! Welcome!")

@client.event # saat ada member yang keluar
async def on_leave(member):
    print(f"{member} has left... ")



@client.command() #s-ping
async def ping(ctx):
    await ctx.send(f"pong! {round(client.latency * 1000)}ms")
    print(f"sent! message : pong! {round(client.latency * 1000)}ms")

@client.command() # s-clear
async def clear(ctx, banyak = 2):
    await ctx.channel.purge(limit=int(banyak))
    print(f"Message cleared! amount = {banyak}")

@client.command() # s-kick
async def kick(ctx, member : discord.Member, *, reason = None):
    await member.kick(reason = reason)
    await ctx.send(f"{member.mention} has been kicked! get out! \nReason = {reason}")
    print(f"kicked a member, name = {member}")

@client.command() #s-ban
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(f"{member.mention} has been banned! let the hell purify your soul! \nReason = {reason}")
    print(f"banned a member, name = {member}")

@client.command()
async def mention(ctx, member : discord.Member,  amount):
  for i in range(amount):
    await ctx.send(f"OI! {member.mention()}")
    await asyncio.sleep(0.5)



#---------------------------------------------------------
#                    in progress zone
#---------------------------------------------------------

# NH SET
try:
  f = open("nhcode.json")
  f.close()
except:
  with open("nhcode.json", "w") as f:
    f.write(json.dumps([]))
    f.close()


@client.command()
async def stopSeering(ctx, sessionName):
  await nh.stopSeering(client, ctx, sessionName)
  await ctx.send("ok")

@client.command() #s-seerNH_here
async def seerNH_here(ctx, *args):
  await nh.seerNH_here(client, ctx, *args)



#ABSEN UNDIP SET


try:
  f = open("MAHASISWA.json")
  f.close()
except:
  with open("MAHASISWA.json", "w") as f:
    f.write(json.dumps([]))
    f.close()

@client.command() #set dummy text
async def dummy_text(ctx, amo = 3):
  for _ in range(0, amo):
    ctx.send("this is a dummy text.")

@client.command() # set pass n mail
async def set_credential(ctx, properties, value):
  await absensi.set_credential(ctx, properties, value)

@client.command() # MAIN FUNCTION
async def absen(ctx, codeOrLink):
  await absensi.absen(ctx, codeOrLink)
    
@client.command()
async def sendMonitorCovid(ctx):
  with open("MAHASISWA.json", "w+") as f:
    pass
  

# all about voice channel
@client.command()
async def play(ctx, *arg):
  await player.play(client, ctx, *arg)
  if ctx.message.content.contains('allah'):
    await ctx.send('mashallah brother, keep up your iman')

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
@client.command()
async def leave(ctx):
  user=ctx.message.author
  voice_channel=user.voice.channel
  voice_clients = client.voice_clients
  for voi in voice_clients:
    if voi.channel == voice_channel:
      voice_client = voi
      break
  else:
    await ctx.send("kamu atau aku engga di voice channel \:(")
    return
  voice_client.stop()
  await voice_client.disconnect()
  await player.clearQueue(ctx)

@client.command()
async def queue(ctx):
  await player.queue(ctx)
@client.command()
async def clearq(ctx):
  await player.clearQueue(ctx)

@client.command()
async def remove(ctx):
  await player.rmFromQueue(ctx)
  
@client.command()
async def pause(ctx):
  await ctx.voice_client.pause()
@client.command()
async def resume(ctx):
  if ctx.voice_client.is_paused():
    await ctx.voice_client.resume()
@client.command()
async def stop(ctx):
  await ctx.voice_client.stop()
@client.command()
async def is_connected(ctx):
  await ctx.send(str(ctx.voice_client.is_connected()))
@client.command()
async def is_playing(ctx):
  await ctx.send(str(ctx.voice_client.is_playing()))
@client.command()
async def is_paused(ctx):
  await ctx.send(str(ctx.voice_client.is_paused()))

@client.command()
async def voice_status(ctx):
  await player.voice_status(ctx, client)


@client.command() # set pass n mail
async def ip(ctx):
  await ctx.send("20.85.244.255")










print(TOKEN)
client.run(TOKEN)

# client.run("drop your discord bot token here")




# sleep coroutine https://discordpy.readthedocs.io/en/stable/faq.html#what-is-a-coroutine

# on repl.it if not working :
# install-pkg gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
