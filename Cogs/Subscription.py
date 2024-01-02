from typing import Optional, Any


import discord
from discord.ext import commands

import requests, json, asyncio
import argparse, inspect
import subprocess, os

import dateutil.parser
from datetime import datetime, timedelta

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
TIME_FORMAT2 = '%Y-%m-%dT%H:%M:%S+00:00Z'
PTIME_FORMAT = '%a, %d %b %Y %H:%M'
CTFTIME_LOGO_URL = "https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png"
SSH_LOGO = "https://w7.pngwing.com/pngs/1008/422/png-transparent-round-greater-than-and-minus-illustratuion-brand-logo-circle-terminal-logo-linux-button-ui-system-apps.png"

ORANGE_WARNING = "#FF7900"
GREEN_OK = "#7CFC00"

class Publisher:
    subscriber = {}
    terminated = False

    def shutdown(self):
        self.terminated = True

    def subscribe(self, identifier, callback):
        self.subscriber[identifier] = callback

    def clean_subscriber(self):
        ...


class Ctftime_Publisher(Publisher):
    def __init__(self, pollrate: float) -> None:
        self.pollrate = pollrate
        asyncio.create_task(self.fetch_loop())

    async def fetch_loop(self):
        await asyncio.sleep(30)

        last_response = {}
        while not self.terminated:
            response = self.fetch()
            if response and last_response != response:
                for name, callback in self.subscriber.items():
                    callback(response)
                last_response = response

            await asyncio.sleep(self.pollrate)

    def fetch(self):
        r = requests.get("https://ctftime.org/api/v1/events/?limit=1", headers = {"User-Agent": 'browser'})
        if r.status_code == 200:
            return json.loads(r.text)[0]
        else:
            return False


class Ctftime_Subscriber:
    def __init__(self, name, channel: discord.TextChannel, publisher: Ctftime_Publisher) -> None:
        self.name = name
        self.channel = channel
        self.publisher = publisher
        self.publisher.subscribe(self.name, self.send)
    
    def send(self, response):
        asyncio.create_task(self.channel.send(embed=self.build_embed(response)))
    
    def build_embed(self, response):
        embed : discord.Embed = discord.Embed(color = discord.Color.from_rgb(215, 0, 10))

        start = datetime.strptime(response['start'], TIME_FORMAT) + timedelta(hours=7)
        fin = datetime.strptime(response['finish'], TIME_FORMAT) + timedelta(hours=7)

        desc =  f"[{response['title']}]({response['url']})\n\n"
        desc += f"Format: {response['format']}\n"
        desc += f"Time: {start.strftime(PTIME_FORMAT)} - {fin.strftime(PTIME_FORMAT)}\n"
        desc += f"Duration: {response['duration']['days']} days {response['duration']['hours']} hours\n"
        desc += f"Weight: {response['weight']}\n"
        desc += f"Restrictions: {response['restrictions']}\n"

        embed.description = desc
        embed.set_author(name="CTFtime", url=response['ctftime_url'], icon_url=CTFTIME_LOGO_URL)
        embed.set_image(url=response['logo'])

        return embed


#single instance
class Endlessh_Pipe:
    "permit endlessh to use port 22 first, `sudo setcap cap_net_bind_service=ep /bin/endlessh`"
    command = "endlessh -p 22 -4 -v"
    terminated = False
    def __init__(self, channel: discord.TextChannel) -> None:
        self.channel = channel
        
        asyncio.create_task(self.loop())
        
    async def loop(self):
        proc = await asyncio.create_subprocess_shell(self.command, stdout=asyncio.subprocess.PIPE)
        print("Load")

        while not self.terminated:
            line = await proc.stdout.readline() #type: ignore
            if line:
                tokens = line.decode('ascii').rstrip().split()
                print(tokens)
                if len(tokens) < 6:
                    continue
                embed = self.build_embed(tokens)
                await self.channel.send(embed=embed) # type: ignore
            else:
                await asyncio.sleep(5)
            
        print("Exit")
        await proc.wait()

    def build_embed(self, tokens):
        if tokens[1] == "ACCEPT":
            color = ORANGE_WARNING
        else:
            color = GREEN_OK
        
        embed : discord.Embed = discord.Embed(color = discord.Color.from_str(color))

        time = dateutil.parser.isoparse(tokens[0]) + timedelta(hours=7)

        desc =  f"{tokens[1]}\n"
        desc += f"Time: {time.strftime(PTIME_FORMAT)}\n\n"
        desc += f"Host: {tokens[2][5:]}\n"
        desc += f"Port: {tokens[3][5:]}\n"
        if tokens[1] == "CLOSE":
            desc += f"Binding time: {tokens[5][5:]}\n"

        embed.description = desc
        embed.set_author(name="Endlessh", icon_url=SSH_LOGO)

        return embed

class Subscription(commands.Cog):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.ctftime_publisher = Ctftime_Publisher(1200)

        self.__get_self_methods()
        self.__create_parser()

    @commands.command()
    async def ctftime(self, ctx: commands.Context):
        self.ctftime_subscriber = Ctftime_Subscriber("subs 1", ctx.channel, self.ctftime_publisher) #type: ignore

    @commands.command()
    async def endlessh(self, ctx: commands.Context):
        self.endlessh_pipe = Endlessh_Pipe(ctx.channel)  #type: ignore
        ...


    # INTERNAL USE
    def __create_parser(self):
        self.parser = parser = argparse.ArgumentParser()
        parser.add_argument("subkoran", type=str, help="pilihan langganan", choices=self.methods)
        parser.add_argument("-d", "--delay", type=int, default=3600, help="delay between request(for request based)")

    def __get_self_methods(self):
        self.methods = mtds = [t[0] for t in inspect.getmembers(self, predicate=inspect.ismethod) if not t[0].startswith('_Koran_')]
        print(mtds)
        # mtds.remove("koran")

