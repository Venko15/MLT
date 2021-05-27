from types import coroutine
from discord import client
import pymongo
import discord
from discord.ext import commands
from discord import Client

class AutoRbot(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.client = pymongo.MongoClient(
            "mongodb+srv://MLT:Venkoto%4015@mlt.kinqt.mongodb.net/MLT?retryWrites=true&w=majority")
        self.db = self.client["MLT"]
    @commands.command(name = "level")
    async def level(self,ctx):
        col = self.db[str(ctx.guild)]
        query = {"name" : str(ctx.author.id)}
        
        if (member := col.find_one(query)):
            await ctx.send(f'<@{int(member["name"])}>you are level {member["lvl"]}')


    
def setup(bot):
    bot.add_cog(AutoRbot(bot))
