from __future__ import unicode_literals
#%%
from pyppeteer import launch
import discord
import asyncio
import json
import os
from types import SimpleNamespace
import youtube_dl
import os

#import time
from discord.ext import commands
from dotenv import load_dotenv
# command prefix s-
client = commands.Bot(command_prefix="s-")

# environment variable
load_dotenv('.env')
TOKEN = os.getenv('TOKEN')

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




#---------------------------------------------------------
#                    in progress zone
#---------------------------------------------------------

# NH SET
lastCodes = []
nhInstanceRunning = False
@client.command() #s-seerNH_here
async def seerNH_here(ctx):
    global nhInstanceRunning
    print(f"{type(str(ctx.channel))}:{str(ctx.channel)}")
    channelid = 0
    # error ga dapet channel id
    channel = discord.utils.get(client.get_all_channels(), name=str(ctx.channel))

    channelid = channel.id
    print(channelid)
    if nhInstanceRunning:
        ctx.send(f"seer sudah aktif")
    else:
        nhInstanceRunning = True
        await NHPLoop(channelid)


async def NHPLoop(channelid): # get 5 codes of popular art on main page
  global nhInstanceRunning
  global lastCodes
  print(channelid)
  while nhInstanceRunning:
    channel = client.get_channel(channelid)
    [codes, thumbnails, captions] = await getNHPopular()
    if len(lastCodes) == 0: # first time run
      for i in range(0, len(codes)):
        # https://stackoverflow.com/questions/64527464/clickable-link-inside-message-discord-py
        tags = await getTagsFromCode(codes[i])
        embed = discord.Embed()
        print(thumbnails[i])
        print("\n")
        embed.set_image(url=thumbnails[i])
        embed.description = f"{captions[i]}\n\nTags: •{' •'.join(tags)}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
        await channel.send(embed=embed)
      lastCodes = codes
    else: # in loop
      adaBeda = False
      for i in range(0, len(codes)):
        if codes[i] in lastCodes:
          pass
        else:
          adaBeda = True
          embed = discord.Embed()
          print(thumbnails[i])
          print("\n")
          embed.set_image(url=thumbnails[i])
          embed.description = f"{captions[i]}\n\nTags: •{' •'.join(tags)}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
          await channel.send(embed=embed)
      if not adaBeda:
        await channel.send("no new art in popular(main page")
    await asyncio.sleep(3600)

# this is the scrap function 
async def getNHPopular():
  browser = await launch(ignoreHTTPSErrors = True, headless = True, args=["--no-sandbox"])
  page = await browser.newPage()
  await page.goto('https://nhentai.net')

  # ambil tag div popular
  popularDiv = await page.querySelector(".container.index-container.index-popular")

  # buat list yang isinya anchor dari karya popular
  anchorInPopularDiv = await popularDiv.querySelectorAll(".cover")
  codes = []
  thumbnails = []
  captions = []

  # olah setiap anchor untuk di ekstrak kode dan thumbnailnya
  for a in anchorInPopularDiv:
    code = await page.evaluate('(ele) => ele.getAttribute("href")', a)
    code = code[3:-1]

    thumbnailURL = await page.evaluate('(ele) => ele.querySelector("img").getAttribute("src")', a)

    caption = await page.evaluate('(ele) => ele.querySelector("div").innerText', a)

    print(thumbnailURL)
    codes.append(code)
    thumbnails.append(thumbnailURL)
    captions.append(caption)
    
  await browser.close()
  return [codes, thumbnails, captions]
#%%
async def getTagsFromCode(code = "370616"):
  browser = await launch(ignoreHTTPSErrors = True, headless = True, args=["--no-sandbox"])
  page = await browser.newPage()
  await page.goto(f"https://nhentai.net/g/{code}/")
  spanTag = await page.querySelectorAll("span.tags")
  spanTag = spanTag[2]
  anchorTags = await spanTag.querySelectorAll("a")
  tags = []
  for a in anchorTags:
    tag = await page.evaluate('(ele) => ele.querySelector("span.name").innerText', a)
    tags.append(tag)
  await page.close()
  await browser.close()
  return tags
#%%



#ABSEN UNDIP SET

textCodeDict = {
  69: "OK",
  420: "NO CREDENTIAL",
  13: "NOT ENOUGH INFORMATION"
}

class Server():
  def __init__(self) -> None:
      pass


