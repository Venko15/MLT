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
ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
               'options': '-vn'}
Youtube_URL = r'((http|https):\/\/|)(www\.|)youtube\.com/playlist'
Spotify_URL = r'((http|https):\/\/|)(open.spotify)'
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)
class NotVoiceChannnel(commands.CommandError):
    pass
class EmptyQueue(commands.CommandError):
    pass
class TempExc(commands.CommandError):
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
            return self._queue[self.pos]

    def add_to_queue(self, *args):
        prev_len = len(self._queue)
      
            
        self._queue.extend(args)
        if not prev_len:
            self.event_listeners["on_not_empty"](self)
    def add_song_names(self, *args):
       
        self.track_names.extend(args)

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
    
    async def disconn(self,error):
        await self.voice_client.disconnect()

    async def search_song(self,query):
        video_output = VideosSearch(query, limit = 1)
        return video_output.result()["result"][0]["link"] if video_output is not None else None

    async def spotify_parse(self,ctx, url):
        playlists = sp.playlist(url)
        spotsong = []
        i=0
        for i in range(10121212121010101):
            try:
                spotsong.append(playlists['tracks']["items"][i]['track']["name"] + " - " + playlists['tracks']["items"][i]['track']["album"]["artists"][0]["name"] )
                i+=1
            except IndexError:
                break
        return list(spotsong)
        
    @commands.command()
    async def pl(self,ctx,*args):
        url = ""
        url = " ".join(args)
        if self.queue.vc is None:
            if ctx.author.voice is None:
                raise NotVoiceChannnel
            self.queue.vc = await ctx.author.voice.channel.connect()
        Track = None

        if re.match(Youtube_URL,url):
            try:
                playlist = Playlist(url)
                songs = [x["link"] for x in playlist.videos]
                songs_names = [x["title"] for x in playlist.videos]
                print(songs_names)
                self.queue.add_song_names(*songs_names)
                self.queue.add_to_queue(*songs)
            except:
                Track = url
            
        elif re.match(Spotify_URL,str(url)):
            List = await self.spotify_parse(ctx,url)
            self.queue.add_song_names(*List)
            for i in List:
                if (song := await self.search_song(i)):
                    self.queue.add_to_queue(song)
            print("ready")
        else:
            Track = await self.search_song(url)
        self.queue.add_to_queue(Track)

    @commands.command()
    async def sk(self,ctx):
        self.queue.vc.stop()
        self.queue.get_next_track(None)
    @commands.command()
    async def mixer(self, ctx):
        self.queue.mix
    @commands.command()
    async def do_loop(self,ctx):
        self.queue.do_loop
    @commands.command(name="q")
    async def queue_com(self, ctx):

        def _check(r, u):
            return (
                r.emoji in SCROLL.keys()
                and u in [m for m in ctx.guild.members if not m.bot]
                and r.message.id == msg.id
            )
        q = ""

        for i in range(self.queue.queuePOS, self.queue.queuePOS+10)[:len(self.queue.track_names)]:
            if i > len(self.queue.track_names)-1:
                pass
            else:
                q += f'{i} - '+ str(self.queue.track_names[i])
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
def set_listeners(queue):
    def not_empty(_queue):
        track = MusicB.download_inf(_queue.get_curr_track)
        audio_src = FFmpegPCMAudio(track,**ffmpeg_opts)
        _queue.vc.play(audio_src, after = _queue.get_next_track)
        
    queue.on_event("on_not_empty", not_empty)
    queue.on_event("on_pos_change", not_empty)
 
def setup(bot):
    bot.add_cog(MusicB(bot))
