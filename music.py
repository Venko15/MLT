import discord
from discord.ext import commands
import wavelink
import asyncio
import ffmpeg
from random import shuffle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
songs = asyncio.Queue()
play_next_song = asyncio.Event()
Tracks = []
p = False

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.audio_task())

    async def on_event_hook(self, event):
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            play_next_song.set()
            Tracks.pop(0)

    async def audio_task(self):
        await self.bot.wait_until_ready()

        node = await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                                     port=80,
                                                     rest_uri='http://127.0.0.1:80',
                                                     password='gosho',
                                                     identifier='TEST',
                                                     region='us_central')
        node.set_hook(self.on_event_hook)

        while True:
            play_next_song.clear()
            song, guild_id = await songs.get()
            player = self.bot.wavelink.get_player(guild_id)
            await player.play(song)
            await play_next_song.wait()

    @commands.command(name='connect')
    async def connect(self, ctx, *, channel: discord.VoiceChannel = None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No ')
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await player.connect(channel.id)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):

        if "https://www.youtube.com/playlist" in query:
            curr_track = await self.bot.wavelink.get_tracks(query)
            if isinstance(curr_track, wavelink.TrackPlaylist):
                for track in curr_track.tracks:
                    await self.play(ctx, query=str(track))
            return
        elif "https://www.youtube.com/watch" in query or 'https://open.spotify.com' in query:
            curr_track = await self.bot.wavelink.get_tracks(query)
        else:
            curr_track = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect)
        Tracks.append(curr_track[0].title)
        queue_it = (curr_track[0], ctx.guild.id)
        await songs.put(queue_it)

    @commands.command()
    async def queue(self, ctx):
        Queue1 = ""
        for i in range(len(Tracks)):
            Queue1 += Tracks[i]
            Queue1 += "\n"
        await ctx.send(f'```{str(Queue1)}```')

    @commands.command()
    async def pause(self, ctx):
        global p
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not p:
            p = True
        else:
            await ctx.send("song already paused")
            return

        await player.set_pause(p)

    @commands.command()
    async def resume(self, ctx):
        global p
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if p:
            p = False

        else:
            await ctx.send("song is playing rn")
            return
        await player.set_pause(p)

    @commands.command()
    async def skip(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await self.update_q(list(songs._queue))
        await player.stop()

    async def update_q(self, ls):
        Tracks.clear()
        for x in list(songs._queue):
            Tracks.append(x[0].title)

    @commands.command()
    async def mix(self, ctx):
        shuffle(songs._queue)
        await self.update_q(list(songs._queue))
