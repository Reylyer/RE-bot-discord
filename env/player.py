from __future__ import annotations
import asyncio, discord, youtube_dl, threading, re, unicodedata, datetime, json
from posixpath import pardir
from youtubesearchpython import VideosSearch
import os, random, glob, sys
from types import SimpleNamespace

class ServerQueue:
  def __init__(self,serverID):
    self.serverID = serverID
    self.queueLen = 0
    self.curQueue = 0
    self.songQueue = []
  def checkQueueResidue(self):
    dirMsg = "" 
    if not os.path.exists(f'server/'): 
      os.makedirs(f'server/')
      dirMsg += f"server  made"
    try:
      os.remove(f"./server/{self.songQueue[-1].title}.mp3")
      dirMsg += f"residue removed at {self.queueLen}"
    except:
      dirMsg += "no queue residue found" 
    self.queueLen = len(self.songQueue)
    return dirMsg
  
class Song:
  def __init__(self, metaInfo, link, titlesluged):
    self.metaInfo = metaInfo
    self.link = link
    self.title = titlesluged
    pass

try:
  os.mkdir('server')
except:
  pass
serverQueues = []
looped = False

async def loopThis(client, ctx):
  global looped
  await ctx.send("looped")
  channel = ctx.message.author.voice.channel
  voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) 
  serverID = str(ctx.message.guild.id)
  serverReference = findServerByIDTryFix(serverID)
  looped = True
  while voice_client.is_playing():
    await asyncio.sleep(1)
  while looped:
    voice_client.play(discord.FFmpegPCMAudio(f'server/{serverReference.songQueue[serverReference.curQueue - 1].title}.mp3'), after=lambda e: print("done", e))
    sys.stdout.flush()
    while voice_client.is_playing():
      await asyncio.sleep(1)
    voice_client.stop()

async def playRandom(client, ctx):
  channel = ctx.message.author.voice.channel
  voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) 
  serverID = str(ctx.message.guild.id)
  serverReference = findServerByIDTryFix(serverID)
  while voice_client.is_playing():
    await asyncio.sleep(1)
  
  filenames = glob.glob("./server/*.mp3")
  print(filenames)
  sys.stdout.flush()
  choice = random.choice(filenames)
  print(choice)
  sys.stdout.flush()
    

  voice_client.play(discord.FFmpegPCMAudio(choice), after=lambda e: print("done", e))
  sys.stdout.flush()
  while voice_client.is_playing():
    await asyncio.sleep(1)
  voice_client.stop()

async def quiz(client, ctx, timern):
  global quizb
  timern = int(timern)
  channel = ctx.message.author.voice.channel
  voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) 
  serverID = str(ctx.message.guild.id)
  serverReference = findServerByIDTryFix(serverID)
  quizb = True
  while voice_client.is_playing():
    await asyncio.sleep(1)
  while quizb:
    await ctx.send("quiz time!\nsilahkan tebak lagu apa ini!")
    filenames = glob.glob("./server/*.mp3")
    choice = random.choice(filenames)
    voice_client.play(discord.FFmpegPCMAudio(choice), after=lambda e: print("done", e))
    sys.stdout.flush()
    timer = 0
    while timer < timern:
      await asyncio.sleep(1)
      timer += 1
    voice_client.stop()
    await ctx.send(f"lagu adalah : {choice[9:-4]}")

async def stopquiz(ctx):
  global quizb
  quizb = False
  await ctx.send("quiz stopped!")

async def stopLoop(ctx):
  global looped
  looped = False
  await ctx.send("out of loop")

