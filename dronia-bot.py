import random
import os
import json
import discord
import asyncio
import time
import datetime
from collections import defaultdict
from discord import app_commands
from discord.ext import commands
from html2image import Html2Image


hti = Html2Image()

html = """<!DOCTYPE html> <html>  <head>     <style>         

  

  @import url('https://fonts.googleapis.com/css2?family=Diphylleia&amp;family=Nanum+Gothic&display=swap');         

  

  body {background-color: #f0f0f0}

  html {height: 100%;}

  

  .container {display: flex; align-items: center; justify-content: center; height: 100%;}

  

  .status-box {text-align: center;

    background-color: rgba(0, 0, 0, 0.5);

    color: #fff;

    background-size: 100% 100%;

    width: 500px;

    max-width: 100%;

    border-radius: 24px;

    box-shadow: 0px 0px 10px 10px rgba(0, 0, 0, 0.5);

    background-position: center;

    display: inline-block;

    padding-left: 4%;

    padding-right: 4%;

    padding-top: 10px;

    padding-bottom: 10px;

    margin-top: 2em;

    margin-bottom: 2em;

  }

  

  .status-box .content {

    font-family: 'Diphylleia', serif;

    color: #fff;

    text-align: center;

    line-height: 2em;

  }

 

  .content span:nth-of-type(1), .content span:nth-of-type(5){

    font-family: 'Diphylleia', serif;

    color: #fae0d4;

    font-style: italic;

    font-size: 1.1em;

    font-weight: normal;

    animation: twinkling1 2s infinite; }

  

  .content span:nth-of-type(3), .content span:nth-of-type(7){

    font-family: 'Diphylleia', serif;

    color: #fff1eb;

    font-style: italic;

    font-size: 1.1em;

    font-weight: normal;

    animation: twinkling2 2s infinite;

  }

  

  .content span:nth-of-type(even){

    color: #ffffff;

    font-family: 'Nanum Gothic', sans-serif;

    font-size: 1em;

    font-weight: 400;

  }

  

  .status-box img {

    max-width: 100%;

    height: auto;

    display: block;

    margin: auto;

    padding-top: 5%;

    padding-bottom: 5%;

  }

  

  @keyframes twinkling1 {

    0% {opacity: 1;} 50% {opacity: 0.7;} 100% {opacity: 1;}

  }

  

  @keyframes twinkling2 {

    0% {opacity: 0.7;} 50% {opacity: 1;} 100% {opacity: 0.7;}

  }

  

  </style> </head> <body>

  <div class="container">

    <div class="status-box">

      <img src="https://i.imgur.com/1ThwEp4.png">

      <div class="content">

        <span>&nbsp;Name:</span><span>&nbsp;&nbsp;$2</span><br>
        
        <span>&nbsp;$3:</span><span>&nbsp;&nbsp;$4</span><br>

        <span>&nbsp;$5:</span><span>&nbsp;&nbsp;$6</span><br>

        <span>&nbsp;$7:</span><span>&nbsp;&nbsp;$8</span>

      </div>

      <img src="https://i.imgur.com/O5ZWSvf.png">

    </div>

  </div>

  </body>  </html>"""
css = """body{}"""

# screenshot an HTML string (css is optional)
hti.screenshot(html_str=html, css_str=css, save_as='page.png')

#client = discord.Client(intents=discord.Intents.all())
loggingChannel = {}
loggingChannelHasChanged = defaultdict(lambda:False,{})
firstRun = True
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
for g in GUILDS:
    #print(g)
    if os.path.exists(f'Data/data_{g}.json'):
        with open(f'Data/data_{g}.json', encoding='utf-8') as j:
            jsonData = json.load(j)
    else:
        continue
    loggingChannel[int(g)] = jsonData["LoggingChannel"]
GUILDS = [discord.Object(id=i) for i in GUILDS]

with open(os.path.join(PATH,'players.txt'),'r') as f:
    PLAYERS = list(f.read().split('\n'))



def roll(min:int,max:int,num:int):
    res = 0
    for i in range(0,num):
        res = res + random.randrange(min, max + 1)
    return res

