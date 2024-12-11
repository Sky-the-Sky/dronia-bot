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

#client = discord.Client(intents=discord.Intents.all())
loggingChannel = {}
loggingChannelHasChanged = defaultdict(lambda:False,{})
firstRun = True
battleChannel = {}
battleStarted = defaultdict(lambda:False,{})
battleAttr = defaultdict(lambda:[],{})
# __file__ = 현재 이 파일의 경로
# os.path.dirname(xxx) = xxx가 속해있는 디렉토리의 경로
PATH = os.path.dirname(__file__)
# 봇
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='^', intents=intents)
with open(os.path.join(PATH, 'token.txt'), 'r') as f:
    TOKEN = f.read()
    # token.txt에 봇의 토큰을 입력해주세요.

class __botNPCManager:
    """
    botNPCManager
    NPC를 관리하는 클래스입니다.
    """
    def __init__(self,gui): #gui = guild id
        self.gui = gui
        self.NPC = {} # (name:str, portrait:str (portrait path))
        if os.path.exists(f'Data/{gui}/NPCslist.json'):
            with open(f'Data/{gui}/NPCslist.json', encoding='utf-8') as j:
                self.NPC = json.load(j)
        else:
            self.NPC = {}
            with open(f'Data/{gui}/NPCslist.json', 'w', encoding='utf-8') as j:
                json.dump(self.NPC, j, ensure_ascii=False)
        print(f"botNPCManager for guild {gui} installed.")
    async def registerNPC(self,id,name:str,portrait:discord.Attachment = None,subtitle:str = None): #사용시 주의, 중복검사 안함
        gui = self.gui
        #if portrait.content_type != 'image/png':
        #    portrait = None
        #    self.NPC[id] = {name:name,portrait:None}
        if portrait is not None:
            await portrait.save(f'Data/{gui}/Illust/{id}.png')
            self.NPC[id] = {"name":name,"portrait":f'Data/{gui}/Illust/{id}.png',"subtitle":subtitle}
        else: self.NPC[id] = {"name":name,"portrait":None,"subtitle":subtitle}
        with open(f'Data/{gui}/NPCslist.json', 'w', encoding='utf-8') as j:
            json.dump(self.NPC, j, ensure_ascii=False)
    def setSubtitle(self,id,subtitle:str):
        gui = self.gui
        self.NPC[id]["subtitle"] = subtitle
        with open(f'Data/{gui}/NPCslist.json', 'w', encoding='utf-8') as j:
            json.dump(self.NPC, j, ensure_ascii=False)
    def deleteSubtitle(self,id):
        gui = self.gui
        self.NPC[id]["subtitle"] = None
        with open(f'Data/{gui}/NPCslist.json', 'w', encoding='utf-8') as j:
            json.dump(self.NPC, j, ensure_ascii=False)
    def deleteNPC(self,id):
        gui = self.gui
        if self.NPC[id]["portrait"] is not None:
            os.remove(self.NPC[id]["portrait"])
        del self.NPC[id]
        with open(f'Data/{gui}/NPCslist.json', 'w', encoding='utf-8') as j:
            json.dump(self.NPC, j, ensure_ascii=False)
botNPCManager = {}


# guilds.txt에 서버 ID를 한 줄씩 적어주세요.
with open(os.path.join(PATH, 'guilds.txt'), 'r') as f:
    GUILDS = list(f.read().split('\n'))
#print(GUILDS)
for g in GUILDS:
    #print(g)
    try:
        os.makedirs(f"Data/{g}/Illust")
        os.makedirs(f"Data/{g}/Users")
    except FileExistsError:
        pass
    botNPCManager[int(g)] = __botNPCManager(int(g))
    if os.path.exists(f'Data/data_{g}.json'):
        with open(f'Data/data_{g}.json', encoding='utf-8') as j:
            jsonData = json.load(j)
    else:
        continue
    loggingChannel[int(g)] = jsonData["LoggingChannel"]
GUILDS = [discord.Object(id=i) for i in GUILDS]



