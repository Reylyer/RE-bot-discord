from __future__ import unicode_literals, annotations
from types import SimpleNamespace
from concurrent.futures import ProcessPoolExecutor
#%%
import discord, asyncio
import json
import os, sys, re, random

from discord.ext.commands.core import Command, command
import env.absensi as absensi
import env.cheatxxx as cheatxxx
import env.nh as nh
import env.piping as piping
import env.player as player
import tweepy
import importlib
import string

#import time
from discord.ext import commands
from dotenv import load_dotenv



"""====================GLOBAL VARIABLE===================="""

# environment variable
load_dotenv('.env')

TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

# global variable



"""=========================SETUP========================="""

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)
client = commands.Bot(command_prefix=f"{PREFIX}-")


"""========================DISCORD========================"""

# event
@client.event # bot online (saat .py ini dijalankan)
async def on_ready():
    print("its ready!! let the message in!")
    sys.stdout.flush()
    tasks = await nh.continyu(client)

@client.event # saat ada member yang masuk
async def on_join(member):
    print(f"{member} has joined the chat! Welcome!")
    sys.stdout.flush()
    await member.send(f"{member} has joined the chat! Welcome!")

@client.event # saat ada member yang keluar
async def on_leave(member):
    print(f"{member} has left... ")
    sys.stdout.flush()


