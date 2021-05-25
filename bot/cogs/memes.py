import random
import praw
from psaw import PushshiftAPI
import datetime as dt
from discord.ext import commands
import discord
class Meme(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.rdt=praw.Reddit(client_id="bHTGyhmgt_ZgRg",
                client_secret="KPWaNlTEeeFyyH0Hk8-IyRraWZAUkw",
                username="ImproperlyEducated",
                password="Nesebar12",
                user_agent="MLT"                
                            )
        self.api = PushshiftAPI(self.rdt)

    @commands.command(name='memepls')
    async def memepls(self,ctx,pass_context=True):
                subreddits=["ProgrammerHumor", "dankmemes"]
                start_epoch=int(dt.datetime(2021, 1, 1).timestamp())
                posts=list(self.api.search_submissions(after=start_epoch,
                                        subreddit=random.choice(subreddits),
                                        filter=['url','author', 'title', 'subreddit'],
                                        limit=100))
                all_subs=[]
                for submissions in posts:
                    all_subs.append(submissions)
                sub=random.choice(all_subs)
                if sub.url.startswith("https://youtu.be/") or sub.url.startswith("https://www.youtube.com"):
                    await ctx.channel.send(sub.url)
                    return
                if sub.url.startswith("https://cpavox"):
                    return
                em=discord.Embed()
                if sub.url.startswith("https://v.redd.it"):
                    await self.memepls(ctx)
                else:
                    em.set_image(url=sub.url)
                
                if sub.author ==None:
                    await self.memepls(ctx)
                    
                else:
                    print(sub.author)
                    
                    await ctx.channel.send(embed=em)
def setup(bot):
    bot.add_cog(Meme(bot))                  