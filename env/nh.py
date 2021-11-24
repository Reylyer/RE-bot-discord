from __future__ import annotations
import discord, os, sys, requests
from types import SimpleNamespace
import json, re
from pyppeteer import launch
import asyncio, threading

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
    os.mkdir('servers')
except:
    pass

import requests

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
def intagRecovery(stringss):
    inTags = []
    instreak = False
    for char in stringss:
        if char == ">":
            temp = ""
            instreak = True
        elif char == "<" and instreak:
            if temp == "":
                continue
            inTags.append(temp)
            temp = ""
            instreak = False
        elif instreak:
            temp += char
    return inTags

def scrapFromCode(code: str) -> dict:
    """
    Parameter
    ----------
    `code`: string
        a string of code that represents the art
        biasa disebut `kode nuklir` terdiri dari
        5 atau 6 digit, biasa terletak di address atau 
        cover
        `https://nhentai.net/g/******`
    
    Return
    ------
    `info` : dictionary
        dictionary untuk kode yang diberikan

        key value pair:
        code       : string 
        altcode    : string
        thumbnail  : string
        title_en   : string
        title_jp   : string
        parodies   : list[string]
        characters : dict
        tags       : dict
        artists    : dict
        groups     : dict
        languages : dict
        categories : dict
        Pages      : integer
    """
    htmlkotor = requests.get(f"https://nhentai.net/g/{code}").text
    infoSection = htmlkotor.split("\n")
    # print("\n\n".join(infoSection))
    # print(len(infoSection))
    # print(code)

    title1 = htmlkotor[infoSection[4].find("""<span class="pretty">""") + 25:infoSection[4].find("""</span><span class="after">""") + 4]
    title2 = htmlkotor[find_nth(infoSection[4], """<span class="pretty">""", 2) + 25:find_nth(infoSection[4], """</span><span class="after">""", 2)]
    


    altcodeIndex = infoSection[4].find("""https://t.nhentai.net/galleries/""") + 36
    altCode = htmlkotor[altcodeIndex: altcodeIndex + 7]
    if not altCode.isnumeric:
        altCode = altCode[:-1]
    thumbnail = htmlkotor[altcodeIndex - 32: altcodeIndex + 17]
    # print(thumbnail)
    parodiesSection = infoSection[6]
    characterSection = infoSection[8]
    tagsSection = infoSection[10]
    artistSection = infoSection[12]
    groupsSection = infoSection[14]
    languagesSection = infoSection[16]
    categoriesSection = infoSection[18]
    pagesSection = infoSection[20]

    result = {}
    result["code"] = code
    result["altcode"] = altCode
    result["thumbnail"] = thumbnail
    result["title1"] = title1
    result["title2"] = "" if len(title2) > 200 else title2
    result["parodies"] = {key: val for key in intagRecovery(parodiesSection)[::2] for val in intagRecovery(parodiesSection)[1::2]}
    result["characters"] = {key: val for key in intagRecovery(characterSection)[::2] for val in intagRecovery(characterSection)[1::2]}
    result["tags"] = {key: val for key in intagRecovery(tagsSection)[::2] for val in intagRecovery(tagsSection)[1::2]}
    result["artists"] = {key: val for key in intagRecovery(artistSection)[::2] for val in intagRecovery(artistSection)[1::2]}
    result["groups"] = {key: val for key in intagRecovery(groupsSection)[::2] for val in intagRecovery(groupsSection)[1::2]}
    result["languages"] = {key: val for key in intagRecovery(languagesSection)[::2] for val in intagRecovery(languagesSection)[1::2]}
    result["categories"] = {key: val for key in intagRecovery(categoriesSection)[::2] for val in intagRecovery(categoriesSection)[1::2]}
    result["pages"] = intagRecovery(pagesSection)[0]

    return result

def getCodes(tag = "main", freq = ""):
    link = "https://nhentai.net"
    link += "" if tag == "main" else f"/tag/{tag}/{freq}"
    htmlkotor = requests.get(link).text
    gIndex = [m.start() for m in re.finditer('/g/', htmlkotor)]
    return [htmlkotor[i + 3: i + 9] for i in gIndex]