async def play(client, ctx, *arg):
  user=ctx.message.author
  voice_channel=user.voice.channel
  
  print(arg)
  sys.stdout.flush()
  if not "youtu" in arg:
    arg = " ".join(arg)
    arg = searchVideoByName(arg)
    metatemp = arg.result()["result"][0]
    arg = arg.result()["result"][0]["link"]

    
  if voice_channel is not None:
    try:
    
      
      channel = ctx.message.author.voice.channel
      voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) 
      serverID = str(ctx.message.guild.id) 
      
      if next((1 for serverQueue in serverQueues if serverID in serverQueue.serverID), None) is None: 
        serverQueues.append(ServerQueue(serverID))
      serverReference = findServerByIDTryFix(serverID)
      
      if not voice_client is None:
        await ctx.send(f"connecting to {ctx.message.author.voice.channel} voice channel")
        if not voice_client.is_connected():
          voice_client = await channel.connect()
      else:
        try:
          voice_client = await channel.connect()
        except Exception as e:
          await ctx.send(e)
      
      await ctx.send(f"downloading: <{arg}>")
      
    
      # create download thread and start it
      downloadThread = DownloadThread(f"threadXXXgaming-{serverReference.curQueue}", arg, serverID, metatemp)
      downloadThread.start()


      waiting = 0
      while not hasattr(downloadThread, "meta"):
        if waiting%60==0:
          await ctx.send(f"waiting thread {downloadThread.name} to finish, {waiting} seconds passed")
        await asyncio.sleep(1)
        waiting += 1


      meta = downloadThread.meta
      
      song = Song(meta, arg, slugify(metatemp["title"]))
      serverReference.songQueue.append(song)
      queueLen = len(serverReference.songQueue)
      serverReference.queueLen = queueLen

      await ctx.send("finished downloading 👍")
      # wait for player stop
      if voice_client.is_playing():
        while voice_client.is_playing():
          await asyncio.sleep(1)

      voice_client.play(discord.FFmpegPCMAudio(f'server/{serverReference.songQueue[serverReference.curQueue].title}.mp3'), after=lambda e: print("done", e))
      sys.stdout.flush()

      serverReference.curQueue+=1
      sendPlaying = False
      while voice_client.is_playing():
        if not sendPlaying:
          embed = discord.Embed()
          embed.set_image(url=song.metaInfo['thumbnail'])
          embed.description = f"Playing: {song.metaInfo['title']}\nUploader: {song.metaInfo['uploader']}\nDuration: {str(datetime.timedelta(seconds=song.metaInfo['duration']))}"
          await ctx.send(embed = embed)
          sendPlaying = True
        await asyncio.sleep(1)
      voice_client.stop()
      
    except Exception as e:
      await ctx.send(e)
  else:
      await ctx.send('User is not in a channel.')
      await ctx.send(ctx.message.author.voice.channel)

class DownloadThread(threading.Thread):
  def __init__(self, name, link, serverid, metatemp):
    threading.Thread.__init__(self)
    self.name = name
    self.link = link
    self.serverid = serverid
    self.metatemp = metatemp
  
  def run(self) -> None:
    print(f"starting thread {self.name}")
    sys.stdout.flush()
    self.downloadmp3()
    print(f"exiting thread {self.name}")
    sys.stdout.flush()

  def downloadmp3(self) -> dict:
    subjectServerQueue = findServerByIDTryFix(self.serverid)
    ydl_opts = {  
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }], 
        'outtmpl':f'server/{slugify(self.metatemp["title"])}.mp3',
        'ignoreerrors' : "true",
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      meta = ydl.extract_info(self.link)
      self.meta =  meta



async def queue(ctx):
  serverReference = findServerByIDTryFix(ctx.message.guild.id)
  try:
    for song in serverReference.songQueue:
      await ctx.send(f"{song}. {song.metaInfo['title']}")
  except:
    await ctx.send("No song in queue")
  await ctx.send(f"curQueue: {serverReference.curQueue}\nqueueLen: {len(serverReference.songQueue)}")
  return


      
def searchVideoByName(namaLagu):
  """ VideoSearch Object"""
  videosSearch = VideosSearch(namaLagu, limit = 2)
  return videosSearch

def getThreadCount():
  return threading.active_count(), threading.current_thread()

def findServerByID(serverid):
  serverIndex = None
  for i in range(0, len(serverQueues)):
    if serverid in serverQueues[i].serverID:
      serverIndex = i
  return serverIndex

def findServerByIDTryFix(serverid: str) -> ServerQueue:
  for serverQueue in serverQueues:
    if serverid in serverQueue.serverID:
      return serverQueue

def slugify(value, allow_unicode=False):
        """
        Me taken from https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')