class Utilities(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client


    @commands.command() #s-ping
    async def ping(self, ctx):
        await ctx.send(f"pong! {round(client.latency * 1000)}ms")
        print(f"sent! message : pong! {round(client.latency * 1000)}ms")
        sys.stdout.flush()

    @commands.command() # s-clear 
    async def clear(self, ctx, banyak = 2):
        await ctx.channel.purge(limit=int(banyak))
        print(f"Message cleared! amount = {banyak}")
        sys.stdout.flush()
    @commands.command() # s-kick
    async def kick(self, ctx, member : discord.Member, *, reason = None):
        await member.kick(reason = reason)
        await ctx.send(f"{member.mention} has been kicked! get out! \nReason = {reason}")
        print(f"kicked a member, name = {member}")
        sys.stdout.flush()

    @commands.command() #s-ban
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        await member.ban(reason = reason)
        await ctx.send(f"{member.mention} has been banned! let the hell purify your soul! \nReason = {reason}")
        print(f"banned a member, name = {member}")
        sys.stdout.flush()

    @commands.command()
    async def mention(self, ctx, member : discord.Member,  amount = "1"):
        for i in range(int(amount)):
            await ctx.send(f"OI! {member.mention}")
            await asyncio.sleep(1)

    @commands.command()
    async def whoami(self, ctx):
        await ctx.send(ctx.author.id)

    @commands.command() # set pass n mail
    async def ip(ctx):
        await ctx.send("52.190.16.247")

    @commands.command() #set dummy text
    async def dummy_text(ctx, amo = 3):
        for _ in range(0, amo):
            await ctx.send("this is a dummy text.")
    
    @commands.command()
    async def echo(self, ctx, *, text):
        await ctx.send(text)
        print(text)

class Piper(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.dumpTasks = {}
        self.streamingTasks = {}

        self.active_filters = {}
        self.active_stream = None

    @commands.command(aliases=["dh"])
    async def dumpHere(self, ctx):
        await ctx.send("setted as dumpster channel, please wait for the messages to be dumped")
        self.dumpTasks = asyncio.create_task(piping.dumping(ctx))
        # task = loop.run_in_executor(executor, dump)
        # loop = asyncio.get_event_loop()
        # loop.run_forever()

    @commands.command(aliases=['pt'])
    async def piper_terminal(self, ctx, *, sqlWord):
        try:
            structure = self.compilerPseudoSQL()
            if type == 0:
                filterWords = None
            stream = piping.DataStream(consumer_key, consumer_secret, access_token, access_token_secret, ctx.channel, filterWords, max_retries=10)
            await ctx.send(f"tracking tweet filtered by {filterWords}")
            stream.filter(follow=["1341567351301361665", "1330354354780577792"])
            # asyncio.create_task(stream.filter(filterWords))
            # thread = stream.filter(track=filterWords, threaded=True)
        except Exception as e:
            await ctx.send(e)
    
    @commands.command()
    async def create_data_stream(self, ctx):
        # args = self.translate(args)
        # for key in args.keys():
        #     if args[key] == 
        try:
            self.active_stream = piping.DataStream(consumer_key, consumer_secret, access_token, access_token_secret, max_retries=10)
            self.active_stream.filter(follow=["1341567351301361665", "1330354354780577792"])
            await ctx.send("success connecting to the stream")
            await ctx.send("now filter using s-create_filter_stream")
        except Exception as e:
            await ctx.send(f"error while connecting to the stream\nerror message : {e}")
    
    @commands.command()
    async def stop_data_stream(self, ctx, name):
        pass
    

    @commands.command()
    async def create_filter_stream(self, ctx, *, user_args = ''):
        user_args = self.translate(user_args.lower())
        for arg in ['filter_has', 'filter_word', 'filter_exclude_has', 'filter_exclude_word', 'mention', 'raw']:
            if arg not in user_args:
                user_args[arg] = []
        if 'name' not in user_args:
            user_args['name'] = str(random.randint(1000000, 9999999))
        else:
            user_args['name'] = user_args['name'][0]
            
        self.active_filters[user_args['name']] = piping.FilterStream(
            name                = user_args['name'], 
            stream              = self.active_stream, 
            channel             = ctx.channel, 
            mentionids          = user_args['mention'],
            filter_has          = user_args['filter_has'],
            filter_word         = user_args['filter_word'],
            filter_exclude_has  = user_args['filter_exclude_has'],
            filter_exclude_word = user_args['filter_exclude_word'],
            raw                 = user_args['raw']
            )
    
    @commands.command()
    async def stop_filter_stream(self, ctx, name):
        if name in self.active_filters:
            await ctx.send(self.active_stream.subscriber)
            self.active_stream.subscriber = {key: val for (key, val) in self.active_stream.subscriber.items() if key != name}
            await ctx.send(self.active_stream.subscriber)
            del self.active_filters[name]
            await ctx.send(f"filter_stream dengan nama {name} telah dihentikan, hopefully :<")
        else:
            await ctx.send(
f"""filter_stream dengan nama {name} tidak ditemukan
filter_stream aktif:
```cmd
{[name + " " for name in self.active_filters.keys()]}
```""")

    def translate(self, text: str):
        for nono in """!"#$%&'()*+,./:;<=>?@[\]^`{|}~""":
            text = text.replace(nono, '')
        text = text.lower().split("\n")
        args = {}
        for line in text:
            line = line.strip()
            if ' ' in line:
                key, value = line.split(' ', maxsplit=1)

                args[key] = list(filter(('').__ne__, value.split(' ')))

        return args


    
    def compilerPseudoSQL(text: str):
        text = text.upper()
        structure = {}
        print(text)
        if text.startswith("```SQL"):
            text = text[7:-3]
            space_index = [m.start() for m in re.finditer(' ', text)]
            open_parentheses_index = text.find("(")
            close_parentheses_index = text.find(")")
            if open_parentheses_index + close_parentheses_index < 0:
                return "ada masalah dengan kurung buka atau kurung tutup"
            if open_parentheses_index < space_index[2]:
                space_index[2] = open_parentheses_index
            structure['keyword'] = text[:space_index[0]]
            structure['object_type'] = text[space_index[0] + 1: space_index[1]]
            structure['object_name'] = text[space_index[1] + 1: space_index[2]]
            structure['properties' ] = [prop.strip() for prop in text[open_parentheses_index + 2:close_parentheses_index].split("\n") if len(prop) != 0]
            for line in structure['properties']:
                if ' ' in line:
                    key, value = line.split(' ', maxsplit=1)
                    structure[key] = [s.strip() for s in value[1:-1].split(',')]
            
            return structure
        else:
            return "pastikan menggunakan code blocks dan gunakan bahasa sql (\`\`\`sql ... \`\`\`)"




#---------------------------------------------------------
#                    in progress zone
#---------------------------------------------------------
class NHentaiScrap(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command()
    async def stopSeering(self, ctx, sessionName):
        await nh.stopSeering(client, ctx, sessionName)
        await ctx.send("ok")

    @commands.command(aliases=["snh"]) #s-seerNH_here
    async def seerNH_here(self, ctx, *args):
        await nh.seerNH_here(client, ctx, *args)



#ABSEN UNDIP SET

class Absen(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command() # set pass n mail
    async def set_credential(self, ctx, properties, value):
        """jangan dipake dulu ya abang"""
        await absensi.set_credential(ctx, properties, value)

    @commands.command() # MAIN FUNCTION
    async def absen(self, ctx, codeOrLink):
        await absensi.absen(ctx, codeOrLink)
        
    @commands.command()
    async def sendMonitorCovid(self, ctx):
        with open("MAHASISWA.json", "w+") as f:
            pass
    @commands.command(aliases=["d"])
    async def debug(self, ctx, *, code):
        if str(ctx.author.id) == "719757341787947060":
            try:
                exec(code)
                await ctx.send("no error")
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send("You dont have the permission to debug!")





# CHEAT ALGO
class Cheat(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(aliases=['dg'])
    async def djikstra(self, ctx, util,   *, arg = ""):
        importlib.reload(cheatxxx)
        await cheatxxx.djikstraGenerator(client, ctx, util, arg)

    @commands.command(aliases=['pg'])
    async def prim(self, ctx, util,   *, arg = ""):
        importlib.reload(cheatxxx)
        await cheatxxx.primGen(client, ctx, util, arg)





class Player(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(aliases=['p'])
    async def play(self, ctx, *arg):
        await player.play(client, ctx, *arg)
        if 'allah' in ctx.message.content:
            await ctx.send('mashallah brother, keep up your iman')

    @commands.command(aliases=['pr'])
    async def playrandom(self, ctx):
        await ctx.send("played random song!\nTebak lagu apa!")
        await player.playRandom(client, ctx)

    @commands.command(aliases=['q'])
    async def quiz(self, ctx, timer = "30"):
        await player.quiz(client, ctx, timer)

    @commands.command(aliases=['sq'])
    async def stopquiz(self, ctx):
        await player.stopquiz(ctx)

    @commands.command()
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) 
        voice_client.stop()
        await voice_client.disconnect()

    @commands.command(aliases=['lt'])
    async def loopthis(self, ctx):
        await player.loopThis(client, ctx)

    @commands.command(aliases=['sl'])
    async def stoploop(self, ctx):
        await player.stopLoop(ctx)

    @commands.command()
    async def show_cached(self, ctx):
        await player.show_cached(ctx)

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        await ctx.voice_client.stop()

    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            await ctx.voice_client.resume()

    @commands.command()
    async def is_connected(self, ctx):
        await ctx.send(str(ctx.voice_client.is_connected()))

    @commands.command()
    async def is_playing(self, ctx):
        await ctx.send(str(ctx.voice_client.is_playing()))

    @commands.command()
    async def is_paused(self, ctx):
        await ctx.send(str(ctx.voice_client.is_paused()))

    @commands.command()
    async def voice_status(self, ctx):
        await player.voice_status(ctx, client)




client.add_cog(Utilities(client))
client.add_cog(Piper(client))
client.add_cog(NHentaiScrap(client))
client.add_cog(Absen(client))
client.add_cog(Cheat(client))
client.add_cog(Player(client))

print(TOKEN)
sys.stdout.flush()        

client.run(TOKEN)

# sleep coroutine https://discordpy.readthedocs.io/en/stable/faq.html#what-is-a-coroutine

# on repl.it if not working :
# install-pkg gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
