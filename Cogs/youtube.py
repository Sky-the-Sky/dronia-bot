import requests
import random
import io
import asyncio
import discord
import os
from yt_dlp import YoutubeDL
from discord.ext import commands

try:
    PATH = 'Data/YT_cache'
    chck = os.listdir(PATH)
except FileNotFoundError:
    os.mkdir(PATH)
    chck = []

ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    'paths': {"home":PATH},
    'outtmpl': f'%(title)s.%(ext)s',
}

class mus():
    def __init__(self, url, instant_cache=False):
        self.url = url
        self.cached = False
        self.path = None
        if instant_cache:
            self.cache()
    
    def cache(self):
        if self.cached:
            return
        try:
            # check file existence
            with YoutubeDL(ydl_opts) as ydl:
                yt = ydl.sanitize_info(ydl.extract_info(self.url, download=False))
                self.title = yt['title']
            self.path = f'{self.title}.m4a'
            if self.path in chck:
                self.cached = True
                self.path = f"{PATH}/{self.title}.m4a"
                return
        except:
            pass
        #try:
        with YoutubeDL(ydl_opts) as ydl:
            yt = ydl.sanitize_info(ydl.extract_info(self.url, download=True))
        self.path = f"{PATH}/{yt['title']}.m4a"
        chck.append(self.path)
        self.title = yt['title']
        self.cached = True
        #except:
        #    self.cached = False
        #    print('An unexpected error occurred while caching the music.')
        #    print(f'In: {self.url}')
    
    def __expr__(self):
        return self.path if self.cached else None
    
    def __str__(self):
        return self.link


class youtubePlayerManager():
    def __init__(self,guild,bot):
        self.guild = guild
        self.bot = bot
        self.playing = False
        self.queue = []
        self.voice_client = None
        self.repeat = False
        self.shuffle = False
        self.loop = False
    
    async def join_channel(self, channel):
        self.voice_client = await channel.connect()
        return self.voice_client
    
    async def leave_channel(self):
        self.queue = []
        if self.voice_client is None:
            return
        self.stop()
        await self.voice_client.disconnect()
        self.voice_client = None

    async def play(self, ctx, m):
        if self.playing:
            self.queue.append(m)
            return
        if self.voice_client is None:
            return
        self.playing = True
        """def repeat(guild, voice, audio):
            voice.play(audio, after=lambda e: repeat(guild, voice, audio))
        def play_next(guild, voice):
            if len(self.queue) == 0:
                self.playing = False
                self.voice_client.disconnect()
                self.voice_client = None
                return
            m = self.queue.pop(0)
            audio = discord.FFmpegPCMAudio(m.path)
            voice.play(audio, after=lambda e: play_next(guild, voice))"""
        audio = discord.FFmpegPCMAudio(m.path)
        self.current = audio
        if self.repeat:
            self.voice_client.play(audio, after=lambda e: self.after_pr(ctx, self.guild, self.voice_client, audio))
        else:
            self.voice_client.play(audio, after=lambda e: self.after_pn(ctx, self.guild, self.voice_client))


    async def play_repeat(self, ctx, guild, voice, audio):
        await self.ensure_voice(ctx)
        if not self.repeat:
            self.playing = False
            await self.voice_client.disconnect()
            self.voice_client = None
            return
        voice.play(audio, after=lambda e: self.after_pr(ctx, self.guild, self.voice_client, audio))
    async def play_next(self, ctx, guild, voice):
        await self.ensure_voice(ctx)
        if self.repeat:
            await self.play_repeat(ctx, guild, voice, self.current)
            return
        if len(self.queue) == 0:
            self.playing = False
            await self.voice_client.disconnect()
            self.voice_client = None
            return
        m = self.queue.pop(0)
        audio = discord.FFmpegPCMAudio(m.path)
        voice.play(audio, after=lambda e: self.after_pn(ctx, self.guild, self.voice_client))
    
    def after_pr(self, ctx, guild, voice, audio):
        cor = self.play_repeat(ctx, guild, voice, audio)
        f = asyncio.run_coroutine_threadsafe(cor, self.bot.loop)
        try:
            f.result()
        except:
            pass
    def after_pn(self, ctx, guild, voice):
        cor = self.play_next(ctx, guild, voice)
        f = asyncio.run_coroutine_threadsafe(cor, self.bot.loop)
        try:
            f.result()
        except:
            pass

    def stop(self):
        self.voice_client.stop()
        self.playing = False

    def skip_to(self, idx):
        if idx < 0 or idx >= len(self.queue):
            return
        self.queue = self.queue[idx:]
        self.stop()
        self.play(self.queue.pop(0))
    
    def skip(self):
        self.skip_to(1)
    
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("음성 채널에 들어가주세요.", reference=ctx.message, mention_author=False)
                raise commands.CommandError("음성 채널에 들어가주세요.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

class youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        for guild in bot.guilds:
            self.players[guild] = youtubePlayerManager(guild,self.bot)
    
    def get_player(self, guild):
        if guild not in self.players:
            self.players[guild] = youtubePlayerManager(guild,self.bot)
        return self.players[guild]
    
    @commands.command(name='재생',aliases=['브금','play','p','bgm'])
    async def play(self, ctx, url):
        voicechk = ctx.author.voice.channel
        if voicechk is None:
            return
        player = self.get_player(ctx.guild)
        if player.voice_client is None:
            res = await player.join_channel(ctx.author.voice.channel)
        m = mus(url, instant_cache=True)
        await player.play(ctx,m)
    
    @commands.command(name='멈춰')
    async def stop(self, ctx):
        player = self.get_player(ctx.guild)
        player.stop()
    
    @commands.command(name='건너뛰기')
    async def skip_to(self, ctx, idx=1):
        player = self.get_player(ctx.guild)
        player.skip_to(idx)
    
    @commands.command(name='반복')
    async def repeat(self, ctx):
        player = self.get_player(ctx.guild)
        player.repeat = not player.repeat
        if player.repeat:
            await ctx.send('반복 재생을 시작합니다.', reference=ctx.message, mention_author=False)
        else:
            await ctx.send('반복 재생을 종료합니다.', reference=ctx.message, mention_author=False)
    
    @commands.command(name='섞기')
    async def shuffle(self, ctx):
        player = self.get_player(ctx.guild)
        player.shuffle = not player.shuffle
    
    @commands.command(name='전체반복')
    async def loop(self, ctx):
        player = self.get_player(ctx.guild)
        player.loop = not player.loop
    
    @commands.command(name='퇴장')
    async def leave(self, ctx):
        player = self.get_player(ctx.guild)
        await player.leave_channel()

async def setup(bot):
    await bot.add_cog(youtube(bot))
    print('Youtube cog loaded.')