with open(os.path.join(PATH,'players.txt'),'r') as f:
    PLAYERS = list(f.read().split('\n'))

def getLoggingChannel(gui:int):
    global loggingChannelHasChanged
    global loggingChannel
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
    return loggingChannel[gui]

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

def dice_customized(cdice:list, num:int, exp:str, rollcrit:bool=True):
    if not (set(' +-/*0123456789.') > set(exp)):
        return '수식이 정상적이지 않은 것 같습니다.'
    elif (exp != '') and (exp.strip()[0] not in set('+-/*')):
        return '첫 글자가 연산자여야 합니다.'
    expText = exp.replace('*', '\*')
    if num <= 1:
        result = eval('cdice[random.randrange(0,len(cdice))]' + exp)
        rexp = exp.replace('+','-') if '+' in exp else exp.replace('-','+')
        if rollcrit and (eval(f"{result}"+rexp)==12):
            text = f'1~12 사이의 주사위를 굴려 **{eval(f"{result}"+rexp)}**(이)가 나왔습니다. **대성공입니다!**\n*(대성공(순수 값 12)은 모든 가중치를 무시하고 무조건 성공으로 처리됩니다.)*'
        elif exp == '':
            text = f'1~12 사이의 주사위를 굴려 {result}(이)가 나왔습니다.'
        else:
            text = f'1~12 사이의 주사위에 \'{expText}\' 연산을 하여 {result}(이)가 나왔습니다.'
    else:
        textList = [f'다음은 1~12 사이의 주사위를 {num}개 굴린 결과입니다.']
        sum = 0
        if exp != '':
            exp = exp.strip()
            textList[0] = f'다음은 1~12 사이의 주사위를 {num}개 굴리고 \'{expText}\' 연산을 한 결과입니다.'
        for i in range(num):
            result = eval('cdice[random.randrange(0,len(cdice))]' + exp)
            rexp = exp.replace('+','-') if '+' in exp else exp.replace('-','+')
            if rollcrit and (eval(f"{result}"+rexp)==12):
                textList.append(f'{i+1}번째 주사위: **{eval(f"{result}"+rexp)}** (대성공)')
            elif exp == '':
                textList.append(f'{i+1}번째 주사위: {result}')
            else:
                textList.append(f'{i+1}번째 주사위 ({expText}): {result}')
            sum += result
        textList.append(f'주사위의 합계: {sum}')
        text = '\n'.join(textList)
    return text



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


# npc subcommand
npc_group = app_commands.Group(name='npc', description='NPC를 관리합니다.')

@npc_group.command(name='register', description='NPC를 등록합니다. 등록한 NPC는 /say의 대상으로 선택할 수 있습니다.')
@app_commands.describe(id='대상 NPC의 id(구분자)입니다. NPC의 id는 고유해야 합니다.',name='대상 NPC의 이름입니다.',portrait='대상의 초상화입니다. say 사용시 같이 출력됩니다. png로 업로드해야 하며, 정사각형 이미지를 권장합니다.',subtitle='NPC의 별칭입니다. /say 사용 시 이름 위에 표시됩니다.')
@app_commands.checks.has_any_role('GM')
async def registerNPC(interaction:discord.Interaction,id:str,name:str,portrait:discord.Attachment = None,subtitle:str = None):
    if portrait.content_type != 'image/png':
        portrait = None
    gui = interaction.guild_id
    if not id in botNPCManager[gui].NPC:
        await botNPCManager[gui].registerNPC(id,name,portrait,subtitle)
        await interaction.response.send_message('등록되었습니다.',ephemeral=True)
    else:
        await interaction.response.send_message('이미 존재하는 id입니다.',ephemeral=True)



