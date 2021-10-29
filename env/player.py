from __future__ import annotations
import asyncio, discord, youtube_dl, threading, re, unicodedata, os
from posixpath import pardir
# from discord.enums import Theme
from youtubesearchpython import VideosSearch
import os #, shutil
from types import SimpleNamespace

class ServerQueue:
  def __init__(self,serverID):
    self.serverID = serverID
    self.queueLen = 0
    self.curQueue = 0
    self.songQueue = []
  def checkQueueResidue(self):
    dirMsg = "" 
    if not os.path.exists(f'server/{self.serverID}'): 
      os.makedirs(f'server/{self.serverID}')
      dirMsg += f"server {self.serverID} made"
    try:
      os.remove(f"./server/{self.serverID}{self.songQueue[-1].title}.mp3") # delete dir and its content
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
    voice_client.play(discord.FFmpegPCMAudio(f'server/{serverID}/{serverReference.songQueue[serverReference.curQueue - 1].title}.mp3'), after=lambda e: print("done", e))
    while voice_client.is_playing():
      # 👍 
      await asyncio.sleep(1)
    # stoop after the player has finished
    voice_client.stop()

async def stopLoop(ctx):
  global looped
  looped = False
  await ctx.send("out of loop")

async def play(client, ctx, *arg):
  # grab the user who sent the command
  user=ctx.message.author
  voice_channel=user.voice.channel
  
  # kalau bukan link
  print(arg)
  if not "youtu" in arg:
    arg = " ".join(arg)
    arg = searchVideoByName(arg)
    metatemp = arg.result()["result"][0]
    arg = arg.result()["result"][0]["link"]

    # await ctx.send(arg)
    
  # only play music if user is in a voice channel
  if voice_channel is not None:
    try:
      # https://discordpy.readthedocs.io/en/stable/api.html#discord.VoiceClient
    
      
      # WHAT THE FUCK WITH THIS MESSY CODE
      channel = ctx.message.author.voice.channel
      voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) 
      serverID = str(ctx.message.guild.id) 
      
      # jadi fungsi bawah ini tu return 1 klo di list serverqueues ada yg mengandung serverID tertentu, return none klo gaada
      if next((1 for serverQueue in serverQueues if serverID in serverQueue.serverID), None) is None: 
        serverQueues.append(ServerQueue(serverID))
      serverReference = findServerByIDTryFix(serverID) # ni terlalu padet euy
      dirMsg = serverReference.checkQueueResidue()
      await ctx.send(dirMsg)
 
      # serverQueue = findServerByID(serverID) # ni terlalu padet euy 
      
      await ctx.send(f"current working server: {serverReference.serverID}")
      # await ctx.send(f"server id: {serverReference.serverID}")
      # await ctx.send(f"voice_client = {voice_client}")

      if not voice_client is None: #test if voice channel exists
        await ctx.send(f"connecting to {ctx.message.author.voice.channel} voice channel")
        if not voice_client.is_connected():
          voice_client = await channel.connect()
      else:
        try:
          voice_client = await channel.connect()
        except Exception as e:
          await ctx.send(e)
      
      # download
      await ctx.send(f"downloading: <{arg}>")
      # await ctx.send(f"voice_client = {voice_client}")
      # await ctx.send(f"type of serverIndex = {type(serverIndex)}")
      # try:
      
      # except Exception as e:
      #   await ctx.send(f"ASU\n{e}")
      #   for i in range(len(serverQueues)):
      #     await ctx.send(f"{i}. {serverQueues[i]}")
      #     # await ctx.send(serverIndex)
      #     await ctx.send(serverQueues)
      
      
    
      # create download thread and start it
      downloadThread = DownloadThread(f"threadXXXgaming-{serverReference.curQueue}", arg, serverID, metatemp)
      downloadThread.start()

      # create wait var for time memory
      # wait until downloadThread has attribute / property 'meta' i.e. downloadThread.meta
      waiting = 0
      while not hasattr(downloadThread, "meta"):# https://stackoverflow.com/questions/843277/how-do-i-check-if-a-variable-exists
        if waiting%60==0:
          await ctx.send(f"waiting thread {downloadThread.name} to finish, {waiting} seconds passed")
        await asyncio.sleep(1)
        waiting += 1
        # if waiting > 20: # dengerin dosen dulu ,setuju
        #   # terminate thread
        #   await ctx.send("reaching time limit, terminating...")
        #   return  #bisa to? kek di c kan jadinya blm dicoba sih, gatau error ato ga wkkwkwk
      
      # get meta from downloadThread
      meta = downloadThread.meta
      # creating song object
      
      song = Song(meta, arg, slugify(metatemp["title"]))
      serverReference.songQueue.append(song)
      queueLen = len(serverReference.songQueue) # songQUeueu harusnya co nes eue EUE
      serverReference.queueLen = queueLen

      await ctx.send("finished downloading 👍")
      # wait for player stop
      if voice_client.is_playing():
        while voice_client.is_playing():
          await asyncio.sleep(1)

      # create StreamPlayer
      # Note: stupid solution but at least it worked
      # if not user.voice.is_connected():
      voice_client.play(discord.FFmpegPCMAudio(f'server/{serverID}/{serverReference.songQueue[serverReference.curQueue].title}.mp3'), after=lambda e: print("done", e))
      serverReference.curQueue+=1
      sendPlaying = False
      while voice_client.is_playing():
        if not sendPlaying:
          await ctx.send(f"Playing: {song.metaInfo['title']}\nUploader: {song.metaInfo['uploader']}\nDuration: {str(datetime.timedelta(seconds=song.metaInfo['duration']))}")
          sendPlaying = True
        # 👍 
        await asyncio.sleep(1)
      # stoop after the player has finished
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
    # self.serverIndex = serverIndex
  
  def run(self) -> None:
    print(f"starting thread {self.name}")
    self.downloadmp3()
    print(f"exiting thread {self.name}")

  def downloadmp3(self) -> dict:
    subjectServerQueue = findServerByIDTryFix(self.serverid)
    ydl_opts = {  
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }], 
        'outtmpl':f'server/{self.serverid}/{slugify(self.metatemp["title"])}.mp3',
        # 'external-downloader': 'aria2c',
        #'quiet' : "true",
        'ignoreerrors' : "true",
        #'external-downloader-args': '-x 2',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      meta = ydl.extract_info(self.link)
      ydl.download([self.link])
      self.meta =  meta

