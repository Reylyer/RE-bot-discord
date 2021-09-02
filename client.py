from __future__ import unicode_literals
from operator import sub
#%%
from pyppeteer import launch
import discord
import asyncio
import json
import os
import datetime
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
try:
  f = open("nhcode.json")
  f.close()
except:
  with open("nhcode.json", "w") as f:
    f.write(json.dumps([]))
    f.close()

class StoredCodes():
  def __init__(self, tag, freq, codes):
    self.tag = tag
    self.freq = freq
    self.codes = codes

nhInstanceRunning = False

@client.command()
async def stopSeering(ctx):
  global nhInstanceRunning
  await ctx.send("ok")
  nhInstanceRunning = False
@client.command() #s-seerNH_here
async def seerNH_here(ctx, *args):
    global nhInstanceRunning
    
    # get channel where seerNH_here invoked
    channel = discord.utils.get(client.get_all_channels(), name=str(ctx.channel))

    if nhInstanceRunning:
        ctx.send(f"seer sudah aktif")
    else:
        nhInstanceRunning = True
        await NHPLoop(channel, args)


async def NHPLoop(channel, args): # get 5 codes of popular art on main page
  print(args)
  global nhInstanceRunning
  firstCheck = True
  # lowering the args
  args = [arg.lower() for arg in args]
  
  # process args
  # --tag
  # --frequency
  # --amount    amount is like grab top # but can be in recent too
  additionalSelector = ""
  if len(args) == 0:
    additionalSelector = ".index-popular"
    tag = "main"
    freq = ""
    amount = 5
  
  helpList = [arg for arg in args if "--help" in arg]
  print(helpList)
  if len(helpList) == 1:
    await channel.send("melakukan scrap di website kesayangan(nh)\n\nformat cmd: s-seerNH_here --tag=optional --freq=optional --amount=optional\nuntuk freq hanya bisa recent, today, week, all-time\nuntuk amount untuk main page 1-5, selain itu 1-25\npastikan tag benar ada! kalau ada spasi ganti dengan \"-\"")
    nhInstanceRunning = False
    return
  # input tag
  tagList = [arg for arg in args if "--tag" in arg]
  print(tagList)
  if len(tagList) == 1:
    tag = tagList[0][tagList[0].index("=") + 1 :]
  else:
    tag = "main"
  print(f"tag = {tag}")
    
  # input freq
  # valid input for freq
  # recent
  # today
  # week
  # all-time
  # freqList, list is in its name but actually its just element that contains --freq=something
  freqList = [arg for arg in args if "--freq" in arg]
  print(freqList)
  if len(freqList) == 1 and "recent" not in freqList[0]:
    freq = freqList[0][freqList[0].index("=") + 1:]
    prefix = "popular"
    if freq == "all-time": # all-time = https://nhentai.net/tag/{yourtag}/popular
      freq = prefix
    else:
      freq = f"{prefix}-{freq}"
  else:
    freq = ""
  print(f"freq = {freq}")
  
  # input amount
  # valid input 1 - 25 if not main page else just 1 - 5
  # not support for multiple pages
  amountList = [arg for arg in args if "--amount" in arg]
  if len(amountList) == 1:
    amount = int(amountList[0][amountList[0].index("=") + 1:])
    if amount < 1:
      await channel.send("ngajak berantem?")
      nhInstanceRunning = False
      return
  else:
    amount = 5
  print(f"amount = {amount}")
  
  
 
    
  subjectLink = "https://nhentai.net"
  if tag != "main":
    subjectLink +=  f"/tag/{tag}/{freq}"
    
  while nhInstanceRunning:
    with open("nhcode.json", "r+") as f:
      content = f.read()
      #JSON to python Object
      print(f"content = {content}")
      savedCodes = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
      # savedCodes structures
      # [
      #  {
      #   "tag": "some-tag1",
      #   "freq": "freq-types2",
      #   "codes": [...,...,...]
      #  },{
      #   "tag": "some-tag2",
      #   "freq": "freq-types2"
      #   "codes": [...,...,...]
      #  }
      # ]
      # 
      print(f"codes = {savedCodes}")
      # resuming from saved codes
      lastCodes = []
      if firstCheck:
        for savedCode in savedCodes:
          if savedCode.tag == tag and savedCode.freq == freq:
            lastCodes = savedCode.codes
            break
        firstCheck = False
      print(lastCodes)
      try:
        [codes, thumbnails, captions] = await nhScraper(subjectLink, additionalSelector, amount)
      except Exception as e:
        await channel.send(f"some error has occurred\nError message:{e}")
        return
      if len(lastCodes) == 0: # first time run on certain tag and freq
        for i in range(0, len(codes)):
          # https://stackoverflow.com/questions/64527464/clickable-link-inside-message-discord-py
          tags = await getTagsFromCode(codes[i])
          embed = discord.Embed()
          if "http" not in thumbnails[i]:
            await channel.send(f"can't load the thumbnail, thumbnail fed: {thumbnails[i]}")
          else:
            embed.set_image(url=thumbnails[i])
          embed.description = f"{captions[i]}\n\nTags: •{' •'.join(tags)}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
          await channel.send(embed=embed)
        lastCodes = codes
        newStoredCodes = StoredCodes(tag, freq, codes)
        
        savedCodes.append(newStoredCodes)
      else: # in loop
        adaBeda = False
        codeBeda = []
        for i in range(0, len(codes)):
          if codes[i] in lastCodes:
            pass
          else:
            codeBeda.append(codes[i])
            adaBeda = True
            embed = discord.Embed()
            print(thumbnails[i])
            print("\n")
            if "http" not in thumbnails[i]:
              await channel.send(f"can't load the thumbnail, thumbnail fed: {thumbnails[i]}")
            else:
              embed.set_image(url=thumbnails[i])
            embed.description = f"{captions[i]}\n\nTags: •{' •'.join(tags)}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
            await channel.send(embed=embed)
        if not adaBeda:
          await channel.send("no new art in popular(main page)")
        else:
          for savedCode in savedCodes:
            if savedCode.tag == tag and savedCode.freq == freq:
              for code in codeBeda:
                savedCode.codes.append(code)
              break
          lastCodes = codes
      f.seek(0)
      f.write(savedCodes)
      f.truncate()
      f.close()
      await asyncio.sleep(3600)

