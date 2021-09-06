import asyncio, discord, datetime, youtube_dl, threading
from posixpath import pardir
from discord.enums import Theme
from youtubesearchpython import VideosSearch
import os

class Song:
  def __init__(self, metaInfo, queueOrder, link):
    self.metaInfo = metaInfo
    self.queueOrder = queueOrder
    self.link = link

    pass
try:
  os.mkdir('server')
except:
  pass
serverDir = (f"{os.getcwd()}\server")
songQueue = []
curQueue = 0
queueLen = 0
# 

async def play(client, ctx, *arg):
  global curQueue
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
        try:
          b = vars(voice_client)
          await ctx.send(', '.join("%s: %s" % item for item in b.items()))
        except Exception as e:
          await ctx.send(e)
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
      dirMsg = checkQueueResidue(serverID)
      if dirMsg:
        await ctx.send(dirMsg)
      await ctx.send("before check residue")
      song = Song(downloadmp3(arg, serverID), curQueue, arg)
      await ctx.send("after check residue")
      songQueue.append(song)
      
      # meta = downloadmp3(arg)
      # expected : it will wait until the thread is finished(hopefully (pretty please (first run ok?)))
      await ctx.send("before thread check")
      await ctx.send(f"type of threading.enumerate() = {type(threading.enumerate())}")
      await ctx.send(threading.enumerate())
      await ctx.send(threading.enumerate()[0].is_alive())
      for thread in threading.enumerate():
        if thread.name == f"threadXXXgaming{curQueue}":
          await asyncio.sleep(1)
          await ctx.send(f"hey! thread with name {thread.name} is still alive\nthread.is_alive value = {thread.is_alive()}")

      #while threading.enumerate()[0].is_alive():
        await asyncio.sleep(1)
      await ctx.send("after thread check")
      await ctx.send("finish downloading")
      await ctx.send(f"Playing: {song.metaInfo['title']}\nUploader: {song.metaInfo['uploader']}\nDuration: {str(datetime.timedelta(seconds=song.metaInfo['duration']))}")
      await ctx.send(f"serverDir: {serverDir}")
      # wait for player stop
      if voice_client.is_playing():
        while voice_client.is_playing():
          await asyncio.sleep(1)
      
      # create StreamPlayer
      # Note: stupid solution but at least it worked
      # if not user.voice.is_connected():
      voice_client.play(discord.FFmpegPCMAudio(f'server\{serverID}\music{curQueue}.mp3'), after=lambda e: print("done", e))
      curQueue+=1
      
      while voice_client.is_playing():
          await asyncio.sleep(1)
      # disconnect after the player has finished
      voice_client.stop()
      # await vc.disconnect()
    except Exception as e:
      await ctx.send(e)
  else:
      await ctx.send('User is not in a channel.')
      await ctx.send(ctx.message.author.voice.channel)
      
def downloadmp3(link, serverid):
  global queueLen
  ydl_opts = {
      'format': 'bestaudio/best',
      'postprocessors': [{
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
      }],
      'outtmpl':f'server\{serverid}\music{queueLen}.mp3',
  }
  queueLen +=1
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    downloadThread = threading.Thread(target=ydl.download, args=([link]), name="threadXXXgaming{queueLen}")
    meta = ydl.extract_info(link)
    try:
      downloadThread.start()
    except Exception as e:
      print("error when running thread({downloadThread.name}) error message: {e}")
      
    return meta

# In Progress
async def addSongToQueue(arg):
  return 

async def clearQueue(ctx):
  global queueLen, curQueue, songQueue
  songCleared = 0
  try:
    await ctx.send(f"active threads : {threading.active_count()}")
    for thread in threading.enumerate():
      await ctx.send(f"{thread.name}, alive: {thread.is_alive()}")
  except Exception as e:
    await ctx.send(e)
  try:
    for songNum in range(0,queueLen):
      #check if the song is playing or the list is empty
      if(curQueue != songNum): 
        try:
          os.remove(f"music{songNum}.mp3")
          songCleared+=1
        except Exception as e:
          await ctx.send(f"error message : {e}")
          await ctx.send(f"queue number {songNum} failed to be erased")
    songQueue = []
    curQueue=0
    await ctx.send(f"{songCleared} songs removed from queue")
    queueLen=0
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
  return


async def voice_status(ctx, client):
  print(client.voice_clients)
  await ctx.send(type(client.voice_clients))
  await ctx.send(client.voice_clients)
  for a in client.voice_clients:
    await ctx.send(type(a))
    try:
      b  = vars(a)
      await ctx.send(', '.join("%s: %s" % item for item in b.items()))
    except:
      pass

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

def checkQueueResidue(serverid):
  global curQueue
  dir = ""
  try:
    os.chdir('server')
    try:
      os.mkdir(f'{serverid}')
      dir = f"server dir ({serverid}) is made"
    except:
      pass
    os.chdir(os.pardir)
    os.remove(f'server\{serverid}\music{curQueue}')
  except:
    dir = "no queue residue found"
  return dir

  
def searchVideoByName(namaLagu):
  """ VideoSearch Object
  """
  videosSearch = VideosSearch(namaLagu, limit = 2)
  return videosSearch

def getThreadCount():
  return threading.active_count(), threading.current_thread()