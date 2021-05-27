
from random import shuffle
import time
import asyncio
import datetime as dt
import re
import typing as t

import discord
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
import wavelink
from discord.ext import commands
from wavelink.events import TrackEnd
from wavelink.meta import WavelinkMixin
from wavelink.player import Track
URL_reg = r"(?i)https:\/\/\S+$"
SCROLL = {
    "⬆️": -1,
    "⬇️": 1,

}


class NoVC(commands.CommandError):
    pass


class AlreadyConnected(commands.CommandError):
    pass


class EmptyQueue(commands.CommandError):
    pass


class Spotify_Handler:
    def __init__(self, url) -> None:
        self.url = url
##################################################


class Queue:
    def __init__(self):
        self._queue = []
        self.pos = 0
        self.queuePOS = 0
        self.mode = False

    @property
    def is_empty(self):
        return not self._queue

    def curr_poss(self):
        return self.pos

    @property
    def get_curr_track(self):
        if not self._queue:
            raise EmptyQueue

        if self.pos <= len(self._queue) - 1:
            print(self._queue[self.pos])
            return self._queue[self.pos]

    def add_to_queue(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise EmptyQueue

        self.pos += 1
        self.queuePOS += 1
        if self.pos < 0:
            return None
        elif self.pos > len(self._queue) - 1:
            if self.mode:
                self.pos = 0
            else:
                return None
        return self._queue[self.pos]

    def progress_queue(self, option):
        if self.queuePOS + 10*option > len(self._queue) - 1 or self.queuePOS + 10*option < 0:
            if self.queuePOS + 10*option < 0:
                self.queuePOS = 0
                return self.queuePOS
            return self.queuePOS

        else:
            self.queuePOS += 10*option
            return self.queuePOS

    @property
    def mix(self):
        firstel = []
        firstel = [i for i in self._queue[:self.pos+1]]
        temp = self.pos + 1
        self._queue = self._queue[temp:]
        shuffle(self._queue)
        firstel.extend(self._queue)
        self._queue = firstel

    def clear_q(self):
        self._queue.clear()
        self.pos = 0

    @property
    def do_loop(self):
        if not self.mode:
            self.mode = True
        else:
            self.mode = False

##############################################################


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnected
        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVC

        await super().connect(channel.id)
        return channel

    async def discon(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def is_empty(self):
        if len(self._queue):
            return False
        else:
            return True

    async def add_t(self, ctx, tracks):
        if not tracks:
            print("q pak")

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add_to_queue(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add_to_queue(tracks[0])
            print(tracks[0].title)
            await ctx.send(f"Added {tracks[0].title} to the queue.")
        else:
            if (track := await self.parse_track(ctx, tracks)) is not None:
                self.queue.add_to_queue(track)
                await ctx.send(f"Added {track.title} to the queue.")
        if not self.is_playing:
            await self.start_playback()

    async def parse_track(self, ctx, tracks):
        return tracks[0]

    async def start_playback(self, offset = 0):
        print(self.queue.get_curr_track)
        await self.play(self.queue.get_curr_track, start = offset)

    async def play_next(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except EmptyQueue:
            pass

    async def queue_com(self, ctx):

        def _check(r, u):
            return (
                r.emoji in SCROLL.keys()
                and u in [m for m in ctx.guild.members if not m.bot]
                and r.message.id == msg.id
            )
        q = ""

        for i in range(self.queue.queuePOS, self.queue.queuePOS+10)[:len(self.queue._queue)]:
            if i > len(self.queue._queue)-1:
                pass
            else:
                q += f'{i} - '+self.queue._queue[i].title
                q += "\n"
        if not self.queue.is_empty:
            msg = await ctx.send(f'```yaml\n{str(q)}```')
            for option in list(SCROLL.keys())[:len(SCROLL)]:
                await msg.add_reaction(option)

            reaction, _ = await self.bot.wait_for("reaction_add", check=_check)
            if not q:
                return
            await msg.delete()
            self.queue.progress_queue(SCROLL[reaction.emoji])
            await self.queue_com(ctx)
        else:
            raise EmptyQueue


#####################################################################################
class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())
        self.ctx = None

    @WavelinkMixin.listener("on_track_stuck")
    @WavelinkMixin.listener("on_track_end")
    @WavelinkMixin.listener("on_track_exception")
    async def on_playerSTOP(self, node, payload):
        await payload.player.play_next()

    @WavelinkMixin.listener("on_track_start")
    async def send_emb(self, node, payload):
        em = discord.Embed()
        th_url = payload.player.queue.get_curr_track.thumb
        em.set_image(url=th_url)
        await self.ctx.send(embed=em)

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        await self.wavelink.initiate_node(host='de17.falix.gg',
                                          port=27105,
                                          rest_uri='http://de17.falix.gg:27105',
                                          password='youshallnotpass',
                                          identifier='TEST',
                                          region='еurope')

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join"])
    async def connect_com(self, ctx, *, channel: discord.VoiceChannel = None):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.guild.change_voice_state(channel=channel, deaf=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).discon()
        if member.bot and after.deaf:
            player = self.get_player(self.ctx)
            offfset = player.position
            await player.start_playback(offset = offfset)


    @commands.command(name="play")
    async def play_com(self, ctx, *,  query: str):
        player = self.get_player(ctx)
        self.ctx = ctx
        if not player.is_connected:
            channel = await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise EmptyQueue

            await player.set_pause(False)
            await ctx.send("Playback resumed.")

        else:
            if not re.match(URL_reg, query):
                await player.add_t(ctx, await self.wavelink.get_tracks(f'ytsearch:{query}'))
            else:
                await player.add_t(ctx, await self.wavelink.get_tracks(query))
        

    @commands.command()
    async def queue(self, ctx):
        player = self.get_player(ctx)
        await player.queue_com(ctx)

    @connect_com.error
    async def connect_exc(self, ctx, exc):
        if isinstance(exc, NoVC):
            msg = await ctx.send("You are not in a voice channel")
        elif isinstance(exc, AlreadyConnected):
            msg = await ctx.send("Bot is already connected")
        await asyncio.sleep(3)
        await msg.delete()

    @play_com.error
    async def connect_exc(self, ctx, exc):
        if isinstance(exc, NoVC):
            msg = await ctx.send("You are not in a voice channel")
        elif isinstance(exc, AlreadyConnected):
            msg = await ctx.send("Bot is already connected")
        await asyncio.sleep(3)
        await msg.delete()

    @queue.error
    async def queue_exc(self, ctx, exc):
        if isinstance(exc, EmptyQueue):
            msg = await ctx.send("```yaml\nThe queue is empty. Play a song/playlist by typing 1play <URL>/<query> ;D```")

    @commands.command()
    async def les_goo(self, ctx):
        player = self.get_player(ctx)
        player.queue.clear_q()
        await self.skip(ctx)
        await self.play_com(ctx, query='https://www.youtube.com/watch?v=Vx2hLrb5w9o')
        while player.is_playing:
            await asyncio.sleep(0.0001)
        await player.discon()

    @commands.command()
    async def skip(self, ctx):
        player = self.get_player(ctx)
        await player.stop()

    @commands.command(name="mix")
    async def mix(self, ctx):
        player = self.get_player(ctx)
        player.queue.mix

    @commands.command(name="loop")
    async def loop(self, ctx):
        player = self.get_player(ctx)
        player.queue.do_loop
    @commands.command()
    async def is_playing(self, ctx):
        player = self.get_player(ctx)
        print(commands.Cog.get_listeners(self))
        if player.is_playing:
            await ctx.send("Im playing rn")

def setup(bot):
    bot.add_cog(Music(bot))
