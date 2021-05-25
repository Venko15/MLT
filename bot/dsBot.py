from pathlib import Path
import pymongo
import discord
from discord.ext import commands
import asyncio
import datetime
import random

class MLT(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        self.client = pymongo.MongoClient(
            "mongodb+srv://MLT:Venkoto%4015@mlt.kinqt.mongodb.net/MLT?retryWrites=true&w=majority")
        self.db = self.client["MLT"]
        
        super().__init__(command_prefix=self.prefix,
                         case_insensitive=True, intents=discord.Intents.all())

    def setup(self):
        print("Running setup...")

        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")
            print(f" Loaded `{cog}` cog.")

    async def on_ready(self):
        print("U modafuka logged in ")

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("1")(bot, msg)

    def run(self):
        self.setup()
        TOKEN = "ODEyNzIxMDg4NjE0MTA1MTI4.YDE3fw.q_a52f6jEBcX9fpcsvc96MGWoS0"
        super().run(TOKEN, reconnect=True)

    async def on_connect(self):
        print(f" Connected to Discord (latency: {self.latency*1000:,.0f} ms).")

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)
    
    async def is_level_up(self,msg,member):
        if member["xp"] >= member["threshold"]: 
            await msg.channel.send(f'<@{str(msg.author.id)}>  just leveled up. Reached level {int(member["lvl"])+1}')
            return True
        return False

    async def on_message(self, msg):
        col = self.db[str(msg.guild)]
        if not msg.author.bot:
            a = datetime.datetime.today()
            query = {"name": str(msg.author.id)}
            if (member := col.find_one(query)) is None:
                ins = {"name": str(msg.author.id), "lvl": 0,
                       "xp": 0, "lastmsg": a, "threshold" : 10}
                col.insert_one(ins)
            else:
                b = datetime.timedelta(minutes=0)
                if a - member["lastmsg"] > b:
                    member["lastmsg"] = a
                    member["xp"] += 10
                    newval = {"$set": {"xp":  int(member["xp"]), "lastmsg": a}}
                    if await self.is_level_up(msg, member):
                        newval = {"$set": {"lvl": int(member["lvl"]+1),
                       "xp":  int(member["xp"] - member["threshold"]), "lastmsg": a, "threshold" :abs((member["lvl"]-1 + member["lvl"])*15)}}
                    col.update(query,newval) 
            await self.process_commands(msg)
