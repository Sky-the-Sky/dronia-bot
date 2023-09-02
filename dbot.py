import random
import os
import discord
import asyncio
from discord import app_commands
from discord.ext import commands

# 봇
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='^', intents=intents)
with open('token.txt', 'r') as f:
    TOKEN = f.read()

async def main():
    dir = os.listdir('Cogs')
    for py in dir:
        if py.endswith('.py'):
            await bot.load_extension(f'Cogs.{py[:-3]}')

# 상수
with open('guilds.txt', 'r') as f:
    GUILDS = list(f.read().split('\n'))
GUILDS = [discord.Object(id=i) for i in GUILDS]

ADVICE = [
'나는 단순히 주사위 굴려주는 봇이 아니야!',
'유명한 TRPG 룰북으로는 D&D, 던전월드, 크툴루의 부름 등이 있어!',
'주사위 운이 너무 안 좋아도 걱정하지 마! GM이 적절히 수습해줄 거니까!',
'지금 하고 있는 룰북, 던전월드지? 던전월드는 2013년에 처음으로 발매됐어!',
'레벨이 잘 안 올라? 전투를 많이 하면 금방 오를 거야!',
'던전월드의 직업은 전사, 마법사, 사제, 도적, 드루이드, 음유시인, 사냥꾼, 성기사로 총 8가지가 있어!',
'레벨업을 하면 원하는 능력치를 1 높일 수 있어! 능력치가 높아지면 가중치도 높아지겠지?',
'소문으로는 언데드 사제나 뱀파이어 음유시인도 있다고 들었는데... 소문이니까 너무 믿지는 마!',
'판정 주사위가 6 이하로 나와도 그게 무조건 캐릭터에게 엄청 나쁜 일이 벌어진다거나 상황이 나쁘게 흘러간다거나 등을 의미하지는 않아. 단지 GM이 모든 것을 결정할 뿐이지~',
'주사위 운이 너무 없어서 진행이 도저히 안 될 정도라고? 음... (소곤소곤) 나를 만든 사람한테 부탁해봐~',
'숨겨진 명령어가 있을지도...?'
]

# 함수
def dice(min: int, max: int, num: int, exp: str):
    if not (set(' +-/*0123456789.') > set(exp)):
        return '수식이 정상적이지 않은 것 같습니다.'
    elif (exp != '') and (exp.strip()[0] not in set('+-/*')):
        return '첫 글자가 연산자여야 합니다.'
    expText = exp.replace('*', '\*')
    if num <= 1:
        result = eval('random.randrange(min, max + 1)' + exp)
        if exp == '':
            text = f'{min}~{max} 사이의 주사위를 굴려 {result}(이)가 나왔습니다.'
        else:
            text = f'{min}~{max} 사이의 주사위에 \'{expText}\' 연산을 하여 {result}(이)가 나왔습니다.'
    else:
        textList = [f'다음은 {min}~{max} 사이의 주사위를 {num}개 굴린 결과입니다.']
        sum = 0
        if exp != '':
            exp = exp.strip()
            textList[0] = f'다음은 {min}~{max} 사이의 주사위를 {num}개 굴리고 \'{expText}\' 연산을 한 결과입니다.'
        for i in range(num):
            result = eval('random.randrange(min, max + 1)' + exp)
            if exp == '':
                textList.append(f'{i+1}번째 주사위: {result}')
            else:
                textList.append(f'{i+1}번째 주사위 ({expText}): {result}')
            sum += result
        textList.append(f'주사위의 합계: {sum}')
        text = '\n'.join(textList)
    return text

@bot.event
async def on_ready():
    for guild in GUILDS:
        await bot.tree.sync(guild=guild)
    game = discord.Game('TRPG')
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.tree.command(name='조언', description='쓸모없는 조언을 해줍니다.', guilds=GUILDS)
async def advice(interaction):
    temp = random.choice(ADVICE)
    await interaction.response.send_message(temp)

@bot.tree.command(name='계산', description='수식을 계산해줍니다.', guilds=GUILDS)
@app_commands.describe(exp='수식을 입력하면 봇이 직접 계산해줍니다. 와!')
async def calculate(interaction: discord.Interaction, exp: str):
    alphabet = set('abcdefghiklmnopqrstuvwxyz')
    if alphabet == alphabet - set(exp.lower()):
        text = eval(exp)
    else:
        text = '이상한 짓 하지 마세요!'
    await interaction.response.send_message(text)

@bot.tree.command(name='인사', description='인사합니다.', guilds=GUILDS)
async def hello(interaction):
    name = interaction.user.name
    print(interaction.user.mention, '\n', interaction.user.id)
    await interaction.response.send_message(f'안녕하세요, {name} 님. 오늘은 무엇을 도와드릴까요?')

@bot.tree.command(name='주사위', description='주사위를 굴립니다.', guilds=GUILDS)
@app_commands.describe(min='주사위의 최소치입니다.', max='주사위의 최대치입니다.', num='주사위의 개수입니다. 기본값은 1입니다.', exp='수식을 입력하면 주사위를 굴려서 나온 결과에 수식을 적용합니다. ex) \'+1\'')
async def rollDice(interaction: discord.Interaction, min: int, max: int, num: int = 1, exp: str = ''):
    await interaction.response.send_message(dice(min, max, num, exp))
    
@bot.command(name='ㅈ')
async def rollDice2(ctx, min: int, max: int, num: int = 1, exp: str = ''):
    await ctx.send(dice(min, max, num, exp), reference=ctx.message, mention_author=False)

@bot.command(name='주사위')
async def rollDice3(ctx, min: int, max: int, num: int = 1, exp: str = ''):
    await ctx.send(dice(min, max, num, exp), reference=ctx.message, mention_author=False)

asyncio.run(main())
bot.run(TOKEN)