async def stopSeering(client, ctx, sessionName):
    """ this function will stop a session given by its sessionName
    """
    # read json
    channel = discord.utils.get(client.get_all_channels(), name=str(ctx.channel))
    with open(f"servers/{ctx.guild.id}/nhSessions.json", "r+") as f:
        content = f.read()
        nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
        for nhSession in nhSessions:
    #      await ctx.send(nhSession.__dict__)
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

async def seerNH_here(client, ctx, *args):
    """ mengaktifkan nhSession 
    """
    # get channel where seerNH_here invoked
    channel = discord.utils.get(client.get_all_channels(), name=str(ctx.channel))

    sessionNameList = [arg for arg in args if "--sessionName=" in arg]
    print(sessionNameList)
    sys.stdout.flush()
    if len(sessionNameList) is 1:
        sessionName = sessionNameList[0][sessionNameList[0].index("=") + 1 :]
    else:
        sessionName = ""
    print(f"sessionName = {sessionName}")
    sys.stdout.flush()
    try:
        os.mkdir(f"./servers/{ctx.message.guild.id}")
    except:
        pass

    try:
        f = open(f"servers/{ctx.guild.id}/nhSessions.json", "r")
        f.close()
        print("yes", flush=True)
    except:
        with open(f"servers/{ctx.guild.id}/nhSessions.json", "w") as f:
            f.write(json.dumps([]))
            f.close()
        
    with open(f"servers/{ctx.guild.id}/nhSessions.json", "r+") as f:
        content = f.read()
        nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
        for nhSession in nhSessions:
    #     await ctx.send(nhSession.__dict__)
            if nhSession.sessionName is sessionName:
            # ketemu
                await ctx.send(f"nhSession dengan nama {sessionName}, sudah dijalankan")
                break
        else:
            await ctx.send(f"Tidak ada nhSession dengan nama {sessionName}")

    await NHPLoop(channel, args, sessionName)

async def NHPLoop(channel, args, sessionName): # get 5 codes of popular art on main page
    print(args)
    sys.stdout.flush()
    
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
    sys.stdout.flush()
    if len(helpList) is 1:
        await channel.send("melakukan scrap di website kesayangan(nh)\n\nformat cmd: s-seerNH_here --tag=optional --freq=optional --amount=optional --sessionName\nuntuk freq hanya bisa recent, today, week, all-time\nuntuk amount untuk main page 1-5, selain itu 1-25\npastikan tag benar ada! kalau ada spasi ganti dengan \"-\"")
        return

    # input tag
    tagList = [arg for arg in args if "--tag=" in arg]
    print(tagList)
    sys.stdout.flush()
    if len(tagList) is 1:
        tag = tagList[0][tagList[0].index("=") + 1 :]
    else:
        tag = "main"
    print(f"tag = {tag}")
    sys.stdout.flush()
        
    # input freq
    # valid input for freq
    # recent
    # today
    # week
    # all-time
    # freqList, list is in its name but actually its just element that contains --freq=something
    freqList = [arg for arg in args if "--freq=" in arg]
    print(freqList)
    sys.stdout.flush()
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
    sys.stdout.flush()
    
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
    sys.stdout.flush()
    
    if sessionName == "":
        sessionName = f"{channel.name}_{tag}_{freq}_{amount}"
    print(f"session name = {sessionName}")
    sys.stdout.flush()
        



    # check and create session if exist return
    f = open(f"servers/{channel.guild.id}/nhSessions.json", "r+")
    content = f.read()
    nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
    for nhSession in nhSessions:
        if nhSession.sessionName == sessionName:
            await channel.send(f"Session with name '{sessionName}' is exist, trying to continue...")
            info = "```py\nSession with the same name:\n\n"
            info += f"server      = {nhSession.server}\n"
            info += f"channel     = {nhSession.channel}\n"
            info += f"tag         = {nhSession.tag}\n"
            info += f"freq        = {nhSession.freq}\n"
            info += f"amount      = {nhSession.amount}\n"
            info += f"sessionName = {nhSession.sessionName}\n```"
            await channel.send(info)
            await channel.send(f"kode terakhir = {nhSession.lastCodes}")
            f.close()
            break
    else:
        await channel.send("sessionName check: OK")
        newNhSession = NhSession(tag, freq, amount, sessionName, channel.name, channel.guild.name)
        nhSessions.append(newNhSession)
        nhSessions = json.dumps([nhSession.__dict__ for nhSession in nhSessions], indent=4)
        # await channel.send(nhSessions)
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
        info += f"amount      = {amount}\n"
        info += f"sessionName = {sessionName}\n```"
        await channel.send(info)


    nhSessionRunning = True

    while nhSessionRunning:

        await mainScrap(channel, sessionName)

