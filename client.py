from pyppeteer import launch
import discord
import asyncio
#import time

from discord.ext import commands

client = commands.Bot(command_prefix="s-")

    
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
  while(nhInstanceRunning):
    channel = client.get_channel(channelid)
    [codes, thumbnails, captions] = await getNHPopular()
    if len(lastCodes) == 0: # first time run
      for i in range(0, len(codes)):
        # https://stackoverflow.com/questions/64527464/clickable-link-inside-message-discord-py
        embed = discord.Embed()
        print(thumbnails[i])
        print("\n")
        embed.set_image(url=thumbnails[i])
        embed.description = f"{captions[i]}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
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
          embed.description = f"{captions[i]}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
          await channel.send(embed=embed)
      if not adaBeda:
        await channel.send("no new art in popular(main page")
    await asyncio.sleep(3600)
  


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
    thumbnails.append((thumbnailURL))
    captions.append(caption)
      
  await browser.close()
  return [codes, thumbnails, captions]

client.run("NzQ1MjI0NjU1MzU4NjU2NTMy.Xzuqiw.Xm73-Tv2u2zmLz-IBjr8yqV-IVM")


    
  
# sleep coroutine https://discordpy.readthedocs.io/en/stable/faq.html#what-is-a-coroutine

# on repl.it if not working : 
# install-pkg gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget