from typing import Optional, Any


import discord
from discord.ext import commands

import requests, json, asyncio
import argparse, inspect

from datetime import datetime, timedelta

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
PTIME_FORMAT = '%a, %d %b %Y %H:%M'
CTFTIME_LOGO_URL = "https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png"


class Publisher:
    subscriber = {}
    terminated = False
    pollrate = 3600

    def shutdown(self):
        self.terminated = True

    def subscribe(self, identifier, callback):
        self.subscriber[identifier] = callback

    def clean_subscriber(self):
        ...


class Ctftime_Publisher(Publisher):
    def __init__(self, pollrate: float) -> None:
        self.pollrate = pollrate

    async def fetch_loop(self):
        last_response = {}
        while not self.terminated:
            response = self.fetch()
            if response and last_response != response:
                for name, callback in self.subscriber:
                    callback(response)

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

class Endlessh:
    channel_id = ""



class Subscription(commands.Cog):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.ctftime_publisher = Ctftime_Publisher(3600)

        self.__get_self_methods()
        self.__create_parser()

    @commands.command()
    async def ctftime(self, ctx: commands.Context):
        self.ctftime_subscriber = Ctftime_Subscriber("subs 1", ctx.channel, self.ctftime_publisher) #type: ignore
        ...


    def whatsapp(self, ctx, **kwargs):
        pass

    def nhentai(self, ctx, **kwargs):
        pass

    # INTERNAL USE
    def __create_parser(self):
        self.parser = parser = argparse.ArgumentParser()
        parser.add_argument("subkoran", type=str, help="pilihan langganan", choices=self.methods)
        parser.add_argument("-d", "--delay", type=int, default=3600, help="delay between request(for request based)")

    def __get_self_methods(self):
        self.methods = mtds = [t[0] for t in inspect.getmembers(self, predicate=inspect.ismethod) if not t[0].startswith('_Koran_')]
        print(mtds)
        # mtds.remove("koran")


def request_ctftime() -> Any:
    r = requests.get("https://ctftime.org/api/v1/events/?limit=1", headers = {"User-Agent": 'browser palsu'})
    if r.status_code == 200:
        return json.loads(r.text)[0]
    else:
        return False