@npc_group.command(name='setsubtitle', description='등록된 NPC의 별칭을 추가하거나 수정합니다.')
@app_commands.describe(id='대상 NPC의 id(구분자)입니다. NPC의 id는 고유함이 보장됩니다.',subtitle='NPC의 별칭입니다. /say 사용 시 이름 위에 표시됩니다.')
@app_commands.checks.has_any_role('GM')
async def npcSetSubtitle(interaction:discord.Interaction,id:str,subtitle:str):
    gui = interaction.guild_id
    if not id in botNPCManager[gui].NPC:
        await interaction.response.send_message('등록되지 않은 id입니다.',ephemeral=True)
    else:
        botNPCManager[gui].setSubtitle(id,subtitle)
        await interaction.response.send_message('수정되었습니다.',ephemeral=True)

@npcSetSubtitle.autocomplete('id')
async def npcSetSubtitle_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    arr = botNPCManager[interaction.guild_id].NPC.keys()
    return [app_commands.Choice(name=id,value=id) for id in arr if current in id]

@npc_group.command(name='delsubtitle', description='등록된 NPC의 별칭을 삭제합니다.')
@app_commands.describe(id='대상 NPC의 id(구분자)입니다. NPC의 id는 고유함이 보장됩니다.')
@app_commands.checks.has_any_role('GM')
async def deleteSubtitle(interaction:discord.Interaction,id:str):
    gui = interaction.guild_id
    if not id in botNPCManager[gui].NPC:
        await interaction.response.send_message('등록되지 않은 id입니다.',ephemeral=True)
    else:
        botNPCManager[gui].deleteSubtitle(id)
        await interaction.response.send_message('삭제되었습니다.',ephemeral=True)

@deleteSubtitle.autocomplete('id')
async def deleteSubtitle_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    arr = botNPCManager[interaction.guild_id].NPC.keys()
    return [app_commands.Choice(name=id,value=id) for id in arr if current in id]

@npc_group.command(name='delete', description='등록된 NPC를 삭제합니다.')
@app_commands.describe(id='대상 NPC의 id(구분자)입니다. NPC의 id는 고유함이 보장됩니다.')
@app_commands.checks.has_any_role('GM')
async def deleteNPC(interaction:discord.Interaction,id:str):
    gui = interaction.guild_id
    if not id in botNPCManager[gui].NPC:
        await interaction.response.send_message('등록되지 않은 id입니다.',ephemeral=True)
    else:
        botNPCManager[gui].deleteNPC(id)
        await interaction.response.send_message('삭제되었습니다.',ephemeral=True)

@deleteNPC.autocomplete('id')
async def deleteNPC_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    arr = botNPCManager[interaction.guild_id].NPC.keys()
    return [app_commands.Choice(name=id,value=id) for id in arr if current in id]

@bot.tree.command(name='say', description='NPC에게 말을 시킵니다.',guilds=GUILDS)
@app_commands.describe(id='대상 NPC의 id입니다.',text='대상의 대사입니다.',spoiler='대상 이름을 ???로 가릴지 지정합니다.')
@app_commands.checks.has_any_role('GM')
async def say(interaction:discord.Interaction,id:str,text:str,spoiler:bool=False): #말하기!
    gui = interaction.guild_id
    if not id in botNPCManager[gui].NPC:
        await interaction.response.send_message('이 id를 가진 NPC가 존재하지 않습니다.',ephemeral=True)
        return
    name = botNPCManager[gui].NPC[id]["name"]
    if spoiler:
        name = "???"
    box = discord.Embed(colour=discord.Colour.default(),title=name,description=text)
    if botNPCManager[gui].NPC[id]["subtitle"] is not None:
        box.set_author(name = botNPCManager[gui].NPC[id]["subtitle"])
        if spoiler:
            box.remove_author()
    if botNPCManager[gui].NPC[id]["portrait"] is not None:
        f = discord.File(f'Data/{gui}/Illust/{id}.png',filename=f"portrait.png")
        box.set_thumbnail(url=f'attachment://portrait.png')
        await interaction.channel.send(file=f,embed=box)
        await interaction.response.send_message('삐빅!',ephemeral=True)
    else:
        await interaction.channel.send(embed=box)
        await interaction.response.send_message('삐빅!',ephemeral=True)

@say.autocomplete('id')
async def say_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    arr = botNPCManager[interaction.guild_id].NPC.keys()
    return [app_commands.Choice(name=id,value=id) for id in arr if current in id]


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
    

