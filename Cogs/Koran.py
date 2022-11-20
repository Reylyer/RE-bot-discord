from typing import Optional, Any


import discord
from discord.ext import commands

import requests, json, asyncio
import argparse, inspect

from datetime import datetime, timedelta

class Koran(commands.Cog):
    tformat = '%Y-%m-%dT%H:%M:%S+00:00'
    print_tformat = '%a, %d %b %Y %H:%M'

    def __init__(self, client) -> None:
        super().__init__()
        self.client = client

        self.__get_self_methods()
        self.__create_parser()

    # ENTRY
    @commands.command()
    async def koran(self, ctx, *, argument):
        await ctx.send(f"args: {argument}")
        try:
            kwargs = self.parser.parse_args(argument.split())
            await ctx.send(f"kwargs: {json.dumps(kwargs.__dict__, indent=4)}")
            await self.ctftime(ctx, kwargs.__dict__)
        except Exception as e:
            await ctx.send(e)
            
    # SUBKORAN
    async def ctftime(self, ctx, kwargs):
        await ctx.send("Berhasil subs ke ctftime")
        asd_json = ''
        while True:
            print("requesting")
            cjson = request_ctftime()
            if cjson and asd_json != cjson:
                asd_json = cjson
                embed = discord.Embed(color = discord.Color.from_rgb(215, 0, 10))
                print(type(cjson))
                start = datetime.strptime(cjson['start'], self.tformat) + timedelta(hours=7)
                fin = datetime.strptime(cjson['finish'], self.tformat) + timedelta(hours=7)

                embed.set_author(name="CTFtime", url=cjson['ctftime_url'], icon_url="https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png")
                desc =  f"[{cjson['title']}]({cjson['url']})\n\n"
                desc += f"Format: {cjson['format']}\n"
                desc += f"Time: {start.strftime(self.print_tformat)} - {fin.strftime(self.print_tformat)}\n"
                desc += f"Duration: {cjson['duration']['days']} days {cjson['duration']['hours']} hours\n"
                desc += f"Weight: {cjson['weight']}\n"
                desc += f"Restrictions: {cjson['restrictions']}\n"

                embed.description = desc
                embed.set_image(url=cjson['logo'])

                await ctx.send("**New CTF!!!**", embed=embed)

                # except Exception as e:
                #     await ctx.send(e)
            await asyncio.sleep(kwargs['delay'])


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

