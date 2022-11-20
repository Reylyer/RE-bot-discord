from typing import Optional, Any

import discord
from discord.ext import commands

import requests, json, asyncio
import argparse, shlex
import importlib, sys
import inspect


class CoreCommands(commands.Cog):
    
    def __create_load_parser(self):
        self.load_parser = load_parser = argparse.ArgumentParser(
                                                    description="testing 124")
        load_parser.add_argument('cog', type=str,
                                help='cog name to load')
                            
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.loaded_cogs = {}

        self.__create_load_parser()

    @commands.command() #s-ping
    async def ping(self, ctx):
        await ctx.send(f"pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def load(self, ctx: commands.context.Context, module_name):
        if module_name not in self.loaded_cogs:
            self.loaded_cogs[module_name] = []
            module = importlib.import_module("Cogs." + module_name)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, commands.Cog):
                    await self.bot.add_cog(obj(self.bot))
                    await ctx.send(f"Loaded Cog: {name}")
                    self.loaded_cogs[module_name].append(name)
        else: 
            await ctx.invoke(self.bot.get_command('reload'), module_name) # type: ignore

    @commands.command()
    async def unload(self, ctx: commands.context.Context, module_name):
        if module_name in self.loaded_cogs:
            for cog in self.loaded_cogs[module_name]:
                await self.bot.remove_cog(cog)
                await ctx.send(f"Unloaded Cog: {cog}")
            del self.loaded_cogs[module_name]

    @commands.command()
    async def reload(self, ctx: commands.context.Context, module_name):
        if module_name in self.loaded_cogs:
            await ctx.invoke(self.bot.get_command('unload'), module_name) # type: ignore
            await ctx.invoke(self.bot.get_command('load'), module_name) # type: ignore

    
    @commands.command()
    async def show_loaded(self, ctx):
        await ctx.send("```\n" + "\n".join([
            module_name + ":\n    " + "    \n".join(cogs)
            for module_name, cogs
            in self.loaded_cogs.items()
        ]) + "```")
    

