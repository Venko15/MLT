import discord
from discord.ext import commands
import youtube_dl
from youtube_dl import YoutubeDL
import wavelink
import asyncio
import ffmpeg
from random import shuffle
songs = asyncio.Queue()
play_next_song = asyncio.Event()
Tracks=[]
p=False
Playlist=[]

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.audio_task())

    async def on_event_hook(self,event):
        if isinstance(event,(wavelink.TrackEnd,wavelink.TrackException)):
            play_next_song.set()
            Tracks.pop(0)

    async def audio_task(self):
        await self.bot.wait_until_ready()


        node= await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                              port=80,
                                              rest_uri='http://127.0.0.1:80',
                                              password='gosho',
                                              identifier='TEST',
                                              region='us_central')
        node.set_hook(self.on_event_hook)
        while True:
            play_next_song.clear()
            song,guild_id=await songs.get()
            player = self.bot.wavelink.get_player(guild_id)
            await player.play(song)
            await play_next_song.wait()
    def get_info_id(self):
        pass



    
    def get_info(self,url):
        ydl_opts = {
            'download_archive': 'YOUR_PATH_HERE',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            }
        video_title=[]
        with YoutubeDL(ydl_opts) as ydl:
            info=ydl.extract_info(url,download=False)
            video_title.append(info.get('title',None))
            ids=info.get("id", None)

        print(ids)
        return video_title 

    @commands.command(name='connect')
    async def connect(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No ')
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await player.connect(channel.id)
        
    @commands.command()
    async def play(self, ctx,*,query:str):
        if "https://www.youtube.com/watch" in query:
            query=self.get_info(query)

        player = self.bot.wavelink.get_player(ctx.guild.id)
        curr_track= await self.bot.wavelink.get_tracks(f'ytsearch:{query}')
        if not player.is_connected:
            await ctx.invoke(self.connect)
        Tracks.append(curr_track[0].title)

        queue_it=(curr_track[0], ctx.guild.id)
        await songs.put(queue_it)


    @commands.command()
    async def queue(self,ctx):
        Queue1=""
        for i in range(len(Tracks)):
            Queue1+=Tracks[i]
            Queue1+="\n"
        await ctx.send(f'```{str(Queue1)}```')

    @commands.command()
    async def pause(self, ctx):
        global p
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not p:
           p=True
        else:
            await ctx.send("song already paused")
            return


        await player.set_pause(p)
    @commands.command()
    async def resume(self, ctx):
        global p
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if p:
            p=False
            
        else:
            await ctx.send("song is playing rn")
            return
        await player.set_pause(p)
    @commands.command()
    async def skip(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await player.stop()


    def update_q(self, ls):
        Tracks.clear()
        for x in list(songs._queue):
            Tracks.append(x[0].title)
    @commands.command()
    async def mix(self,ctx):
        shuffle(songs._queue)
        self.update_q(list(songs._queue))

          

