import asyncio, discord, datetime, youtube_dl, threading, json
from posixpath import pardir
from discord.enums import Theme
from youtubesearchpython import VideosSearch
import os
from types import SimpleNamespace

class Song:
  def __init__(self, metaInfo, link, queueOrder):
    self.metaInfo = metaInfo
    self.link = link

    pass
try:
  os.mkdir('server')
except:
  pass
songQueue = []
curQueue = 0
queueLen = len(songQueue)
# 

async def play(client, ctx, *arg):
  global curQueue, queueLen
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
      voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
      serverID = ctx.message.guild.id
      
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
      dirMsg = checkQueueResidue(serverID, curQueue)
      if dirMsg:
        await ctx.send(dirMsg)
      downloadThread, meta = downloadmp3(arg, serverID)
      song = Song(meta, arg, queueLen)
      songQueue.append(song)
      queueLen = len(songQueue)
      
      # meta = downloadmp3(arg)
      # expected : it will wait until the thread is finished(hopefully (pretty please (first run ok?)))
      downloadThread.start()
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
        await asyncio.sleep(1)
      await ctx.send("after thread check")
      await ctx.send("finish downloading")
      # wait for player stop
      if voice_client.is_playing():
        while voice_client.is_playing():
          await asyncio.sleep(1)

      # create StreamPlayer
      # Note: stupid solution but at least it worked
      # if not user.voice.is_connected():
      voice_client.play(discord.FFmpegPCMAudio(f'server/{serverID}/music{curQueue}.mp3'), after=lambda e: print("done", e))
      curQueue+=1
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


def downloadmp3(link: str, serverid: str) -> list[object, dict]:
  global queueLen
  ydl_opts = {
      'format': 'bestaudio/best',
      'postprocessors': [{
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
      }],
      'outtmpl':f'server/{serverid}/music{queueLen}.mp3',
  }
  queueLen +=1
  with youtube_dl.YoutubeDL(ydl_opts) as ydl: # masi ada raise error ato belom reload?
    meta = ydl.extract_info(link) # 
    downloadThread = threading.Thread(target=ydl.download, args=([link]), name=f"threadXXXgaming - {meta['title']}")
    return downloadThread, meta

# In Progress
async def addSongToQueue(arg):
  return 

async def clearQueue(ctx, serverid):
  global curQueue, songQueue, queueLen
  songCleared = 0
  try:
    await ctx.send(f"active threads : {threading.active_count()}")
    for thread in threading.enumerate():
      await ctx.send(f"{thread.name}, alive: {thread.is_alive()}")
  except Exception as e:
    await ctx.send(e)
  try:
    for songNum in range(0,len(songQueue)+1):
      #check if the song is playing or the list is empty
      if(curQueue != songNum): 
        try:
          os.remove(f"server/{serverid}/music{songNum}.mp3")
          songCleared+=1
        except Exception as e:
          await ctx.send(f"error message : {e}")
          await ctx.send(f"queue number {songNum} failed to be erased")
    songQueue = []
    curQueue=0
    queueLen = len(songQueue)
    await ctx.send(f"{songCleared} songs removed from queue")
  except:
    await ctx.send("clear queue failed")
    pass
  return


async def queue(ctx):
  try:
    for song in songQueue:
      await ctx.send(f"{song}. {song.metaInfo['title']}")
  except:
    await ctx.send("No song in queue")
  await ctx.send(f"curQueue: {curQueue}\nqueueLen: {len(songQueue)}")
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

def checkQueueResidue(serverid, curQueue):
  dir = ""
  try:
    if not os.path.exists(f'server/{serverid}'):
      os.makedirs(f'server/{serverid}')
    os.remove(f'server/{serverid}/music{curQueue}')
  except:
    dir = "no queue residue found"
  return dir

async def rmFromQueue(ctx):
  global queueLen
  index = int(ctx.message.content)
  serverid = ctx.message.guild.id
  songName = songQueue[index].metainfo['title']
  queueLen = len(songQueue)
  try:
    os.remove(f'server/{serverid}/music{curQueue}')
    songQueue.pop(index)
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