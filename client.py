from __future__ import unicode_literals, annotations
from types import SimpleNamespace
#%%
import discord, asyncio
import json
import os, sys
from env import *

#import time
from discord.ext import commands
from dotenv import load_dotenv

# environment variable
load_dotenv('.env')
TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')

# command prefix z-
client = commands.Bot(command_prefix=f"{PREFIX}-")


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
    sys.stdout.flush()
    # await nh.continyu()

@client.event # saat ada member yang masuk
async def on_join(member):
    print(f"{member} has joined the chat! Welcome!")
    sys.stdout.flush()
    await member.send(f"{member} has joined the chat! Welcome!")

@client.event # saat ada member yang keluar
async def on_leave(member):
    print(f"{member} has left... ")
    sys.stdout.flush()


@client.command(aliases=["h", "c"])
async def commands(ctx):
    await ctx.send(
"""
```cmd
general:
- ping
- clear
- kick
- ban
- mention
```

```cmd
player:
- play(p) <nama_lagu> | menggunakan ytdl untuk mendownload lalu play
- playrandom(pr) | memutar lagu random yang berasal dari cache yang pernah diplay
- quiz(q) <optional:timeout> | sama dengan playrandom namun dengan default timeout 30 detik
- stopquiz(sq) | menghentikan quiz (set var quizb to false)
- loopthis(lt) | loop lagu terbaru dari play(confusing)
- stoploop(sl) | stop loopthis
not used much
join, leave, is_connected, is_playing, is_paused, voice_status
```

```cmd
cheat:
- djiksta(dg) <input> | lakukan generate table djikstra, pass help untuk melihat format input
cooming soon
```

```cmd
absensi:
JANGAN COBA MASUKAN CREDENTIAL ANDA UNTUK SEKARANG!
- set_credential
- absen
- sendMonitorCovid
- debug(d) <code> | experimental, use it well!
```

```cmd
nhScraping:
- seerNH_here(snh) <input> | pass --help untuk lebih jelas, default scrap main page !!WARNING!! tidak ada cara untuk stop untuk sekarang!!!
- stopSeering <sessionname> | in development
- editSession <property> <value> | in development

```
"""
    )


@client.command() #s-ping
async def ping(ctx):
    await ctx.send(f"pong! {round(client.latency * 1000)}ms")
    print(f"sent! message : pong! {round(client.latency * 1000)}ms")
    sys.stdout.flush()

@client.command() # s-clear 
async def clear(ctx, banyak = 2):
    await ctx.channel.purge(limit=int(banyak))
    print(f"Message cleared! amount = {banyak}")
    sys.stdout.flush()

@client.command() # s-kick
async def kick(ctx, member : discord.Member, *, reason = None):
    await member.kick(reason = reason)
    await ctx.send(f"{member.mention} has been kicked! get out! \nReason = {reason}")
    print(f"kicked a member, name = {member}")
    sys.stdout.flush()

@client.command() #s-ban
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(f"{member.mention} has been banned! let the hell purify your soul! \nReason = {reason}")
    print(f"banned a member, name = {member}")
    sys.stdout.flush()

@client.command()
async def mention(ctx, member : discord.Member,  amount = "1"):
    for i in range(int(amount)):
        await ctx.send(f"OI! {member.mention}")
        await asyncio.sleep(1)



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

@client.command(aliases=["snh"]) #s-seerNH_here
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
        await ctx.send("this is a dummy text.")

@client.command() # set pass n mail
async def set_credential(ctx, properties, value):
    """jangan dipake dulu ya abang"""
    await absensi.set_credential(ctx, properties, value)

@client.command() # MAIN FUNCTION
async def absen(ctx, codeOrLink):
    await absensi.absen(ctx, codeOrLink)
    
@client.command()
async def sendMonitorCovid(ctx):
    with open("MAHASISWA.json", "w+") as f:
        pass
@client.command(aliases=["d"])
async def debug(ctx, *, code):
    try:
        exec(code)
        await ctx.send("no error")
    except Exception as e:
        await ctx.send(e)
# CHEAT ALGO

@client.command(aliases=['dg'])
async def djikstra(ctx, space,   *, arg):
    await cheatxxx.djikstraGenerator(client, ctx, arg)

# all about voice channel
@client.command(aliases=['p'])
async def play(ctx, *arg):
    await player.play(client, ctx, *arg)
    if 'allah' in ctx.message.content:
        await ctx.send('mashallah brother, keep up your iman')

@client.command(aliases=['pr'])
async def playrandom(ctx):
    await ctx.send("played random song!\nTebak lagu apa!")
    await player.playRandom(client, ctx)

@client.command(aliases=['q'])
async def quiz(ctx, timer = "30"):
    await player.quiz(client, ctx, timer)

@client.command(aliases=['sq'])
async def stopquiz(ctx):
    await player.stopquiz(ctx)

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
@client.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) 
    voice_client.stop()
    await voice_client.disconnect()
@client.command(aliases=['lt'])
async def loopthis(ctx):
    await player.loopThis(client, ctx)
@client.command(aliases=['sl'])
async def stoploop(ctx):
    await player.stopLoop(ctx)

# @client.command()
# async def queue(ctx):
#     await player.queue(ctx)
# @client.command()
# async def clearq(ctx):
#     await player.clearQueue(ctx)

# @client.command()
# async def remove(ctx):
#     await player.rmFromQueue(ctx)
  
# @client.command()
# async def pause(ctx):
#     await ctx.voice_client.pause()
# @client.command()
# async def resume(ctx):
#     if ctx.voice_client.is_paused():
#         await ctx.voice_client.resume()
# @client.command(aliases=['s'])
# async def stop(ctx):
#     await ctx.voice_client.stop()
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
    await ctx.send("52.190.16.247")





print(TOKEN)
sys.stdout.flush()        

client.run(TOKEN)



# client.run("drop your discord bot token here")




# sleep coroutine https://discordpy.readthedocs.io/en/stable/faq.html#what-is-a-coroutine

# on repl.it if not working :
# install-pkg gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
