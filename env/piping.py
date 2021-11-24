from __future__ import annotations
import asyncio, discord, re, unicodedata, datetime, json, os, random, glob, sys, inotify, threading
from discord.colour import Color
from discord import channel
from asyncinotify import Inotify, Mask
import tweepy, asyncio, random
from tweepy.asynchronous import AsyncStream
from tweepy import Stream


async def dumping(ctx):
    with Inotify() as inotify:
        inotify.add_watch('./piped', Mask.CLOSE_WRITE)
        async for event in inotify:
            try:
                msg = json.loads(open("./piped/piped.json", "r").read())
                # await ctx.send("```=================================================================```")
                await ctx.send(msg["body"] + "\n\nby: " + msg["from"])
                await asyncio.sleep(10)
            except Exception as e:
                await ctx.send(e)





class DataStream(AsyncStream, object):
    """
    Twitter data stream
    ===================
    

    """
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, name = None, *, max_retries=..., proxy=None):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret, max_retries=max_retries, proxy=proxy)

        if name == None:
            name = str(random.randint(1000000, 9999999))
        self.name = name
        self.newest_tweet = None
        self.subscriber = {}


    async def on_connect(self):
        print("connected to stream")
    async def on_disconnect(self):
        print("disconnected from stream")

    @property
    def newest_tweet(self):
        return self._newest_tweet

    @newest_tweet.setter
    def newest_tweet(self, tweet):
        self._newest_tweet = tweet
        try:
            print(tweet['text'])
            for callback in self.subscriber.values():
                print("new tweet!")
                callback(self._newest_tweet)
        except Exception as e:
            print(e)
    
    def subscribe(self, name, callback):
        print('SUScribed')
        self.subscriber[name] = callback

    async def on_data(self, raw_data):
        try:
            data = json.loads(raw_data.decode("utf-8"))
            if data["in_reply_to_screen_name"] == None:
                print(self.subscriber)
                # print(data)
                self.newest_tweet = data
        except Exception as e:
            pass


class FilterStream(object):
    def __init__(self, name, stream: DataStream, channel, mentionids = [], filter_has = [], filter_word = [], filter_exclude_has = [], filter_exclude_word = []):

        self.name = name
        self.channel = channel
        self.stream = stream
        self.mentionids = mentionids
        self.filter_has = filter_has
        self.filter_word = filter_word
        self.filter_exclude_has = filter_exclude_has
        self.filter_exclude_word = filter_exclude_word

        self.stream.subscribe(self.name, self.process_tweet)

        print("ok")
        asyncio.create_task(self.channel.send(
f"""successfully creating filter stream
```cmd
info:
name                = {self.name} 
stream              = {self.stream.name} 
channel             = {str(self.channel)}
mentions            = {self.mentionids}
filter_has          = {self.filter_has}
filter_word         = {self.filter_word}
filter_exclude_has  = {self.filter_exclude_has}
filter_exclude_word = {self.filter_exclude_word}

stop using s-stop_filter_stream {self.name}
```
"""
        ))

    def process_tweet(self, tweet):
        print("triggered")
        link = f"\n\n[Intip bounty joki](https://twitter.com/i/web/status/{tweet['id_str']})"
        text = tweet["extended_tweet"]["full_text"] if "extended_tweet" in tweet else tweet["text"]
        embed = discord.Embed(color = discord.Color.from_rgb(29, 161, 242))
        
        # filter has
        # asyncio.create_task(self.channel.send(f"triggered, filter_has check: {bool(self.filter_has)}"))
        if self.filter_has:
            changed = False
            for word in self.filter_has:
                if word in text:
                    text = "".join([sliced + "**" + word + "**" for sliced in text.split(word)])[:-6 - len(word)]
                    changed = True

            if not changed:
                return
        # filter word
        # asyncio.create_task(self.channel.send(f"filter_word check: {bool(self.filter_word)}"))
        if self.filter_word:
            text = text.split(' ')
            changed = False
            for word in self.filter_word:
                if word in text:
                    word = "*" + word + "*"
                    changed = True
            
            if not changed:
                return
        
            text = ' '.join(text)
        # filter exclude has
        # asyncio.create_task(self.channel.send(f"filter_exclude_has check: {bool(self.filter_exclude_has)}"))
        if self.filter_exclude_has:
            for word in self.filter_exclude_has:
                if word in text:
                    return
        # filter exclude word
        # asyncio.create_task(self.channel.send(f"filter_exclude_word check: {bool(self.filter_exclude_word)}"))
        if self.filter_exclude_word:
            text = text.split(' ')
            for word in self.filter_exclude_word:
                if word in text:
                    return

        embed.set_author(name=tweet['user']['name'], url=f"https://twitter.com/{tweet['user']['screen_name']}", icon_url=tweet['user']['profile_image_url_https'])
        embed.description = text + link
        if 'media' in tweet['entities']:
            try:
                embed.set_thumbnail(url=tweet['entities']['media'])
            except Exception as e:
                asyncio.create_task(self.channel.send(f"error while setting thumbnail\nerror message : {e}"))
        asyncio.create_task(self.channel.send(" ".join(['<@&'+ id + '>' for id in self.mentionids]), embed = embed))

            # await self.channel.send(e)

# asyncio.create_taskstream.filter(track=["python"])) #start the stream



# f = open("data_raw.json", "w");
# f.write(json.dumps(tweet, indent=4))
# f.close()
# attachment = discord.File("data_raw.json")
# asyncio.create_task(self.channel.send(file = attachment))