import asyncio, discord, datetime, youtube_dl, threading
from discord.enums import Theme
from youtubesearchpython import VideosSearch
# import os

class Song:
  def __init__(self, metaInfo, queueOrder, link):
    self.metaInfo = metaInfo
    self.queueOrder = queueOrder
    self.link = link

    pass

songQueue = []
curQueue = 0
queueLen = 0
# 

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
  if voice_channel!= None:
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
      
      
      # try:
      #   _ = open(f"music{curQueue}.mp3")
      #   os.remove(f"music{curQueue}.mp3")
      # except:
      #   pass
      
      # download
      await ctx.send(f"downloading: <{arg}>")
      await ctx.send(f"voice_client = {voice_client}")
      song = Song(downloadmp3(arg), curQueue, arg)
      
      songQueue.append(song)
      
      # meta = downloadmp3(arg)
      # expected : it will wait until the thread is finished(hopefully (pretty please (first run ok?)))
      await ctx.send("before thread check")
      await ctx.send(f"type of threading.enumerate() = {type(threading.enumerate())}")
      await ctx.send(threading.enumerate())
      await ctx.send(threading.enumerate()[0].is_alive())
      while len(['' for thread in threading.enumerate() if thread.name == arg]):
        # thread.name is == youtube_link in this case arg
        # print([thr.name for thr in threading.enumerate()])
      #while threading.enumerate()[0].is_alive():
        await asyncio.sleep(1)
      await ctx.send("after thread check")
      await ctx.send("finish downloading")
      await ctx.send(f"Playing: {song.metaInfo['title']}\nUploader: {song.metaInfo['uploader']}\nDuration: {str(datetime.timedelta(seconds=song.metaInfo['duration']))}")

      # create StreamPlayer
      # if not user.voice.is_connected():
      voice_client.play(discord.FFmpegPCMAudio(f'music{curQueue}.mp3'), after=lambda e: print("done", e))
      
      if voice_client.is_playing():
        while voice_client.is_playing():
          await asyncio.sleep()
      
      while voice_client.is_playing():
          await asyncio.sleep(1)
      # disconnect after the player has finished
      voice_client.stop()
      # await vc.disconnect()
    except Exception as e:
      await ctx.send(e)
  else:
      await ctx.send('User is not in a channel.')
      
def downloadmp3(link):
  global queueLen
  ydl_opts = {
      'format': 'bestaudio/best',
      'postprocessors': [{
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
      }],
      'outtmpl':f'music{queueLen}.mp3',
  }
  queueLen +=1
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    downloadThread = threading.Thread(target=ydl.download([link]))
    meta = ydl.extract_info(link)
    downloadThread.setName(meta['title'])
    downloadThread.start()
    return meta

# In Progress
async def addSongToQueue(arg):
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
 
  
def searchVideoByName(namaLagu):
  """ VideoSearch Object
  """
  videosSearch = VideosSearch(namaLagu, limit = 2)
  return videosSearch

def getThreadCount():
  return threading.active_count(), threading.current_thread()