# 함수
def dice(min: int, max: int, num: int, exp: str,rollcrit:bool=False):
    if not (set(' +-/*0123456789.') > set(exp)):
        return '수식이 정상적이지 않은 것 같습니다.'
    elif (exp != '') and (exp.strip()[0] not in set('+-/*')):
        return '첫 글자가 연산자여야 합니다.'
    expText = exp.replace('*', '\*')
    if num <= 1:
        result = eval('random.randrange(min, max + 1)' + exp)
        rexp = exp.replace('+','-') if '+' in exp else exp.replace('-','+')
        if rollcrit and (eval(f"{result}"+rexp)==max):
            text = f'{min}~{max} 사이의 주사위를 굴려 **{eval(f"{result}"+rexp)}**(이)가 나왔습니다. **대성공입니다!**\n*(대성공(순수 값 {max})은 모든 가중치를 무시하고 무조건 성공으로 처리됩니다.)*'
        elif exp == '':
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
            rexp = exp.replace('+','-') if '+' in exp else exp.replace('-','+')
            if rollcrit and (eval(f"{result}"+rexp)==max):
                textList.append(f'{i+1}번째 주사위: **{eval(f"{result}"+rexp)}** (대성공)')
            elif exp == '':
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
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')



@bot.tree.command(name='주사위', description='주사위를 굴립니다.', guilds=GUILDS)
@app_commands.describe(min='주사위의 최소치입니다.', max='주사위의 최대치입니다.', num='주사위의 개수입니다. 기본값은 1입니다.')
async def rollDice(interaction: discord.Interaction, min: int, max: int, num: int = 1):
    await interaction.response.send_message(dice(min, max, num))

#@bot.tree.command(name='register', description='helps you to create a character.', guilds=GUILDS)
#@app_commands.describe(

class rollButton(discord.ui.View):
    def __init__(self, *,target:discord.User,min:int,max:int,num:int=1,bonus:int=0,harsh:bool=False, timeout=300): #5분 뒤 버튼 슝~
        self.target=target
        self.min=min
        self.max=max
        self.num=num
        self.bonus=bonus
        self.harsh=harsh
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Roll!",style=discord.ButtonStyle.blurple)
    async def roll_button(self,interaction,button:discord.ui.Button):
        user = interaction.user.id
        if self.target.id == user:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)
            await interaction.response.send_message(dice(self.min, self.max, self.num,f"+{self.bonus}" if self.bonus>0 else "" if self.bonus==0 else f"{self.bonus}",True))
        else:
            await interaction.response.send_message("요청의 당사자만 판정 주사위를 굴릴 수 있습니다.",ephemeral=True)
    @discord.ui.button(label="Cancel",style=discord.ButtonStyle.danger)
    async def cancel_button(self,interaction,button):
        user = interaction.user
        if self.target.id == user.id or user.guild_permissions.administrator == True:
            await interaction.response.edit_message(view=None,delete_after=1)
        else:
            await interaction.response.send_message("요청의 당사자 및 관리자만 판정 요청을 취소할 수 있습니다.",ephemeral=True)


async def calcProb(min:int,max:int,bonus:int):
    goal=10-bonus
    amount=max-goal+1
    minimum = int(1/(max-min+1)*100)
    if amount > 0:
        va = int(amount/(max-min+1)*100)
        return (va if va<100 else 100) if va>minimum else minimum
    else:
        return minimum
    

@bot.tree.command(name='querydice', description='The bot inquires the targeting player to roll the dice, one or more.',guilds=GUILDS)
@app_commands.describe(target='굴림 요청의 대상입니다.',min='주사위의 최소치입니다.', max='주사위의 최대치입니다.', num='주사위의 개수입니다. 기본값은 1입니다.', bonus='보너스/패널티입니다. 이 숫자만큼 최종 결과를 증/감합니다.', bonusdesc='보너스가 발생한 사유입니다. 없다면 따로 표시되지 않습니다.',bonus2='2번째 보너스입니다.',bonus2desc='placeholder',bonus3='3번째 보너스입니다.',bonus3desc='placeholder')
async def rollDiceInquiry(interaction:discord.Interaction,target:discord.User,min:int=1,max:int=12,num:int=1,bonus:int=0,bonusdesc:str='',bonus2:int=0,bonus2desc:str='',bonus3:int=0,bonus3desc:str=''): #성공 확률이 20% 이하라면 challenging/hard 태그 부여, embed 색 빨간색으로
    rbonus=bonus+bonus2+bonus3
    harsh = await calcProb(min,max,rbonus) <= 20
    trivial = await calcProb(min,max,rbonus) == 100
    box = discord.Embed(colour=discord.Colour.red() if harsh else (discord.Colour.green() if trivial else discord.Colour.default()),title=("판정 요청!" if not trivial else "무조건 성공!") if not harsh else "도전적인 판정 요청!",description=f'{target.mention}님이 {min}~{max} 사이의 주사위를 굴려 판정합니다.')
    if bonus:
        val=(f"{bonusdesc} +{bonus}" if bonus>0 else f"{bonusdesc} {bonus}")
        if bonus2:
            val=val+"\n"+(f"{bonus2desc} +{bonus2}" if bonus2>0 else f"{bonus2desc} {bonus2}")
            if bonus3:
                val=val+"\n"+(f"{bonus3desc} +{bonus3}" if bonus3>0 else f"{bonus3desc} {bonus3}")
        box.add_field(name="가중치",value=val)
        
    box.add_field(name="판정 성공 확률",value=f"{await calcProb(min,max,rbonus)}%")
    rB = rollButton(target=target,min=min,max=max,num=num,bonus=rbonus,harsh=harsh)
    await interaction.response.send_message(embed=box,view=rB)
    rB.message = await interaction.original_response()
    
    
