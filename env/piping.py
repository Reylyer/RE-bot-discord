from __future__ import annotations
import asyncio, discord, re, unicodedata, datetime, json, os, random, glob, sys, inotify, threading
from discord import channel
from asyncinotify import Inotify, Mask
import tweepy, asyncio
from tweepy.asynchronous import AsyncStream


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





class testStream(AsyncStream):
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, channel, *, max_retries=..., proxy=None):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret, max_retries=max_retries, proxy=proxy)
        self.channel = channel
    async def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            return False
        elif status.in_reply_to_status_id != None:
            return False
        elif status.in_reply_to_screen_name != None:
            return False
        elif status.in_reply_to_user_id != None:
            return False
        else:
            pass

    async def on_connect(self):
        await self.channel.send("connected to stream")
    async def on_disconnect(self):
        await self.channel.send("disconnected from stream")
    async def on_data(self, raw_data):
        try:
            half_cooked_data = raw_data.decode("utf-8")
            cooked_data = json.loads(half_cooked_data)
            # await self.channel.send(cooked_data.keys())
            if len(cooked_data["text"]) > 5000:
                f = open("dump.txt", "w");
                f.write(cooked_data["text"])
                f.close()
                attachment = discord.File("dump.txt")

                await self.channel.send(file=attachment)
            else:
                await self.channel.send(cooked_data["text"])
        except Exception as e:
            await self.channel.send(e)

# asyncio.create_task(stream.filter(track=["python"])) #start the stream
