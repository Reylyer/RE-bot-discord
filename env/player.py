import asyncio
import discord
import datetime
import youtube_dl
from youtubesearchpython import VideosSearch

async def play(client, ctx, *arg):
  # grab the user who sent the command
  user=ctx.message.author
  voice_channel=user.voice.channel
  
  # kalau bukan link
  print(arg)
  if not "youtu" in arg:
    arg = " ".join(arg)
    arg = await searchVideoByName(arg)

    arg = arg.result()["result"][0]["link"]

    await ctx.send(arg)
    
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
      await ctx.send(f"typeof ctx.message.author.voice.channel = {type(ctx.message.author.voice.channel)}, with value = {ctx.message.author.voice.channel}")
      await ctx.send(f"ctx.guild.voice_channels = {ctx.guild.voice_channels}")
      channel = ctx.message.author.voice.channel
      voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
      await ctx.send(f"voice_client = {voice_client}")
      if not voice_client is None: #test if voice is 
        try:
          b = vars(voice_client)
          await ctx.send(', '.join("%s: %s" % item for item in b.items()))
        except Exception as e:
          await ctx.send(e)
        await ctx.send(f"connecting{ctx.message.author.voice.channel}")
        if not voice_client.is_connected():
          voice_client = await channel.connect()
      else:
        try:
          voice_client = await channel.connect()
          await ctx.send(f"voice_client = {voice_client}")
        except Exception as e:
          await ctx.send(e)
      # vc = ctx.voice_client

      # download
      await ctx.send(f"downloading: {arg}")
      try:
        f = open("music.mp3")
        os.remove("music.mp3")
      except:
        pass
      print(arg)
      await ctx.send(f"voice_client = {voice_client}")
      meta = await downloadmp3(arg)
      await ctx.send(f"Playing: {meta['title']}\nUploader: {meta['uploader']}\nDuration: {str(datetime.timedelta(seconds=meta['duration']))}")

      # create StreamPlayer
      # if not user.voice.is_connected():
      await ctx.send(f"voice_client = {voice_client}")
      voice_client.play(discord.FFmpegPCMAudio('music.mp3'), after=lambda e: print("done", e))
      #player = vc.create_ffmpeg_player('test.m4a', after=lambda: print('done'))
      while voice_client.is_playing():
          await asyncio.sleep(1)
      # disconnect after the player has finished
      voice_client.stop()
      # await vc.disconnect()
    except Exception as e:
      await ctx.send(e)
  else:
      await ctx.send('User is not in a channel.')
      
async def downloadmp3(link):
  ydl_opts = {
      'format': 'bestaudio/best',
      'postprocessors': [{
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
      }],
      'outtmpl':'music.mp3',
  }
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      ydl.download([link])
      meta = ydl.extract_info(link)
      return meta

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
      
async def getInfoYoutube(linkYoutubeOrSongName):
  """mengembalikan informasi video\n
  url\n
  judul\n
  durasi
  """
 
  
async def searchVideoByName(namaLagu):
  """ VideoSearch Object
  """
  videosSearch = VideosSearch(namaLagu, limit = 2)
  return videosSearch
