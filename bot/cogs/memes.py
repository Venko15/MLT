import random
from discord import embeds
import praw
from psaw import PushshiftAPI
import datetime as dt
from discord.ext import commands
import discord
import requests
class Meme(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    @commands.command(name='memepls')
    async def memepls(self,ctx,pass_context=True):
        res = requests.get("https://meme-api.herokuapp.com/gimme")
        x = res.json()
        print(x)
        embed = discord.Embed()
        embed.set_image(url = x["url"])
        embed.set_author(name = x["title"])
        await ctx.send(embed = embed)

    
def setup(bot):
    bot.add_cog(Meme(bot))                  