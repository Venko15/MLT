import discord
from discord.ext import commands
from music import Music
from memes import Meme

class Bot(commands.Bot):
    def __init__(self, command_prefix, self_bot):
        commands.Bot.__init__(self, command_prefix=command_prefix, self_bot=self_bot)
       
        self.add_cog(Music(self))
        self.add_cog(Meme(self))
    
    async def on_ready(self):
        print("Bot logged in")
bot=Bot(command_prefix="1", self_bot=False)    
bot.run(TOKEN)
