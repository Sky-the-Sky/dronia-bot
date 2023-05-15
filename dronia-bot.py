import random
import os
import discord
import asyncio
from discord import app_commands
from discord.ext import commands

# __file__ = 현재 이 파일의 경로
# os.path.dirname(xxx) = xxx가 속해있는 디렉토리의 경로
PATH = os.path.dirname(__file__)
# 봇
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='^', intents=intents)
with open(os.path.join(PATH, 'token.txt'), 'r') as f:
    TOKEN = f.read()
    # token.txt에 봇의 토큰을 입력해주세요.

async def main():
    dir = os.listdir('Cogs')
    for py in dir:
        if py.endswith('.py'):
            await bot.load_extension(f'Cogs.{py[:-3]}')

# guilds.txt에 서버 ID를 한 줄씩 적어주세요.
with open(os.path.join(PATH, 'guilds.txt'), 'r') as f:
    GUILDS = list(f.read().split('\n'))
GUILDS = [discord.Object(id=i) for i in GUILDS]

# 함수
def dice(min, max, num):
    if num <= 1:
        result = random.randrange(min, max + 1)
        text = f'{min}~{max} 사이의 주사위를 굴려 {result}(이)가 나왔습니다.'
    else:
        textList = [f'다음은 {min}~{max} 사이의 주사위를 {num}개 굴린 결과입니다.']
        for i in range(1, num+1):
            result = random.randrange(min, max + 1)
            textList.append(f'{i}번째 주사위: {result}')
        text = '\n'.join(textList)
    return text

@bot.event
async def on_ready():
    for guild in GUILDS:
        await bot.tree.sync(guild=guild)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')



@bot.tree.command(name='주사위', description='주사위를 굴립니다.', guilds=GUILDS)
@app_commands.describe(min='주사위의 최소치입니다.', max='주사위의 최대치입니다.', num='주사위의 개수입니다. 기본값은 1입니다.')
async def rollDice(interaction: discord.Interaction, min: int, max: int, num: int = 1):
    await interaction.response.send_message(dice(min, max, num))
    
@bot.command(name='주사위')
async def rollDice2(ctx, min: int, max: int, num: int = 1):
    await ctx.send(dice(min, max, num), reference=ctx.message, mention_author=False)

@commands.command(name='어')
async def howDoThis(self, ctx):
    await ctx.message.delete()
    await ctx.send('```어떻게 하시겠습니까?```')

asyncio.run(main())
bot.run(TOKEN)