import requests
import random
import io
import discord
from discord.ext import commands

def urlToImage(url):
    bytes = requests.get(url)
    image = io.BytesIO(bytes.content)
    return discord.File(image, filename='image.jpg')

class hiddenCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playing = False

    @commands.command(name='패배자')
    async def taunt(self, ctx):
        await ctx.send(file=discord.File('cancel.webp'))
    
    @commands.command(name='언성을')
    async def ichigo(self, ctx):
        await ctx.send(file=discord.File('aijen.jpg'))

    @commands.command(name='선생님')
    async def RTFM(self, ctx):
        await ctx.send(file=discord.File('RTFM.png'))

    @commands.command(name='지도')
    async def map(self, ctx, type=''):
        await ctx.message.delete()
        if type == '동양':
            await ctx.send(file=discord.File('map 2.png'))
        elif type == '신대륙':
            await ctx.send(file=discord.File('map 3.png'))
        elif type == '남대륙':
            await ctx.send(file=discord.File('map 4.png'))
        else:
            await ctx.send(file=discord.File('map 1.png'))

            
    @commands.command(name='재생',aliases=['브금','play','p','bgm'])
    async def play(self,ctx,mus=''):
        author = ctx.author
        if ctx.voice_client is not None:
            voice = ctx.voice_client
        elif author.voice.channel is not None:
            voiceid = author.voice.channel
            voice = await voiceid.connect()
        else:
            return
        def repeat(guild, voice, audio):
            voice.play(audio, after=lambda e: repeat(guild, voice, audio))
        if mus == '백진혼':
            audio = discord.FFmpegPCMAudio('BGM/frost-theme.opus')
        if audio == None:
            self.playing = False
            ctx.send('해당하는 곡이 존재하지 않습니다.', reference=ctx.message, mention_author=False)
        else:
            self.playing = True
            voice.play(audio, after=lambda e: repeat(ctx.guild, voice, audio))

    @commands.command(name='mte')
    async def MTE(self, ctx):
        if self.playing:
            await ctx.send('BGM이 재생되는 중입니다.', reference=ctx.message, mention_author=False)
            return
        author = ctx.author
        MTE = discord.FFmpegPCMAudio('MTE World.opus')
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            ctx.voice_client.play(MTE)
        elif author.voice.channel is not None:
            await ctx.send('𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝒕𝒉𝒆 𝑴𝑻𝑬 𝑾𝒐𝒓𝒍𝒅')
            voiceChannel = author.voice.channel
            voiceClient = await voiceChannel.connect()
            voiceClient.play(MTE)

    @commands.command(name='번개')
    async def lightning(self, ctx):
        await ctx.message.delete()
        await ctx.send('```번개```')

    @commands.command(name='엄')
    async def umjunsik(self, ctx):
        if self.playing:
            await ctx.send('BGM이 재생되는 중입니다.', reference=ctx.message, mention_author=False)
            return
        author = ctx.author
        um = discord.FFmpegPCMAudio('um.opus')
        await ctx.message.delete()
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            ctx.voice_client.play(um)
        elif author.voice.channel is not None:
            voiceChannel = author.voice.channel
            voiceClient = await voiceChannel.connect()
            voiceClient.play(um)
        await ctx.send('엄')
        
    @commands.command(name='그런데')
    async def however(self, ctx, who=''):
        if self.playing:
            await ctx.send('BGM이 재생되는 중입니다.', reference=ctx.message, mention_author=False)
            return
        author = ctx.author
        dic = {
            '체인소맨': ('Kickback.opus', '그런데 그때 체인소맨이 나타났다'),
            '닌자': ('naruto.opus', '그런데 그때 닌자가 나타났다'),
            '죠타로': ('Jojo.opus', '그런데 그때 죠타로가 나타났다'),
            '죠르노': ('giorno.opus', '그런데 그때 죠르노가 나타났다'),
            '호시노': ('mephisto.opus', '그런데 그때...'),
            '유희': ('yugioh.opus', '속공 마법 발동! 버서커 소울!'),
            '샌즈': ('megalovania.opus', '그런데 그때 샌즈가 나타났다\n끔찍한 시간을 보내고 싶어?')
        }
        if who == '':
            opus_file, person = random.choice(list(dic.values()))
        else:
            opus_file, person = dic[who]
        
        music = discord.FFmpegPCMAudio(opus_file)
        sending = f'```{person}```'

        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            ctx.voice_client.play(music)
        elif author.voice.channel is not None:
            voiceChannel = author.voice.channel
            voiceClient = await voiceChannel.connect()
            voiceClient.play(music)
        await ctx.send(sending)

    @commands.command(name='나가', aliases=['ㄴㄱ'])
    async def getOut(self, ctx):
        self.playing = False
        voiceClient = ctx.voice_client
        if voiceClient.is_connected():
            await voiceClient.disconnect()

async def setup(bot):
    await bot.add_cog(hiddenCommand(bot))