entropy_group = app_commands.Group(name='entropy', description='엔트로피를 관리합니다.')

@entropy_group.command(name='config', description='엔트로피 설정을 변경합니다.')
@app_commands.describe(config='변경할 설정입니다.',value='변경할 값입니다.')
async def configEntropy(interaction:discord.Interaction,config:str,value:str):
    gui = interaction.guild_id
    pid = interaction.user.id
    with open(f'Data/{gui}/Users/{pid}/entropy.json', encoding='utf-8') as j:
        jsonData = json.load(j)
    if config == 'maxEntropy':
        jsonData["maxEntropy"] = int(value)
    elif config == 'entropyBiasDice': # for each [entropyBiasValue] increase, 1d[12-entropyBiasMin-1]+[entropyBiasMin-1] is added to ^ㅍ's 1d12 roll
        jsonData["entropyBiasDice"] = int(value)
    elif config == 'entropyBiasValue':
        jsonData["entropyBiasValue"] = int(value)
    elif config == 'entropyBiasMin': # ex) if 10, 1d3+9 is added to ^ㅍ's 1d12 roll, thus [1,2,3,4,5,6,7,8,9,10,11,12,(10,11,12)]
        jsonData["entropyBiasMin"] = int(value)
    with open(f'Data/{gui}/Users/{pid}/entropy.json', 'w', encoding='utf-8') as j:
        json.dump(jsonData, j, ensure_ascii=False)
    await interaction.response.send_message('변경되었습니다.',ephemeral=True)