@bot.command(name='ㅈ',aliases=['주사위'])
async def rollDice2(ctx, min: int, max: int, num: int = 1, exp: str='',rollcrit:bool=False):
    await ctx.send(dice(min, max, num,exp,rollcrit), reference=ctx.message, mention_author=False)
    
class isDigit(Exception):
    def __init__(self, message='상수를 왜 넣어 임마'):
        self.message = message

    def __str__(self):
        return 'ExpWarn: ' + self.message

class exprError(Exception):
    def __init__(self, message='식 좀 제대로 써'):
        self.message = message

    def __str__(self):
        return 'ExprError: ' + self.message
class exprErrorParen(Exception):
    def __init__(self, message='괄호가 비었잖아'):
        self.message = message

    def __str__(self):
        return 'ExprError: ' + self.message

class tooMuchRecurrance(Exception):
    def __init__(self, message='괄호 개수가 왜이래'):
        self.message = message

    def __str__(self):
        return 'RecurError: ' + self.message

async def subRollDiceFunc(recur,die,val,opt,query):
    if len(query) == 0:
        raise exprError
    tv = []
    paren = []
    dnum = 0
    dmax = 0
    dmin = 1 #for default
    skipTO = False #skip til next operator
    calcMin = False
    isParen = False
    parens = 1
    firstHalf = 0
    debug = False
    for i in range(0,len(query)):
        if debug:
            print(f'현재 처리 중: {query[i]}')
        if query[i] in ')':
            parens = parens - 1
            if parens != 0:
                paren.append(query[i])
                continue
            if not isParen:
                raise exprError
            if paren == []:
                raise exprErrorParen
            val.append(await subRollDiceAlt2(recur+1,''.join(paren)))
            isParen = False
            if debug:
                print(f'parentheses 닫힘.')
            continue
        if isParen:
            if query[i] in '(':
                parens = parens + 1
            paren.append(query[i])
            if debug:
                print(f'paren 배열 진입: {query[i]}')
            continue
        if query[i] in '(':
            parens = 1
            if tv != []:
                if not skipTO:
                    val.append(''.join(tv))
                    tv = []
                    opt.append('*')
                else:
                    dmax = eval(''.join(tv))
                    tv = []
                    skipTO=False
                    if calcMin:
                        if dmin>dmax:
                            raise exprError
                        die.append(f"{dnum}d[{dmin}..{dmax}]")
                        calcMin = False
                        firstHalf = 0
                    else:
                        die.append(str(dnum)+"d"+str(dmax))
                    val.append(str(roll(dmin,dmax,dnum)))
                    dmin = 1
                    opt.append('*')
            if query[i-1] in ')':
                opt.append('*')
            paren = []
            isParen = True
            if debug:
                print(f'parentheses 열림.')
            continue
        if query[i] in '[':
            if skipTO:
                if tv != []:
                    raise exprError
                calcMin = True
                firstHalf = 0
                continue
            else:
                raise exprError
        elif query[i] == '.':
            if skipTO and firstHalf < 2 and calcMin:
                firstHalf = firstHalf + 1
                if firstHalf == 1:
                    if tv == []:
                        raise exprError
                    dmin = eval(''.join(tv))
                    tv=[]
                continue
            else:
                raise exprError
        elif query[i] in ']':
            if skipTO and firstHalf == 2 and calcMin and tv != []:
                continue
            else:
                raise exprError
        elif query[i] in '+-/*':
            if query[i-1] in ')':
                pass
            elif skipTO:
                dmax = eval(''.join(tv))
                tv = []
                skipTO=False
                if calcMin:
                    if dmin>dmax:
                        raise exprError
                    die.append(f"{dnum}d[{dmin}..{dmax}]")
                    calcMin = False
                    firstHalf = 0
                else:
                    die.append(str(dnum)+"d"+str(dmax))
                val.append(str(roll(dmin,dmax,dnum)))
                dmin = 1
            else:
                if tv != []:
                    val.append(''.join(tv))
                    tv = []
            opt.append(query[i])
            continue
        if skipTO:
            if query[i].isdigit():
                tv.append(query[i])
            else:
                raise exprError
            continue
        if query[i].isdigit():
            if query[i-1] in ')':
                opt.append('*')
            tv.append(query[i])
            continue
        if query[i] == 'd' or query[i] == 'D':
            dnum = eval(''.join(tv))
            tv = []
            skipTO = True
        else:
            raise exprError
    if isParen:
        raise exprError
    if query[-1] in '+-/*':
        raise exprError
    if tv != []:
        if skipTO:
            dmax = eval(''.join(tv))
            tv = []
            skipTO=False
            if calcMin:
                if dmin>dmax:
                    raise exprError
                die.append(f"{dnum}d[{dmin}..{dmax}]")
                calcMin = False
                firstHalf = 0
            else:
                die.append(str(dnum)+"d"+str(dmax))
            val.append(str(roll(dmin,dmax,dnum)))
        else:
            val.append(''.join(tv))
            tv = []

