from cache_decorator.cache import cache
from discord.activity import Spotify
from discord.player import FFmpegAudio
from youtube_dl import YoutubeDL
import discord
import asyncio
from discord import FFmpegPCMAudio
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from discord.ext import commands
from youtube_dl.postprocessor import ffmpeg
from youtubesearchpython import VideosSearch
import re
from random import shuffle
from youtubesearchpython import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import unittest
ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
               'options': '-vn'}
Youtube_URL = r'((http|https):\/\/|)(www\.|)youtube\.com/playlist'
Spotify_URL = r'\w+:\/\/open.spotify.com\/playlist\/.*'
Spotify_song_url = r'https://open.spotify.com/track/'
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)


class NotVoiceChannnel(commands.CommandError):
    pass


class EmptyQueue(commands.CommandError):
    pass


class TempExc(commands.CommandError):
    pass


class TrackNotFound(commands.CommandError):
    pass


SCROLL = {
    "⬆️": -1,
    "⬇️": 1,

}


class Queue:
    def __init__(self):
        self._queue = []
        self.track_names = []
        self.pos = 0
        self.queuePOS = 0
        self.mode = False
        self.event_listeners = {}
        self.vc = None

    @property
    def is_empty(self):
        return not self._queue

    def curr_poss(self):
        return self.pos

    @property
    def get_curr_track(self):
        if not self._queue:
            raise EmptyQueue

        if self.pos <= len(self._queue)-1:
            print(self._queue[self.pos])
            return self._queue[self.pos]["song_link"]

    def add_to_queue(self, *args):
        prev_len = len(self._queue)

        self._queue.extend(args)
        if not prev_len:
            self.event_listeners["on_not_empty"](self)

    def get_next_track(self, error):
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
                self.clear_q()
        self.event_listeners["on_pos_change"](self)

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

    def on_event(self, event, clb):
        events = ["on_pos_change", "on_not_empty"]
        if event not in events:
            raise TempExc
        self.event_listeners[event] = clb


class MusicB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = Queue()
        set_listeners(self.queue)

    @staticmethod
    def download_inf(url):
        ytdl = YoutubeDL()
        mp3 = ytdl.extract_info(url, download=False)
        track = mp3["formats"][0]["url"]
        print(mp3["title"])
        return track

    async def disconn(self, error):
        await self.voice_client.disconnect()

    async def get_song_name(self, query):
        video_output = VideosSearch(query, limit=1)
        return video_output.result()["result"][0]["title"] if video_output is not None else None

    async def search_song(self, query):
        video_output = VideosSearch(query, limit=1)
        return video_output.result()["result"][0]["link"] if video_output is not None else None

    async def spotify_parse(self, ctx, url):
        playlists = sp.playlist(url)
        spotsong = []
        i = 0
        for i in range(10121212121010101):
            try:
                spotsong.append(playlists['tracks']["items"][i]['track']["name"] + " - " +
                                playlists['tracks']["items"][i]['track']["album"]["artists"][0]["name"])
                i += 1
            except IndexError:
                break
        return list(spotsong)

    async def spotify_song(self, ctx, url):
        song = sp.track(url)
        output = str(song["album"]["artists"][0]["name"]) + \
            " - " + str(song["name"])
        print(output)
        return output

    @commands.command(name="play", aliases=["pl", "p"])
    async def play(self, ctx, *args):
        url = ""
        url = " ".join(args)
        if self.queue.vc is None:
            if ctx.author.voice is None:
                raise NotVoiceChannnel
            self.queue.vc = await ctx.author.voice.channel.connect()
        Track = None

        if re.match(Youtube_URL, url):
            try:
                playlist = Playlist(url)
                songs = [{"song_link": x["link"], "song_title" : x["title"]}
                         for x in playlist.videos]
                self.queue.add_to_queue(*songs)
            except:
                Track = url

        elif re.match(Spotify_URL, str(url)):
            dc = []
            List = await self.spotify_parse(ctx, url)
            for i in List:
                if (song := await self.search_song(i)):
                    dc.append({"song_link": song, "song_title": i})
            self.queue.add_to_queue(*dc)
            return
        elif re.match(Spotify_song_url, str(url)):
            Track = await self.search_song(await self.spotify_song(ctx, url))
            song_name = await self.get_song_name(await self.spotify_song(ctx, url))
            dc = {"song_link": Track, "song_title": song_name}

        else:
            song_name = await self.get_song_name(url)
            Track = await self.search_song(url)
            dc = {"song_link": Track, "song_title": song_name}
        if Track == None:
            raise TrackNotFound

        self.queue.add_to_queue(dc)

    @commands.command(name="skip", aliases=["sk"])
    async def skip(self, ctx):
        self.queue.vc.stop()
        self.queue.get_next_track(None)

    @commands.command()
    async def mix(self, ctx):
        self.queue.mix

    @commands.command()
    async def loop(self, ctx):
        self.queue.do_loop

    @commands.command(name="q", aliases=["queue"])
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
                q += f'{i+1} - ' + str(self.queue._queue[i]["song_title"])
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

    @queue_com.error
    async def queue_exc(self, ctx, exc):
        if isinstance(exc, EmptyQueue):
            msg = await ctx.send("```yaml\nThe queue is empty. Play a song/playlist by typing 1play <URL>/<query> ;D```")

    @play.error
    async def queue_exc(self, ctx, exc):
        if isinstance(exc, TrackNotFound):
            msg = await ctx.send("```yaml\nDidnt find the track :(```")

    @commands.command()
    async def test_m(self, ctx):
        t = Test()
        if not await t.test_music():
            await ctx.send("tests passed")


class Test(unittest.TestCase):
    async def test_music(self):
        m = MusicB(discord.Client())
        self.assertEqual(await m.search_song("azis"), "https://www.youtube.com/watch?v=j2IVk3SG7l8")
        self.assertEqual(await m.spotify_parse(ctx=None, url="https://open.spotify.com/playlist/3gm3JRpm2bQvnBPn7EEn5a?si=c1469ed9eb8547f4"), ["Immortal - 21 Savage"])


def set_listeners(queue):
    def not_empty(_queue):
        track = MusicB.download_inf(_queue.get_curr_track)
        audio_src = FFmpegPCMAudio(track, **ffmpeg_opts)
        _queue.vc.play(audio_src, after=_queue.get_next_track)

    queue.on_event("on_not_empty", not_empty)
    queue.on_event("on_pos_change", not_empty)


def setup(bot):
    bot.add_cog(MusicB(bot))