# this is the scrap function 
async def nhScraper(subjectLink, additionalSelector, amount):
  browser = await launch(ignoreHTTPSErrors = True, headless = True, args=["--no-sandbox"])
  page = await browser.newPage()
  await page.goto(subjectLink)

  # ambil tag div popular
  subjectDiv = await page.querySelector(f".container.index-container{additionalSelector}")

  # buat list yang isinya anchor dari karya popular
  subjectAnchor = await subjectDiv.querySelectorAll(".cover")
  codes = []
  thumbnails = []
  captions = []
  if amount > len(subjectAnchor):
    amount = len(subjectAnchor)
  # olah setiap anchor untuk di ekstrak kode dan thumbnailnya
  for i in range(0, amount):
    code = await page.evaluate('(ele) => ele.getAttribute("href")', subjectAnchor[i])
    code = code[3:-1]

    thumbnailURL = await page.evaluate('(ele) => ele.querySelector("img").getAttribute("src")', subjectAnchor[i])
    caption = await page.evaluate('(ele) => ele.querySelector("div").innerText', subjectAnchor[i])

    print(thumbnailURL)
    print(code)
    codes.append(code)
    thumbnails.append(thumbnailURL)
    captions.append(caption)
    
  await browser.close()
  return [codes, thumbnails, captions]

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
vc = 0
@client.command()
async def play(ctx, *linkYoutubeOrSongName):
  global vc
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
    channel = ctx.author.voice.channel
    if vc == 0:
      vc = await voice_channel.connect()
    #vc = ctx.voice_client

    # download
    await ctx.send(f"downloading: {linkYoutubeOrSongName}")
    try:
      f = open("music.mp3")
      os.remove("music.mp3")
    except:
      pass
    print(linkYoutubeOrSongName)
    meta = await downloadmp3(linkYoutubeOrSongName)
    await ctx.send(f"Playing: {meta['title']}\nUploader: {meta['uploader']}\nDuration: {str(datetime.timedelta(seconds=meta['duration']))}")

    # create StreamPlayer
    # if not user.voice.is_connected():
    
    vc.play(discord.FFmpegPCMAudio('music.mp3'), after=lambda e: print("done", e))
    #player = vc.create_ffmpeg_player('test.m4a', after=lambda: print('done'))
    while vc.is_playing():
        await asyncio.sleep(1)
    # disconnect after the player has finished
    vc.stop()
    # await vc.disconnect()
  else:
      await client.say('User is not in a channel.')

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
@client.command()
async def pause(ctx):
  await ctx.voice_client.pause()
@client.command()
async def resume(ctx):
  await ctx.voice_client.resume()
@client.command()
async def stop(ctx):
  await ctx.voice_client.stop()
@client.command()
async def is_connected(ctx):
  await ctx.send(str(ctx.voice_client.is_connected()))
@client.command()
async def is_playing(ctx):
  await ctx.send(str(ctx.voice_client.is_playing()))
@client.command()
async def is_paused(ctx):
  await ctx.send(str(ctx.voice_client.is_paused()))


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








@client.command() # set pass n mail
async def ip(ctx):
  await ctx.send("20.85.244.255")


























print(TOKEN)
client.run(TOKEN)

# client.run("drop your discord bot token here")




# sleep coroutine https://discordpy.readthedocs.io/en/stable/faq.html#what-is-a-coroutine

# on repl.it if not working :
# install-pkg gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

