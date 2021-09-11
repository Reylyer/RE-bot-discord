import discord, os
from types import SimpleNamespace
import json
from pyppeteer import launch
import asyncio

class StoredCodes:
  def __init__(self, tag, freq, codes):
    self.tag = tag
    self.freq = freq
    self.codes = codes

class NhSession:
  def __init__(self, tag: str, freq: str, amount: int, sessionName: str, channel: str, server: str) -> None:
   
    self.tag = tag
    self.freq = freq
    self.amount = amount
    self.sessionName = sessionName
    self.running = True
    self.channel = channel
    self.server = server
    self.savedCodes = []
    self.lastCodes = []


try:
  os.mkdir('server')
except:
  pass


async def stopSeering(client, ctx, sessionName):
  """ this function will stop a session given by its sessionName
  """
  # read json
  channel = discord.utils.get(client.get_all_channels(), name=str(ctx.channel))
  with open(f"server/{ctx.guild.id}/nhSessions.json", "r+") as f:
    content = f.read()
    nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
    for nhSession in nhSessions:
      await ctx.send(nhSession.__dict__)
      if nhSession.sessionName is sessionName:
        # ketemu
        nhSession.running = False
        break
    else:
      await ctx.send(f"Tidak ada nhSession dengan nama {sessionName}")
    f.seek(0)
    f.write(nhSessions)
    f.truncate()
    f.close()

      
  # check if exist session with $sessionName

  # else show all session within the channel invoked

async def seerNH_here(client, ctx, *args):
  """ mengaktifkan nhSession 
  """
  # get channel where seerNH_here invoked
  channel = discord.utils.get(client.get_all_channels(), name=str(ctx.channel))
  with open(f"server/{ctx.guild.id}/nhSessions.json", "r+") as f:
    content = f.read()
    nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
    for nhSession in nhSessions:
      await ctx.send(nhSession.__dict__)
      if nhSession.sessionName is sessionName:
        # ketemu
        await ctx.send(f"nhSession dengan nama {sessionName}, sudah dijalankan")
    else:
      await ctx.send(f"Tidak ada nhSession dengan nama {sessionName}")
    f.seek(0)
    f.write(nhSessions)
    f.truncate()
    f.close()
  await NHPLoop(channel, args)

