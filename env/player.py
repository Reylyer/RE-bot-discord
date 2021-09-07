import asyncio, discord, datetime, youtube_dl, threading, json
from posixpath import pardir
# from discord.enums import Theme
from youtubesearchpython import VideosSearch
import os
from types import SimpleNamespace

class ServerQueue:
  def __init__(self,serverID):
    self.serverID = serverID
    self.queueLen = 0
    self.curQueue = 0
    self.songQueue = []
  def checkQueueResidue(self):
    dir = ""
    try:
      if not os.path.exists(f'server/{self.serverID}'):
        os.makedirs(f'server/{self.serverID}')
      os.remove(f'server/{self.serverID}/music{self.curQueue}')
    except:
      dir = "no queue residue found"
    return dir
  
class Song:
  def __init__(self, metaInfo, link, queueOrder):
    self.metaInfo = metaInfo
    self.link = link

    pass
try:
  os.mkdir('server')
except:
  pass
serverQueues = []

async def play(client, ctx, *arg):
  # grab the user who sent the command
  user=ctx.message.author
  voice_channel=user.voice.channel
  
  # kalau bukan link
  print(arg)
  if not "youtu" in arg:
    arg = " ".join(arg)
    arg = searchVideoByName(arg)

    arg = arg.result()["result"][0]["link"]

    # await ctx.send(arg)
    
  # only play music if user is in a voice channel
  if voice_channel is not None:
    try:
      # https://discordpy.readthedocs.io/en/stable/api.html#discord.VoiceClient
      # voice_clients = client.voice_clients
      # for voi in voice_clients:
      #   if voi.channel == voice_channel:
      #     voice_client = voi
      #     break
      # else:
      #   voice_client = await voice_channel.connect()
      
      
      # WHAT THE FUCK WITH THIS MESSY CODE
      channel = ctx.message.author.voice.channel
      voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild) # bntr ada stack  overflowny kg? gw kirim ya ok
      serverID = ctx.message.guild.id # jadi fungsi bawah ini tu return 1 klo di list serverqueues ada yg mengandung serverID tertentu, return none klo gaada
      if next((1 for serverQueue in serverQueues if serverQueue.serverID == serverID), None) is None: 
        serverQueues.append(ServerQueue(serverID))
      serverIndex = findServerByID(serverID) # ni terlalu padet euy
      await ctx.send(f"server id: {serverQueues[serverIndex].serverID}")
      await ctx.send(f"voice_client = {voice_client}")
      if not voice_client is None: #test if voice is 
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
      await ctx.send(f"voice_client = {voice_client}")
      dirMsg = serverQueues[serverID].checkQueueResidue()
      if dirMsg:
        await ctx.send(dirMsg)
      downloadThread, meta = downloadmp3(arg, serverID, serverIndex)
      song = Song(meta, arg, serverQueues[serverIndex].queueLen)
      serverQueues[serverIndex].songQueue.append(song)
      queueLen = len(serverQueues[serverIndex].serverQueue)
      serverQueues[serverIndex].queueLen = queueLen
      
      # meta = downloadmp3(arg)
      # expected : it will wait until the thread is finished(hopefully (pretty please (first run ok?)))
      downloadThread.start()

      # >>>>>>>>>>>>>>>>>>>>>>>>> goin to delete
      try:
        await ctx.send(f"this thread name: {downloadThread.name}")
      except Exception as e:
        await ctx.send(e)
      await ctx.send("before thread check")
      # 👍 nice thread gaming ftw real shit
      for index, thread in enumerate(threading.enumerate()):
        await ctx.send(f"{index}. {thread.name}")
        if thread.name == f"threadXXXgaming - {meta['title']}":
          await asyncio.sleep(1)
          await ctx.send(f"hey! thread with name {thread.name} is still alive/nthread.is_alive value = {thread.is_alive()}")
      #while threading.enumerate()[0].is_alive():
        # await asyncio.sleep(1)
      # <<<<<<<<<<<<<<<<<<<<<<<<<<<<< end
      await ctx.send("after thread check")

      await ctx.send("finished downloading")
      # wait for player stop
      if voice_client.is_playing():
        while voice_client.is_playing():
          await asyncio.sleep(1)

      # create StreamPlayer
      # Note: stupid solution but at least it worked
      # if not user.voice.is_connected():
      voice_client.play(discord.FFmpegPCMAudio(f'server/{serverID}/music{serverQueues[serverIndex].curQueue}.mp3'), after=lambda e: print("done", e))
      serverQueues[serverIndex].curQueue+=1
      sendPlaying = False
      while voice_client.is_playing():
        if not sendPlaying:
          await ctx.send(f"Playing: {song.metaInfo['title']}\nUploader: {song.metaInfo['uploader']}\nDuration: {str(datetime.timedelta(seconds=song.metaInfo['duration']))}")
          sendPlaying = True
        # 👍 
        await asyncio.sleep(1)
      # disconnect after the player has finished
      voice_client.stop()
      
    except Exception as e:
      await ctx.send(e)
  else:
      await ctx.send('User is not in a channel.')
      await ctx.send(ctx.message.author.voice.channel)


