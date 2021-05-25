from types import coroutine
from discord import client
import pymongo
import dns
import discord
from discord.ext import commands
from discord import Client
client = Client()
class AutoRbot(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    
def setup(bot):
    bot.add_cog(AutoRbot(bot))