async def NHPLoop(channel, args): # get 5 codes of popular art on main page
  print(args)
  
  # lowering the args
  args = [arg.lower() for arg in args]
  
  # process args
  # --tag
  # --frequency
  # --amount    amount is like grab top # but can be in recent too
  additionalSelector = "" # this is for main page
  if len(args) is 0:
    additionalSelector = ".index-popular"
    tag = "main"
    freq = ""
    amount = 5
  
  helpList = [arg for arg in args if "--help" in arg]
  print(helpList)
  if len(helpList) is 1:
    await channel.send("melakukan scrap di website kesayangan(nh)\n\nformat cmd: s-seerNH_here --tag=optional --freq=optional --amount=optional --sessionName\nuntuk freq hanya bisa recent, today, week, all-time\nuntuk amount untuk main page 1-5, selain itu 1-25\npastikan tag benar ada! kalau ada spasi ganti dengan \"-\"")
    return

  # input tag
  tagList = [arg for arg in args if "--tag=" in arg]
  print(tagList)
  if len(tagList) is 1:
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
  freqList = [arg for arg in args if "--freq=" in arg]
  print(freqList)
  if len(freqList) is 1 and "recent" not in freqList[0]:
    freq = freqList[0][freqList[0].index("=") + 1:]
    prefix = "popular"
    if freq is "all-time": # all-time = https://nhentai.net/tag/{yourtag}/popular
      freq = prefix
    else:
      freq = f"{prefix}-{freq}"
  else:
    freq = ""
  print(f"freq = {freq}")
  
  # input amount
  # valid input 1 - 25 if not main page else just 1 - 5
  # not support for multiple pages
  amountList = [arg for arg in args if "--amount=" in arg]
  if len(amountList) is 1:
    amount = int(amountList[0][amountList[0].index("=") + 1:])
    if amount < 1:
      await channel.send("ngajak berantem?")
      return
  else:
    amount = 5
  print(f"amount = {amount}")
  
  # session name
  # valib input no spaces
  sessionNameList = [arg for arg in args if "--sessionName=" in arg]
  if len(sessionNameList) is 1:
    sessionName = sessionNameList[0][sessionNameList[0].index("=") + 1:]
  else:
    sessionName = f"{channel.name}_{tag}_{freq}_{amount}"
    



  # check and create session if exist return
  f = open(f"/server/{channel.guild.id}/nhcode.json", "r+")
  content = f.read()
  nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))

  for nhSession in nhSessions:
    if nhSession.sessionName is sessionName:
      await channel.send(f"There is conflict session name.\nSession with name '{sessionName}' is existed, try to use other name... TERMINATING")
      info = "```py\nSession with same name:\n\n"
      info += f"server      = {nhSession.server}\n"
      info += f"channel     = {nhSession.channel}\n"
      info += f"tag         = {nhSession.tag}\n"
      info += f"freq        = {nhSession.freq}\n"
      info += f"amount      = {nhSession.amount}"
      info += f"sessionName = {nhSession.sessionName}\n```"
      await channel.send(info)
      f.close()
      return
  else:
    await channel.send("sessionName check: OK")
    newNhSession = NhSession(tag, freq, amount, sessionName, channel.name, channel.guild.name)
    nhSessions.append(newNhSession)
    nhSessions = json.dumps(nhSessions.__dict__)
    await channel.send(nhSessions)
    f.seek(0)
    f.write(nhSessions)
    f.truncate()
    f.close()

  # lulus check informasi seering
  info = "```py\nseering Info:\n\n"
  info += f"server      = {channel.guild.name}\n"
  info += f"channel     = {channel.name}\n"
  info += f"tag         = {tag}\n"
  info += f"freq        = {freq}\n"
  info += f"amount      = {amount}"
  info += f"sessionName = {sessionName}\n```"
  await channel.send(info)

  nhSessionRunning = True

  subjectLink = "https://nhentai.net"
  if tag is not "main":
    subjectLink +=  f"/tag/{tag}/{freq}"
  
  while nhSessionRunning:
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

    f = open(f"/server/{channel.guild.id}/nhcode.json", "r+")
    content = f.read()
    print(f"content = {content}")
    nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))

    # debug
    try:
      await channel.send(f"nhSessions = {nhSessions}")
    except Exception as e:
      await channel.send(e)

    # debug 
    try:
      for nhSession in nhSessions:
        if nhSession.sessionName is sessionName:
          if not nhSession.running:
            return
          subjectNhSession = nhSession
          break
    except:
      pass
    # subjectNhSession -> NhSession Object

    

    try:
      [codes, captions] = await nhScraper(subjectLink, additionalSelector, amount)
    except Exception as e:
      await channel.send(f"some error has occurred\nError message:{e}")
      return

    if len(lastCodes) == 0: # first time run on certain tag and freq
      for i in range(0, len(codes)):
        # https://stackoverflow.com/questions/64527464/clickable-link-inside-message-discord-py
        [tags, thumbnail, pages] = await getTagsAndThumbnailAndPagesFromCode(codes[i])
        embed = discord.Embed()
        if "http" not in thumbnail:
          await channel.send(f"can't load the thumbnail, thumbnail fed: {thumbnail}")
        else:
          embed.set_image(url=thumbnail)
        embed.description = f"{captions[i]}\n\nTags: •{' •'.join(tags)}\nPages: {pages}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
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
          [tags, thumbnail, pages] = await getTagsAndThumbnailAndPagesFromCode(codes[i])
          embed = discord.Embed()
          print(thumbnail)
          print("\n")
          if "http" not in thumbnail:
            await channel.send(f"can't load the thumbnail, thumbnail fed: {thumbnail}")
          else:
            embed.set_image(url=thumbnail)
          embed.description = f"{captions[i]}\n\nTags: •{' •'.join(tags)}\nPages: {pages}\n\n[#{codes[i]}](https://nhentai.net/g/{codes[i]})."
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
    savedCodes = json.dumps([savedCode.__dict__ for savedCode in savedCodes])
    print(savedCodes)
    f.seek(0)
    f.write(savedCodes)
    f.truncate()
    f.close()
    await asyncio.sleep(3600)


# this is the scrap function 
async def nhScraper(subjectLink: str, additionalSelector: str, amount: int) -> list[list[str], list[str]]:
  """this is the scrap function """
  browser = await launch(ignoreHTTPSErrors = True, headless = True, args=["--no-sandbox"])
  page = await browser.newPage()
  await page.goto(subjectLink)

  # ambil tag div popular
  subjectDiv = await page.querySelector(f".container.index-container{additionalSelector}")

  # buat list yang isinya anchor dari karya popular
  subjectAnchor = await subjectDiv.querySelectorAll(".cover")
  codes = []
  #thumbnails = []
  captions = []
  if amount > len(subjectAnchor):
    amount = len(subjectAnchor)
  # olah setiap anchor untuk di ekstrak kode dan thumbnailnya
  for i in range(0, amount):
    code = await page.evaluate('(ele) => ele.getAttribute("href")', subjectAnchor[i])
    code = code[3:-1]

    #thumbnailURL = await page.evaluate('(ele) => ele.querySelector("img").getAttribute("src")', subjectAnchor[i])
    caption = await page.evaluate('(ele) => ele.querySelector("div").innerText', subjectAnchor[i])

    #print(thumbnailURL)
    print(code)
    codes.append(code)
    #thumbnails.append(thumbnailURL)
    captions.append(caption)
    
  await browser.close()
  return [codes, captions]


async def getTagsAndThumbnailAndPagesFromCode(code: str = "177013") -> list[list[str], str, str]:
  """return tags, thumbail url and pages count given code """
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
  imgThumbnail = await page.querySelector(".lazyload")
  thumbnailURL = await page.evaluate("""(ele) => ele.getAttribute("data-src")""", imgThumbnail)
  anchorPages = await page.querySelectorAll("a.tag")
  anchorPages = anchorPages[-1]
  pages =  await page.evaluate(""" (ele) => ele.querySelector("span.name").innerText """, anchorPages)
  await page.close()
  await browser.close()
  return [tags, thumbnailURL, pages]