def downloadmp3(link: str, serverid: str, serverIndex: int) -> list[object, dict]:
  ydl_opts = {
      'format': 'bestaudio/best',
      'postprocessors': [{
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
      }],
      'outtmpl':f'server/{serverid}/music{serverQueues[serverIndex].queueLen}.mp3',
  }
  serverQueues[serverIndex].queueLen +=1
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    meta = ydl.extract_info(link) # 
    downloadThread = threading.Thread(target=ydl.download, args=([link]), name=f"threadXXXgaming - {meta['title']}")
    return downloadThread, meta

# In Progress
async def addSongToQueue(arg):
  return 

async def clearQueue(ctx):
  serverIndex = findServerByID(ctx.message.guild.id)
  songCleared = 0
  msg = ""
  # try:
  #   msg += f"active threads : {threading.active_count()}\n"
  #   for thread in threading.enumerate():
  #     msg += f"{thread.name}, alive: {thread.is_alive()}\n"
  # except Exception as e:
  #   msg += e
  try:
    for songNum in range(0,len(serverQueues[serverIndex].songQueue)+1):
      #check if the song is playing or the list is empty
      if(serverQueues[serverIndex].curQueue != songNum): 
        try:
          os.remove(f"server/{serverQueues[serverIndex].serverID}/music{songNum}.mp3\n")
          songCleared+=1
        except Exception as e:
          return ctx.send(f"error message : {e}\nqueue number {songNum} failed to be erased,\n")
    serverQueues[serverIndex].songQueue = []
    serverQueues[serverIndex].curQueue=0
    serverQueues[serverIndex].queueLen = len(serverQueues[serverIndex].songQueue)
    msg+=f"{songCleared} songs removed from queue\n"
  except:
    msg+="clear queue failed\n"
    pass
  return msg


async def queue(ctx):
  serverIndex = findServerByID(ctx.message.guild.id)
  try:
    for song in serverQueues[serverIndex].songQueue:
      await ctx.send(f"{song}. {song.metaInfo['title']}")
  except:
    await ctx.send("No song in queue")
  await ctx.send(f"curQueue: {serverQueues[serverIndex].curQueue}\nqueueLen: {len(serverQueues[serverIndex].songQueue)}")
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
      
def getInfoYoutube(linkYoutubeOrSongName):
  """mengembalikan informasi video\n
  url\n
  judul\n
  durasi
  """



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
  """ VideoSearch Object
  """
  videosSearch = VideosSearch(namaLagu, limit = 2)
  return videosSearch

def getThreadCount():
  return threading.active_count(), threading.current_thread()

def findServerByID(serverid):
  for i in enumerate(serverQueues):
    return i if serverQueues[i].serverID == serverid else None