async def kickstart(channel, sessionName):
    nhSessions = json.loads(open(f"./servers/{str(channel.guild.id)}/nhSessions.json", "r").read())
    try:
        for nhSession in nhSessions:
            print(f"{nhSession['sessionName']} == {sessionName}")
            sys.stdout.flush()
            if nhSession['sessionName'] == sessionName:
                subjectNhSession = nhSession
                break
    except:
        pass
    while subjectNhSession["running"]:
        await mainScrap(channel, sessionName)
        nhSessions = json.loads(open(f"./servers/{str(channel.guild.id)}/nhSessions.json", "r").read())
        try:
            for nhSession in nhSessions:
                print(f"{nhSession['sessionName']} == {sessionName}")
                sys.stdout.flush()
                if nhSession['sessionName'] == sessionName:
                    subjectNhSession = nhSession
                    break
        except:
            pass

async def mainScrap(channel, sessionName):
    f = open(f"servers/{channel.guild.id}/nhSessions.json", "r+")
    content = f.read()
    # print(f"content = {content}")
    sys.stdout.flush()
    nhSessions = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))


    try:
        for nhSession in nhSessions:
            print(f"{nhSession.sessionName} == {sessionName}")
            sys.stdout.flush()
            if nhSession.sessionName == sessionName:
                subjectNhSession = nhSession
                break
    except:
        pass

    try:
        codes = getCodes(subjectNhSession.tag, subjectNhSession.freq)
    except Exception as e:
        await channel.send(f"some error has occurred\nError message:{e}")

    for code in codes[:subjectNhSession.amount]:
        if code in subjectNhSession.savedCodes:
            continue
        subjectNhSession.savedCodes.append(code)
        info = scrapFromCode(code)
        embed = discord.Embed()
        thumbnail = info["thumbnail"]
        try:
            embed.set_image(url=thumbnail)
        except Exception as e:
            await channel.send(e)
        try:
            embed.description = f"""
Title: {info['title1']}
Alternative title: {info['title2']}
Code : {info['code']}
Alternative code : {info['altcode']}
Parodies : •{' •'.join(list(info['parodies'].keys()))}
Characters : •{' •'.join(list(info['characters'].keys()))}
Tags: •{' •'.join(list(info['tags'].keys()))}
Artists: •{' •'.join(list(info['artists'].keys()))}
Groups: •{' •'.join(list(info['groups'].keys()))}
Languages: •{' •'.join(list(info['languages'].keys()))}
Categories: •{' •'.join(list(info['categories'].keys()))}
Pages: {info['pages']}

[#{code}](https://nhentai.net/g/{code}) :point_left: 
enjoy ~
"""     
            await channel.send(embed=embed)
        except:
            await channel.send(f"sepertinya kepanjangan, length description = {len(embed.description)}, max is 6000")
            print(embed.description)
    nhSessions = json.dumps([nhSession.__dict__ for nhSession in nhSessions], indent=4)
    # print(nhSessions)
    sys.stdout.flush()
    f.seek(0)
    f.write(nhSessions)
    f.truncate()
    f.close()
    await asyncio.sleep(1200)

async def continyu(client):

    serverDirs = os.listdir("./servers")
    tasks = []
    loop = asyncio.get_event_loop()
    await asyncio.sleep(60)
    for server in serverDirs:
        nhSessions = json.loads(open(f"./servers/{server}/nhSessions.json").read())
        for nhsession in nhSessions:
            if nhsession["running"]:
                channel = discord.utils.get(client.get_all_channels(), name=nhsession["channel"])
                asyncio.ensure_future(kickstart(channel, nhsession["sessionName"]))

    return tasks