@configEntropy.autocomplete('config')
async def configEntropy_autocomplete(interaction:discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
    return [app_commands.Choice(name='최대 엔트로피',value='maxEntropy'),app_commands.Choice(name='엔트로피 판정 가중치 사용',value='entropyBiasDice'),app_commands.Choice(name='판정 가중치 당 엔트로피 증분 요구량',value='entropyBiasValue'),app_commands.Choice(name='판정 가중치 최솟값',value='entropyBiasMin')]

@entropy_group.command(name='reset', description='엔트로피를 0으로 초기화합니다.')
async def resetEntropy(interaction:discord.Interaction):
    gui = interaction.guild_id
    pid = interaction.user.id
    try:
        with open(f'Data/{gui}/Users/{pid}/entropy.json', encoding='utf-8') as j:
            jsonData = json.load(j)
    except FileNotFoundError:
        try:
            os.makedirs(f'Data/{gui}/Users/{pid}')
        except FileExistsError:
            pass
        jsonData = {}
        jsonData["maxEntropy"] = 31
        jsonData["entropy"] = 0
        jsonData["entropyBiasDice"] = 0
        jsonData["entropyBiasValue"] = 1
        jsonData["entropyBiasMin"] = 7
    jsonData["entropy"] = 0
    if "entropyBiasDice" in jsonData and jsonData["entropyBiasDice"] == 1:
        jsonData["biasedDice"] = list(range(1,13))
    with open(f'Data/{gui}/Users/{pid}/entropy.json', 'w', encoding='utf-8') as j:
        json.dump(jsonData, j, ensure_ascii=False)
    await interaction.response.send_message('엔트로피가 초기화되었습니다.',ephemeral=True)

@entropy_group.command(name='add', description='엔트로피를 추가합니다.')
@app_commands.describe(value='추가할 엔트로피의 양입니다.')
async def addEntropy(interaction:discord.Interaction,value:int):
    gui = interaction.guild_id
    pid = interaction.user.id
    with open(f'Data/{gui}/Users/{pid}/entropy.json', encoding='utf-8') as j:
        jsonData = json.load(j)
    jsonData["entropy"] = jsonData["entropy"] + value
    if jsonData["entropy"] > jsonData["maxEntropy"]:
        value = value - (jsonData["entropy"] - jsonData["maxEntropy"])
        jsonData["entropy"] = jsonData["maxEntropy"]
    jsonData["lastEditValue"] = value
    if jsonData["entropyBiasDice"] == 1:
        diff = value // jsonData["entropyBiasValue"]
        jsonData["lastEditBias"] = []
        for _ in range(0,diff):
            t = roll(jsonData["entropyBiasMin"],12,1)
            jsonData["biasedDice"].append(t)
            jsonData["lastEditBias"].append(t)
        jsonData["biasedDice"].sort()
    with open(f'Data/{gui}/Users/{pid}/entropy.json', 'w', encoding='utf-8') as j:
        json.dump(jsonData, j, ensure_ascii=False)
    embed = discord.Embed(title='현재 엔트로피',description=f'{jsonData["entropy"]}/{jsonData["maxEntropy"]}', color=discord.Colour.default())
    await interaction.response.send_message(f'**엔트로피 +{value}**',embed=embed)

@entropy_group.command(name='undo', description='최근의 연산을 취소합니다.')
async def undoEntropy(interaction:discord.Interaction):
    gui = interaction.guild_id
    pid = interaction.user.id
    with open(f'Data/{gui}/Users/{pid}/entropy.json', encoding='utf-8') as j:
        jsonData = json.load(j)
    if jsonData["lastEditValue"] == 0:
        await interaction.response.send_message('최근의 연산이 없습니다.',ephemeral=True)
        return
    jsonData["entropy"] = jsonData["entropy"] - jsonData["lastEditValue"]
    jsonData["lastEditValue"] = 0
    if jsonData["entropyBiasDice"] == 1:
        for i in jsonData["lastEditBias"]:
            jsonData["biasedDice"].remove(i)
    with open(f'Data/{gui}/Users/{pid}/entropy.json', 'w', encoding='utf-8') as j:
        json.dump(jsonData, j, ensure_ascii=False)
    embed = discord.Embed(title='현재 엔트로피',description=f'{jsonData["entropy"]}/{jsonData["maxEntropy"]}', color=discord.Colour.default())
    await interaction.response.send_message('최근의 연산을 취소했습니다.',embed=embed)

@entropy_group.command(name='show', description='현재 엔트로피 상태를 보여줍니다.')
async def showEntropy(interaction:discord.Interaction):
    gui = interaction.guild_id
    pid = interaction.user.id
    with open(f'Data/{gui}/Users/{pid}/entropy.json', encoding='utf-8') as j:
        jsonData = json.load(j)
    embed = discord.Embed(title='현재 엔트로피',description=f'{jsonData["entropy"]}/{jsonData["maxEntropy"]}', color=discord.Colour.default())
    if jsonData["entropyBiasDice"] == 1:
        embed.add_field(name='엔트로피 주사위',value=f'{jsonData["biasedDice"]}')
    await interaction.response.send_message(embed=embed)

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

class tooManyRecurrance(Exception):
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
    percent = False
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
        elif query[i] in '%':
            if i == 0 or not query[i-1].isdigit() or skipTO or (i+1 < len(query) and query[i+1] in 'd'):
                raise exprError
            percent = True
            continue
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
                    if not percent:
                        val.append(''.join(tv))
                    else:
                        val.append(str(eval(''.join(tv)+"/100")))
                        percent = False
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
        if query[i] == 'd' or query[i] == 'D' or query[i] == 'ㅇ':
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
            if not percent:
                val.append(''.join(tv))
            else:
                val.append(str(eval(''.join(tv)+"/100")))
                percent = False
            tv = []

async def subRollDiceAlt2(recur,query):
    if recur > 6:
        raise tooManyRecurrance
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
            if int(res) == float(res):
                await ctx.send(f"다음 쿼리를 처리합니다: `{query}`\n결과: `{res}`", reference=ctx.message, mention_author=False)
            else:
                await ctx.send(f"다음 쿼리를 처리합니다: `{query}`\n결과: `{res:.2f}`", reference=ctx.message, mention_author=False)
        else:
            res2 = eval(res)
            if int(res2) == float(res2):
                await ctx.send(f"다음 쿼리를 처리합니다: `{query}`\n결과: `{res}={res2}`", reference=ctx.message, mention_author=False)
            else:
                await ctx.send(f"다음 쿼리를 처리합니다: `{query}`\n결과: `{res}={res2:.2f}`", reference=ctx.message, mention_author=False)
    except exprError:
        await ctx.send("표현식이 올바르지 않습니다.", reference=ctx.message, mention_author=False)
    except isDigit:
        await ctx.send(f"다음 쿼리는 상수입니다: `{query}`", reference=ctx.message, mention_author=False)
    except tooManyRecurrance:
        await ctx.send("괄호는 최대 6번 중첩시킬 수 있습니다.", reference=ctx.message, mention_author=False)
    except exprErrorParen:
        await ctx.send("괄호 안에는 하나 이상의 표현식이 존재해야 합니다.", reference=ctx.message, mention_author=False)
    finally:
        if ctx.channel.id == 1077942754254004246:
            await ctx.send("# 잠깐만요!\n여긴 봇 채널이 아닌 것 같아요.\n만약 채널을 착각하셨거나 의도하신 게 아니라면, 원활한 대화를 위해 <#1104426926396944464>로 가서 이 명령어를 써 주세요!",delete_after = 60)
            

@bot.command(name='ㅍ',aliases=['판정','ㅍㅈ'])
async def rollDiceVariant(ctx, min:str ="1", max:int = 1, num:int = 1, exp:str=''):
    try:
        with open(f'Data/{ctx.guild.id}/Users/{ctx.author.id}/entropy.json', encoding='utf-8') as j:
            jsonData = json.load(j)
    except FileNotFoundError:
        jsonData = {}
    if "entropyBiasDice" in jsonData and jsonData["entropyBiasDice"] == 1 and not min.isdigit():
        if not "biasedDice" in jsonData:
            jsonData["biasedDice"] = list(range(1,13))
            with open(f'Data/{ctx.guild.id}/{Users}/{ctx.author.id}/entropy.json', 'w', encoding='utf-8') as j:
                json.dump(jsonData, j, ensure_ascii=False)
        await ctx.send(dice_customized(jsonData["biasedDice"],max,min), reference=ctx.message, mention_author=False)
    elif "entropyBiasDice" in jsonData and jsonData["entropyBiasDice"] == 1 and min.isdigit():
        if not "biasedDice" in jsonData:
            jsonData["biasedDice"] = list(range(1,13))
            with open(f'Data/{ctx.guild.id}/{Users}/{ctx.author.id}/entropy.json', 'w', encoding='utf-8') as j:
                json.dump(jsonData, j, ensure_ascii=False)
        await ctx.send(dice_customized(jsonData["biasedDice"],int(min),''), reference=ctx.message, mention_author=False)
    elif min.isdigit():
        if max == int(min):
            max = 12
        await ctx.send(dice(int(min),max,num,exp,True), reference=ctx.message, mention_author=False)
    else:
        await ctx.send(dice(1,12,max,min,True), reference=ctx.message, mention_author=False)



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
    await interaction.response.send_message(f"로깅 채널을 <#{cha}>로 설정했습니다.",ephemeral=True)

"""
@bot.tree.command(name='registerbattle', description='명령어를 사용한 채널에서 전투를 시작합니다.', guilds=GUILDS)
@app_commands.describe()
async def registerBattle(interaction: discord.Interaction):
    global battleStarted
    if battleStarted:
        await interaction.response.send_message(f"이미 진행중인 전투가 있습니다.",ephemeral=True)
    gui = interaction.guild_id
    battleStarted[gui] = True
    cha = interaction.channel_id
    if os.path.exists(f'Data/data_{gui}.json'):
        with open(f'Data/data_{gui}.json', encoding='utf-8') as j:
            jsonData = json.load(j)
    else:
        jsonData = {}
    jsonData["InBattle"] = True
    jsonData["BattleChannel"] = cha
    with open(f'Data/data_{gui}.json', 'w', encoding='utf-8') as j:
        json.dump(jsonData, j, ensure_ascii=False)
    await interaction.response.send_message(f"<#{cha}>에서 전투를 시작합니다.\n```현재 턴: 1턴```")

@bot.tree.command(name='registercooldown', description='전투에 사용되는 기술의 쿨다운을 등록합니다.', guilds=GUILDS)
@app_commands.describe()

@bot.tree.command(name='endbattle', description='전투를 끝냅니다.', guilds=GUILDS)
@app_commands.describe()
async def registerBattle(interaction: discord.Interaction):
    global battleStarted
    if not battleStarted:
        await interaction.response.send_message(f"진행중인 전투가 없습니다.",ephemeral=True)
    gui = interaction.guild_id
    battleStarted[gui] = False
    if os.path.exists(f'Data/data_{gui}.json'):
        with open(f'Data/data_{gui}.json', encoding='utf-8') as j:
            jsonData = json.load(j)
    else:
        jsonData = {}
    jsonData["InBattle"] = False
    jsonData["BattleChannel"] = -1
    with open(f'Data/data_{gui}.json', 'w', encoding='utf-8') as j:
        json.dump(jsonData, j, ensure_ascii=False)
    await interaction.response.send_message(f"전투를 종료합니다.")
"""

@bot.event
async def on_message_delete(message):
    if message.content == None or message.content == "":
        return
    if message.content[0] == '^' and (message.content[1] == 'ㅇ' or message.content[1] == 'ㄷ'):
        return
    channel_id = getLoggingChannel(message.guild.id)
    channel=bot.get_channel(channel_id)
    if len(message.content)<=1024:
        embed=discord.Embed(title="삭제 기록", description=f"작성자: `{message.author.name}`", color=0xAF0000, timestamp=datetime.datetime.now())
        embed.add_field(name="메시지 내용",value=message.content,inline=True)
        embed.add_field(name="채널",value=f"<#{message.channel.id}>",inline=True)
        await channel.send(embed=embed)
    else:
        channel.send(f"## 삭제 기록\n### (너무 길어서 엠베드하지 못했습니다...)\n작성자: `{message.author.name}`\n메시지 내용:\n```{message.content}```\n채널:<#{message.channel.id}>")

@bot.event
async def on_message_edit(before, after):
    if after.content == None or after.content == "":
        return
    channel_id = getLoggingChannel(before.guild.id)
    channel=bot.get_channel(channel_id)
    resb = before.content
    resa = after.content
    if len(before.content)>1024:
        resb = before.content[:1024]
    if len(after.content)>1024:
        resa = after.content[:1024]
    embed=discord.Embed(title="수정 기록", description=f"작성자: `{before.author.name}`", color=0xFFA500, timestamp=datetime.datetime.now())
    embed.add_field(name="채널",value=f"<#{before.channel.id}>",inline=False)
    embed.add_field(name="이전 내용",value=resb,inline=False)
    embed.add_field(name="바뀐 내용",value=resa,inline=False)
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
async def howDoThisVariant(ctx):
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
    elif (ord(reason[-1])-44032)%28==0|(ord(reason[-1])-44032)%28==8:
        sjon='로'
    else:
        sjon='으로'
    match reason:
        case '번개'|'낙뢰':
            await ctx.send(f'```{name}{fjon} 번개에 직격당하여 그만 사망하고 말았습니다```')
        case '그냥':
            t = roll(1,6,1)
            match t:
                case 1:
                    await ctx.send(f'```{name}이(가) 세계 밖으로 떨어졌습니다```')
                case 2:
                    await ctx.send(f'```ZAPZAPZAP → {name}```')
                case 3:
                    await ctx.send(f'```d/dx{name}```')
                case 4:
                    await ctx.send(f'```{name} 아웃, {name} 아웃```')
                case 5:
                    await ctx.send(f'```{name}의 마음이 무너졌어...```')
                case 6:
                    await ctx.send(f'```굿바이... {name}')
        case 'paranoia'|'파라노이아':
            await ctx.send(f'```ZAPZAPZAP → {name}```')
        case '/kill':
            await ctx.send(f'```{name}이(가) 세계 밖으로 떨어졌습니다```')
        case '루디':
            await ctx.send(f'```{name}의 마음이 무너졌어...```')
        case '레이펜버':
            await ctx.send(f'```굿바이... {name}```')
        case '고죠'|'고죠사토루'|'스쿠나'|'더위사냥':
            await ctx.send(f'```작별이다, {name}```')
            time.sleep(2)
            await ctx.send(f'```내가 없는 시대에 태어났을 뿐인 범부여```')
        case '신창섭':
            await ctx.send(f'```과징금 크악```')
            time.sleep(1)
            await ctx.send(f'```씨이 빨```')
            time.sleep(1)
            await ctx.send(f'```바로 {name} 정상화```')
            time.sleep(1)
            await ctx.send(f'```OUT!!```')
        case _:
            await ctx.send(f'```{name}{fjon} {reason}{sjon} 인해 그만 사망하고 말았습니다```')
    if name=='마스터' or name=='드로니아' or name=='dronia':
        num = roll(1,100,1)
        if num == 92:
            time.sleep(2)
            await ctx.send(f'```...그럼 이제 마스터링은 누가 해주지?```')
            time.sleep(6)
            await ctx.send(f'```아```')

@bot.command(name='불',aliases=['ㅂ','얼음','f'])
async def fuckOff(ctx,addition=0):
    await ctx.message.delete()
    if ctx.author.guild_permissions.manage_channels == False:
        return
    target = ctx.channel
    role = discord.utils.get(ctx.guild.roles, name="@everyone")
    if target.permissions_for(role).send_messages is True:
        await target.set_permissions(role,send_messages=False)
        if addition:
            t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 1:
                await ctx.send('던전의 불을 끌 시간')
            elif t == 2:
                await ctx.send('던전의')
                time.sleep(0.7)
                await ctx.send('불을')
                time.sleep(1.1)
                await ctx.send('끌 시간')
            else:
                await ctx.send('얼린 대구')
    else:
        await target.set_permissions(role,send_messages=True)
        if addition:
            t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 1 or t == 2:
                await ctx.send('던전의 불을 지필 시간')
            else:
                await ctx.send('대구통구이')

#천안문 이스터에그
#@bot.tree.command(name='베이징올림픽', description='beijing', guilds=GUILDS)
#@app_commands.describe() # 슬래시 커맨드 등록
#async def 베이징올림픽(ctx): # 슬래시 커맨드 이름
#    await ctx.response.send_message("我爱北京天安门.") # 인터렉션 응답

@bot.command(name='던전',aliases=['던'])
async def fuckOffVariant(ctx,addition=1):
    await ctx.message.delete()
    if ctx.author.guild_permissions.manage_channels == False:
        return
    target = ctx.channel
    role = discord.utils.get(ctx.guild.roles, name="@everyone")
    if target.permissions_for(role).send_messages is True:
        await target.set_permissions(role,send_messages=False)
        if addition:
            t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 1:
                await ctx.send('던전의 불을 끌 시간')
            elif t == 2:
                await ctx.send('던전의')
                time.sleep(0.7)
                await ctx.send('불을')
                time.sleep(1.1)
                await ctx.send('끌 시간')
            else:
                await ctx.send('얼린 대구')
    else:
        await target.set_permissions(role,send_messages=True)
        if addition:
            t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 3:
                t = roll(1,3,1)
            if t == 1 or t == 2:
                await ctx.send('던전의 불을 지필 시간')
            else:
                await ctx.send('대구통구이')
#@bot.command(name='증거인멸',aliases=['증'])
#async def deleteMsg(ctx, sec=0.2):
#    await ctx.message.delete()

async def main():
    dir = os.listdir('Cogs')
    for py in dir:
        if py.endswith('.py'):
            await bot.load_extension(f'Cogs.{py[:-3]}')
    
@bot.event
async def on_ready():
    
    bot.tree.add_command(npc_group)
    bot.tree.add_command(entropy_group)
    for guild in GUILDS:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        #debug message - show all commands in the tree
        #print(bot.tree.get_commands())
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

asyncio.run(main())
bot.run(TOKEN)