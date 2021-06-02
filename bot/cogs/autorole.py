from re import L
from types import coroutine
from discord import client
import pymongo
import discord
import asyncio
from discord.ext import commands
from discord import Client
from discord import channel, guild
from discord.ext.commands.core import command
import os, sys
currentdir = os.path.dirname(os.path.realpath('D:\\veni\python\Project\\bot\\dsBot.py'))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from bot import MLT
mlt = MLT()
class AutoRbot(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.client = pymongo.MongoClient(
            "mongodb+srv://MLT:Venkoto%4015@mlt.kinqt.mongodb.net/MLT?retryWrites=true&w=majority")
        self.db = self.client["MLT"]
        self.rl = self.client["MLTROLES"]
    @commands.command(name = "level")
    async def level(self,ctx):
        col = self.db[str(ctx.guild)]
        query = {"name" : str(ctx.author.id)}
        
        if (member := col.find_one(query)):
            await ctx.send(f'<@{int(member["name"])}>you are level {member["lvl"]}')

    @commands.command(name = "setrole")
    @commands.has_permissions(manage_roles = True) 
    async def setrole(self, ctx, level, *rolename):
        role = " ".join(rolename)
        col = self.rl[str(ctx.guild.id)]
        if (rl := discord.utils.get(ctx.guild.roles, name=role)) is None:
            guild = ctx.guild
            await guild.create_role(name=role)

        query = {"name": role}
        if (member := col.find_one(query)) is None:
            ins = {"name":role ,"lvl" : int(level)}
            col.insert_one(ins)
        else:
            msg = await ctx.send("This role already exists in the database")
            await asyncio.sleep(4)
            await msg.delete()



        
        

    
def setup(bot):
    bot.add_cog(AutoRbot(bot))