class Mahasiswa(): #kelas mahasiswa
  def __init__(self, id, mail = "NOT SET", password = "NOT SET"):
      self.id = id
      self.mail = mail
      self.password = password

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
  print(properties)
  print(value)
  if properties == "" or value == "":
    await ctx.send("pastikan pengejaannya benar!")
  else:
    properties = properties.lower()
    if properties in ["mail", "password"]:
      
      with open("MAHASISWA.json", "r+") as f:
        content = f.read()
        #JSON to python Object not dict
        print(f"content = {content}")
        mahasiswas = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
        print(f"mahasiswas = {mahasiswas}")
        
        for mahasiswa in mahasiswas:
          
          print(f"{mahasiswa.id} == {ctx.author.id}")
          if mahasiswa.id == ctx.author.id:
            if properties == "mail":
              mahasiswa.mail = value
            elif properties == "password":
              mahasiswa.password = value
            # eval(f"mahasiswa.{properties} = \"{value}\"")
            censored = '\*'.join(['' for _ in range(0, len(value) -2)])
            await ctx.message.delete()
            await ctx.send(f"{properties} telah diset menjadi {censored}{value[-2]}{value[-1]}")
            break

        else:
          print(ctx.author.id)
          eval(f"mahasiswas.append(Mahasiswa(ctx.author.id, {properties} = '{value}'))")
        print(mahasiswas)
        mahasiswas = json.dumps([mahasiswa.__dict__ for mahasiswa in mahasiswas])
        print(mahasiswas)
        f.seek(0)
        f.write(mahasiswas)
        f.truncate()
        f.close()
    else:
      ctx.send("properti kemungkinan salah pengejaan")


@client.command() # MAIN FUNCTION
async def absen(ctx, codeOrLink):
  with open("MAHASISWA.json", "w+") as f:
    mahasiswas = json.loads(f.read())
    [index, password, mail, resultCode] = await credential_check_of(mahasiswas, ctx.author.id)
    if resultCode == textCodeDict[69]:
      text = "OK"
      browser = await launch(headless = False)
      page = await browser.newPage()
      page.goto("https://form.undip.ac.id/questioner/monitoring_covid#")
    elif resultCode == textCodeDict[420]:
      text = "penuhi credential"
    elif resultCode == textCodeDict[13]:
      text = "belum di inisialisasi"
    f.close()
      
    
@client.command()
async def sendMonitorCovid(ctx):
  with open("MAHASISWA.json", "w+") as f:
    pass
  


async def credential_check_of(mahasiswas, idTarget):
  textCode = ''
  [password, mail] = ["*", "*"]
  index = None
  for i, mahasiswa in enumerate(mahasiswas):
    if mahasiswa.id == idTarget:
      password = mahasiswa.password
      mail = mahasiswa.mail
      index = i
      if mahasiswa.mail != "*" and mahasiswa.password != "*":
        textCode = textCodeDict[69]
        pass
      else:
        textCode = textCodeDict[13] #belum lengkap credential
      break
  else:
    #not created
    textCode = textCodeDict[420]
  return index, password, mail, textCode


# all about voice channel
@client.command()
async def play(ctx, *linkYoutubeOrSongName):
  # grab the user who sent the command
  user=ctx.message.author
  voice_channel=user.voice.channel
  
  # kalau bukan link
  print(linkYoutubeOrSongName)
  if not "youtube.com" in linkYoutubeOrSongName:
    linkYoutubeOrSongName = "+".join(linkYoutubeOrSongName)
    linkYoutubeOrSongName = await searchVideoByName(linkYoutubeOrSongName)
    
    
  # only play music if user is in a voice channel
  if voice_channel!= None:
      # download
      await ctx.send(f"downloading: {linkYoutubeOrSongName}")
      try:
        f = open("music.mp3")
        os.remove("music.mp3")
      except:
        pass
      print(linkYoutubeOrSongName)
      meta = await downloadmp3(linkYoutubeOrSongName)
      await ctx.send(f"Playing: {meta['title']}\nUploader: {meta['uploader']}\nViews: {meta['title']}")

      # create StreamPlayer
      vc= await voice_channel.connect()
      vc.play(discord.FFmpegPCMAudio('test'), after=lambda e: print("done", e))
      #player = vc.create_ffmpeg_player('test.m4a', after=lambda: print('done'))
      while vc.is_playing():
          await asyncio.sleep(1)
      # disconnect after the player has finished
      vc.stop()
      await vc.disconnect()
  else:
      await client.say('User is not in a channel.')

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

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


async def getInfoYoutube(linkYoutubeOrSongName):
  """mengembalikan informasi video\n
  url\n
  judul\n
  durasi
  """
 
  
async def searchVideoByName(namaLagu):
  """return link
  """
  browser = await launch(ignoreHTTPSErrors = True, headless = True, args=["--no-sandbox"])
  page = await browser.newPage()
  await page.goto(f"https://www.youtube.com/results?search_query={namaLagu}")
  print(page.url)
  anchorTitles = await page.querySelectorAll("#video-title")
  
  subjectAnchor = anchorTitles[0]
  
  href = await page.evaluate('(ele) => ele.getAttribute("href")', subjectAnchor)
  await browser.close()
  return f"https://www.youtube.com{href}"



































print(TOKEN)
client.run(TOKEN)

# client.run("drop your discord bot token here")




# sleep coroutine https://discordpy.readthedocs.io/en/stable/faq.html#what-is-a-coroutine

# on repl.it if not working :
# install-pkg gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

# %%