async def subRollDiceAlt2(recur,query):
    if recur > 6:
        raise tooMuchRecurrance
    if query.isdigit():
        return query
    die = [] #주사위
    val = [] #값
    #tv = [] # temp 값
    opt = [] #연산자
    #viter = 0
    #oiter = 0
    await subRollDiceFunc(recur,die,val,opt,query)
    res = ""
    for i in range(0,len(val)):
        res = res + val[i]
        if i != len(val)-1:
            res = res + opt[i]
    return str(eval(res))

@bot.command(name='ㅈㅅ',aliases=['주사위식','주식','ㅅ','r','ㄱ'])
async def rollDiceAlt2(ctx, *args):
    query = ''.join(args)
    try:
        if query.isdigit():
            raise isDigit
        die = [] #주사위
        val = [] #값
        #tv = [] # temp 값
        opt = [] #연산자
        #viter = 0
        #oiter = 0
        await subRollDiceFunc(0,die,val,opt,query)
        res = ""
        print(die)
        print(val)
        print(opt)
        for i in range(0,len(val)):
            res = res + val[i]
            if i != len(val)-1:
                res = res + opt[i]
        if res == str(eval(res)):
            await ctx.send(f"다음 쿼리를 처리합니다: `{query}`\n결과: `{res}`", reference=ctx.message, mention_author=False)
        else:
            await ctx.send(f"다음 쿼리를 처리합니다: `{query}`\n결과: `{res}={eval(res)}`", reference=ctx.message, mention_author=False)
    except exprError:
        await ctx.send("표현식이 올바르지 않습니다.", reference=ctx.message, mention_author=False)
    except isDigit:
        await ctx.send(f"다음 쿼리는 상수입니다: `{query}`", reference=ctx.message, mention_author=False)
    except tooMuchRecurrance:
        await ctx.send("괄호는 최대 6번 중첩시킬 수 있습니다.", reference=ctx.message, mention_author=False)
    except exprErrorParen:
        await ctx.send("괄호 안에는 하나 이상의 표현식이 존재해야 합니다.", reference=ctx.message, mention_author=False)
    finally:
        if ctx.channel.id == 1077942754254004246:
            await ctx.send("# 잠깐만요!\n여긴 봇 채널이 아닌 것 같아요.\n만약 채널을 착각하셨거나 의도하신 게 아니라면, 원활한 대화를 위해 <#1104426926396944464>로 가서 이 명령어를 써 주세요!",delete_after = 60)
            

@bot.command(name='ㅍ',aliases=['판정','ㅍㅈ'])
async def rollDiceAlt(ctx, min: int=1, max: int=12, num: int = 1, exp: str=''):
    await ctx.send(dice(min, max, num,exp,True), reference=ctx.message, mention_author=False)

@bot.tree.command(name='registerlogchannel', description='명령어를 사용한 채널을 로깅 채널로 지정합니다.', guilds=GUILDS)
@app_commands.describe()
async def registerLogChannel(interaction: discord.Interaction):
    global loggingChannelHasChanged
    gui = interaction.guild_id
    loggingChannelHasChanged[gui] = True
    cha = interaction.channel_id
    if os.path.exists(f'Data/data_{gui}.json'):
        with open(f'Data/data_{gui}.json', encoding='utf-8') as j:
            jsonData = json.load(j)
    else:
        jsonData = {}
    jsonData["Logging"] = True
    jsonData["LoggingChannel"] = cha
    with open(f'Data/data_{gui}.json', 'w', encoding='utf-8') as j:
        json.dump(jsonData, j, ensure_ascii=False)
    await interaction.response.send_message(f"로깅 채널을 <#{cha}>로 설정했습니다.`",ephemeral=True)

