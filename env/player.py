from __future__ import annotations
import asyncio, discord, youtube_dl, threading, re, unicodedata, youtubesearchpython, os
from posixpath import pardir

playerList = []

try:
  os.mkdir('servers')
except:
  pass

async def bind(client, ctx, arg):
    if ctx.message.author.voice is not None:
        newPlayer = Player(client, ctx.author.voice.channel, ctx.channel, 80)
        newPlayer.start()
        playerList.append(newPlayer)

async def play(client, ctx, arg):
    for player in playerList:
        if player.server_id == ctx.message.guild.id:
            pass
    else:
        if ctx.message.author.voice is not None:
            newPlayer = Player(client, ctx.author)
            playerList.append(newPlayer)
            await newPlayer.launch()
        else:
            await ctx.send("Ku harus kemana sayang...")

async def latency():

    pass

# <===================== experimental ===========================>
"""
jika pertama kali panggil play, buat object player lalu panggil bind() ke voice_channel
handle exception:
  tidak di voice_channel

sekarang queue di atur oleh class

songQueue berisi Song Object


"""

class Player(discord.VoiceClient, threading.Thread):
    # self.serverIndex now deprecated we use the search object now
    def __init__(self, client: discord.Client, channel: discord.VoiceChannel, logChannel: discord.TextChannel, timerLimit: int = 60):
        discord.VoiceClient.__init__(self, client = client, channel = channel)
        self.pointerPlayer = 0
        self.songQueue = [] # list of Song Objects
        self.logChannel = logChannel
        self.timerLimit = timerLimit
        self.server_id = logChannel.guild.id
        threading.Thread.__init__(self, name=str(self.server_id))
        try:
            os.mkdir(f"./servers/{self.server_id}")
            os.mkdir(f"./servers/{self.server_id}/musics")
        except:
            pass
        
    async def launch(self):
        await self.connect(self.channel)
        while self.is_connected():
            # loop player
            self.play()
            await asyncio.sleep(1)

    def run(self):
        while self.is_connected():
            loop = asyncio.get_event_loop()
            asyncio.set_event_loop(loop)
            while self.pointerPlayer < len(self.songQueue):
                loop.run_until_complete(self.playSong(self.songQueue[self.pointerPlayer]))
                while self.is_playing:
                    loop.run_until_complete(self.sleep())
                self.pointerPlayer += 1

    async def playSong(self, fileName):
        self.play(discord.FFmpegAudio(f'servers/{self.server_id}/musics/{fileName}.mp3'))
    
    async def sleep():
        await asyncio.sleep(1)

        
    def startQueue(self):
        while self.pointerPlayer != len(self.songQueue):
            self.play

    async def addToQueue(self, arg: str):
        # getting link and metaInfo part
        try:
            metaInfo = youtubesearchpython.VideosSearch(arg, 1)[0] if ".com" not in arg else youtubesearchpython.Video.getInfo(arg)
            link = metaInfo["link"]
        except Exception:
            print(Exception)
        # Download Part
        fileName = self.slugify(metaInfo["title"])
        downloadThread = self.DownloadThread("downloadThread", link, self.server_id, fileName)
        try:
            downloadThread.start()
            timer = 0
            while not hasattr(downloadThread, "meta") and timer < self.timerLimit:
                if timer % 10 == 0:
                    await self.logChannel.send(f"{timer} has passed since started downloading...")
                timer += 1
                await asyncio.sleep(1)
            if not hasattr(downloadThread, "meta"):
                await self.logChannel.send("Time limit reached, Terminating thread...")
                return
        except Exception:
            await self.logChannel.send(f"Error has occurred: {Exception}")
            await self.logChannel.send(f"{metaInfo['title']} not added to queue")
            return
        # saving part
        newSong = self.Song(metaInfo, fileName)
        self.songQueue.append(newSong)
        
    def removeQueue(self):
        pass

    class Song:
        def __init__(self, metaInfo: object, fileName: str):
            self.fileName = fileName
            self.link = metaInfo["link"]
            self.thumbnailUrl = metaInfo["thumbnail"][0]["url"]
            self.viewCount = metaInfo["viewCount"]
            self.title = metaInfo["title"]
            self.channel = metaInfo["channel"]["name"]  

    class DownloadThread(threading.Thread):
        def __init__(self, name: str, link: str, serverid: str, songName: str):
            threading.Thread.__init__(self)
            self.name = name
            self.link = link
            self.serverid = serverid
            self.songName = songName
        
        def run(self):
            print(f"starting thread {self.name}")
            try:
              self.downloadmp3()
            except :
              raise Exception()
            print(f"exiting thread {self.name}")

        def downloadmp3(self, songName: str):
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl':f'./servers/{self.server_id}/musics/{songName}.mp3',
                'external-downloader': 'aria2c',
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(self.link)
                ydl.download([self.link])
                self.meta =  meta
    def slugify(self, value, allow_unicode=False):
        """
        Me taken from https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')


def getThreadCount():
  return threading.active_count(), threading.current_thread()