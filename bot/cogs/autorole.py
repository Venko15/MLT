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
import typing as t
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
        self.roles = []
    @commands.command(name = "level")
    async def level(self,ctx):
        col = self.db[str(ctx.guild.id)]
        query = {"name" : str(ctx.author.id)}
        print("ti si negur")
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
    @commands.command(name = "remrole")
    @commands.has_permissions(manage_roles = True) 
    async def remrole(self,ctx, *rolename):
        role = " ".join(rolename)
        col = self.rl[str(ctx.guild.id)]
        query = {"name": role}
        if (member := col.find_one(query)):
            col.delete_one(query)
        else:
            msg = await ctx.send(f'There isnt a role named {role}')
            await asyncio.sleep(4)
            await msg.delete()
    @commands.command(name = "editrole")
    @commands.has_permissions(manage_roles = True) 
    async def editrole(self, ctx, *rolename):
        def _check(m):
            return m.author == ctx.author
        role = " ".join(rolename)
        col = self.rl[str(ctx.guild.id)]
        query = {"name": role}
        print("Negur1")
        if (member := col.find_one(query)):
            print("Negur2")
            await ctx.send("Waiting for level input")
            
            level = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            newval = {"$set": { "lvl" : int(level.content)}}
            col.update(query, newval)

    @commands.command(name = "display_roles")
    @commands.has_permissions(manage_roles = True) 
    async def display_roles(self, ctx):
        rlcol=self.rl[str(ctx.guild.id)]
        myres = rlcol.find().sort("lvl")
        for r in myres:
            if r not in self.roles:
                self.roles.append(r)
        roles = [x["name"] for x in self.roles]
        levels = [x["lvl"] for x in self.roles]
        output = ""
        for i in range(len(roles)):
            output += f'{roles[i]} - {str(levels[i])}\n'
        await ctx.send(output)
        self.roles.clear()
    @commands.command()
    async def help(self, ctx, intention = None):

        if intention == "general" or intention is None:
            
            embed = discord.Embed(title="This is General Help", colour=discord.Colour(0xa94ab1), description="This is a multifunctional bot")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")
            embed.set_author(name="Yeah thats me >__MLT ze bot__<", icon_url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")

            embed.add_field(name="🎷Music", value="```yaml\nFor help with the memes commmand type - 1help Music```")
            embed.add_field(name="🏋Autorole", value="```yaml\nFor help with the memes commmand type - 1help Autorole```")
            embed.add_field(name="☁️Weather", value="```yaml\nFor help with the memes commmand type - 1help Weather```")
            embed.add_field(name="🤣Memes", value="```yaml\nFor help with the memes commmand type - 1help Memes```")
        elif intention == "Music":
            embed = discord.Embed(title="This is Music Help", colour=discord.Colour(0xa94ab1), description="This is a multifunctional bot")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")
            embed.set_author(name="Yeah thats me >__MLT ze bot__<", icon_url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")

            embed.add_field(name="Play music on demand", value="```yaml\nUse the 1play/1p/1pl to play a song, a playlist or even music from a link(spotify/youtube): 1pl/1play <query>```")
            embed.add_field(name="Skip a song", value="```yaml\nUse 1sk/1skip to skip to the next song : 1sk/1skip```")
            embed.add_field(name="View the queue", value="```yaml\nUse 1queue/1q to view all the songs you have queued up : 1q```")
            embed.add_field(name="Or even loop the queue", value="```yaml\nUse 1loop to enable/disable the loop : 1loop```")
        elif intention == "Autorole":
            embed = discord.Embed(title="This is Autorole Help", colour=discord.Colour(0xa94ab1), description="This is a multifunctional bot")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")
            embed.set_author(name="Yeah thats me >__MLT ze bot__<", icon_url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")

            embed.add_field(name="Set role to a certain level", value="```yaml\nUse the 1setrole to set a role to a certain level : 1setrole <level> <role_name>```")
            embed.add_field(name="Edit role level", value="```yaml\nUse 1sk/1skip to skip to the next song : 1editrole <role_name>```")
            embed.add_field(name="Remove role by name query", value="```yaml\nUse 1remrole to view all the songs you have queued up : 1remrole <level> <role_name>```")
            embed.add_field(name="Display all roles", value="```yaml\nUse 1display_roles to show all roles : 1display_roles ```")
        elif intention == "Weather":
            embed = discord.Embed(title="This is Weather Help", colour=discord.Colour(0xa94ab1), description="This is a multifunctional bot")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")
            embed.set_author(name="Yeah thats me >__MLT ze bot__<", icon_url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")

            embed.add_field(name="Set role to a certain level", value="```yaml\nUse the 1setrole to set a role to a certain level : 1weather <City/Country>```")
            embed.add_field(name="Check the forecast for certain amount of days ahead", value="```yaml\nUse 1forecast : 1forecast <days> <City/Country>```")
        elif intention == "Memes":
            embed = discord.Embed(title="This is Weather Help", colour=discord.Colour(0xa94ab1), description="This is a multifunctional bot")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")
            embed.set_author(name="Yeah thats me >__MLT ze bot__<", icon_url="https://cdn.discordapp.com/attachments/827580959322144768/850770402796109854/unknown.png")

            embed.add_field(name="Set role to a certain level", value="```yaml\nUse the 1setrole to set a role to a certain level : 1weather <City/Country>```")
            embed.add_field(name="Check the forecast for certain amount of days ahead", value="```yaml\nUse 1forecast : 1forecast <days> <City/Country>```")

        await ctx.send(embed=embed)







        
        

    
def setup(bot):
    bot.add_cog(AutoRbot(bot))