@bot.event
async def on_message_delete(message):
    if message.content == None or message.content == "":
        return
    if message.content[0] == '^':
        return
    global loggingChannelHasChanged
    global loggingChannel
    gui = message.guild.id
    if loggingChannelHasChanged[gui]:
        loggingChannelHasChanged[gui] = False
        if os.path.exists(f'Data/data_{gui}.json'):
            with open(f'Data/data_{gui}.json', encoding='utf-8') as j:
                jsonData = json.load(j)
        else:
            jsonData = {}
        if jsonData["Logging"] == None or jsonData["Logging"] == False:
            return
        loggingChannel[gui] = jsonData["LoggingChannel"]
    channel_id = loggingChannel[gui]
    embed=discord.Embed(title="삭제 기록", description=f"작성자: `{message.author.name}`", color=0xAF0000, timestamp=datetime.datetime.now())
    embed.add_field(name="메시지 내용",value=message.content,inline=True)
    embed.add_field(name="채널",value=f"<#{message.channel.id}>",inline=True)
    channel=bot.get_channel(channel_id)
    await channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if after.content == None or after.content == "":
        return
    global loggingChannelHasChanged
    global loggingChannel
    gui = before.guild.id
    if loggingChannelHasChanged[gui]:
        loggingChannelHasChanged[gui] = False
        if os.path.exists(f'Data/data_{gui}.json'):
            with open(f'Data/data_{gui}.json', encoding='utf-8') as j:
                jsonData = json.load(j)
        else:
            jsonData = {}
        if jsonData["Logging"] == None or jsonData["Logging"] == False:
            return
        loggingChannel[gui] = jsonData["LoggingChannel"]
    channel_id = loggingChannel[gui]
    embed=discord.Embed(title="수정 기록", description=f"작성자: `{before.author.name}`", color=0xFFA500, timestamp=datetime.datetime.now())
    embed.add_field(name="채널",value=f"<#{before.channel.id}>",inline=False)
    embed.add_field(name="이전 내용",value=before.content,inline=False)
    embed.add_field(name="바뀐 내용",value=after.content,inline=False)
    channel=bot.get_channel(channel_id)
    await channel.send(embed=embed)
#@bot.command(name='판정')
#async def rollDiceAlt2(ctx, min: int, max: int, num: int = 1, exp: str=''):
#    await ctx.send(dice(min, max, num,exp,True), reference=ctx.message, mention_author=False)

#@bot.command(name='주사위')
#async def rollDice3(ctx, min: int, max: int, num: int = 1, exp: str='',rollcrit:bool=False):
#    await ctx.send(dice(min, max, num,exp,rollcrit), reference=ctx.message, mention_author=False)

@bot.command(name='어',aliases=['ㅇㅇ','d','ㅇ'])
async def howDoThis(ctx,*args):
    what = ' '.join(args)
    await ctx.message.delete()
    if what != '':
        await ctx.send(f'```어떻게 {what}하시겠습니까?```')
    else:
        await ctx.send('```어떻게 하시겠습니까?```')

@bot.command(name='대',aliases=['ㄷ','e','대응'])
async def howDoThis_Alt(ctx):
    await ctx.message.delete()
    await ctx.send('```어떻게 대응하시겠습니까?```')

@bot.command(name='낙석',aliases=['낙','ㄴ'])
async def rayPenbar(ctx,name:str='마스터',reason:str='낙석'):
    await ctx.message.delete()
    fjon = ''
    sjon = ''
    if not (44032<=ord(name[-1])<=55203):
        fjon='은(는)'
    elif (ord(name[-1])-44032)%28==0:
        fjon='는'
    else:
        fjon='은'
    if not (44032<=ord(name[-1])<=55203):
        sjon='(으)로'
    elif (ord(reason[-1])-44032)%28==0:
        sjon='로'
    else:
        sjon='으로'
    if reason == '번개':
        await ctx.send(f'```{name}{fjon} 번개에 직격당하여 그만 사망하고 말았습니다```')
    else:
        await ctx.send(f'```{name}{fjon} {reason}{sjon} 인해 그만 사망하고 말았습니다```')
    if name=='마스터':
        num = roll(1,100,1)
        if num == 82:
            time.sleep(2)
            await ctx.send(f'```...그럼 이제 마스터링은 누가 해주지?```')
            time.sleep(6)
            await ctx.send(f'```아```')




#@bot.command(name='증거인멸',aliases=['증'])
#async def deleteMsg(ctx, sec=0.2):
#    await ctx.message.delete()
asyncio.run(main())
bot.run(TOKEN)