# In Progress
async def addSongToQueue(arg):
  return 

async def clearQueue(ctx):
  serverReference = findServerByIDTryFix(str(ctx.message.guild.id))
  songCleared = 0
  # try:
  #   msg += f"active threads : {threading.active_count()}\n"
  #   for thread in threading.enumerate():
  #     msg += f"{thread.name}, alive: {thread.is_alive()}\n"
  # except Exception as e:
  #   msg += e
  try:
    for songNum in range(0,serverReference.queueLen):
      #check if the song is playing or the list is empty
      if(serverReference.curQueue != songNum): 
        try:
          os.remove(f"./server/{serverReference.serverID}/music{songNum}.mp3")
          songCleared+=1
        except Exception as e:
          await ctx.send(f"error message : {e}\nqueue number {songNum} failed to be erased,\n")
    serverReference.songQueue = []
    serverReference.curQueue=0
    serverReference.queueLen = len(serverReference.songQueue)
    await ctx.send(f"{songCleared} songs removed from queue\n")
  except Exception as e:
    await ctx.send("clear queue failed\n" + e)


async def queue(ctx):
  serverReference = findServerByIDTryFix(ctx.message.guild.id)
  try:
    for song in serverReference.songQueue:
      await ctx.send(f"{song}. {song.metaInfo['title']}")
  except:
    await ctx.send("No song in queue")
  await ctx.send(f"curQueue: {serverReference.curQueue}\nqueueLen: {len(serverReference.songQueue)}")
  return


async def voice_status(ctx, client):
  print(client.voice_clients)
  await ctx.send(type(client.voice_clients))
  await ctx.send(client.voice_clients)
  channel = discord.utils.get(ctx.guild.voice_channels, name=ctx.message.author.voice.channel)
  voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
  if not voice is None: #test if voice is 
    try:
      b = vars(voice)
      await ctx.send(', '.join("%s: %s" % item for item in b.items()))
    except Exception as e:
      await ctx.send(e)
    await ctx.send(f"connecting{ctx.message.author.voice.channel}")
    if not voice.is_connected():
      await channel.connect()
  else:
    await channel.connect()
      
async def rmFromQueue(ctx):
  index = int(ctx.message.content)
  serverid = ctx.message.guild.id
  serverIndex = findServerByID(serverid)
  songName = serverQueues[serverIndex].songQueue[index].metainfo['title']
  serverQueues[serverIndex].queueLen = len(serverQueues[serverIndex].songQueue)
  try:
    os.remove(f'server/{serverid}/music{serverQueues[serverIndex].curQueue}')
    serverQueues[serverIndex].songQueue.pop(index)
  except:
    await ctx.send("can't remove currently playing music")
    return
  await ctx.send(f"removed {songName}")
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