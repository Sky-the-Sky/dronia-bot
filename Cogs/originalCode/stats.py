import os
import json
import discord
from discord import app_commands
from discord.ext import commands

# 여기에 데코레이터 입력
class stats(commands.GroupCog, group_name='능력치'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='보기', description='전체 능력치를 봅니다. key에 능력치를 입력하면, key 능력치를 봅니다.')
    async def see(self, interaction: discord.Interaction, key: str = ''):
        try:
            guild_id = str(interaction.guild_id)
            user_id = str(interaction.user.id)
            # utf-8 형식으로 json 파일을 연다. 파일이 없으면 FileNotFoundError 예외 처리를 한다.
            with open(f'Data/{guild_id}-{user_id}-stats.json', encoding='utf-8') as j:
                jsonData = json.load(j)
            # 입력받은 key가 없으면 전체 능력치를 보여준다.
            if key == '':
                description = []
                for key, value in jsonData.items():
                    description.append(f'{key}: {value}')
                embed = discord.Embed(title=interaction.user.name, description='\n'.join(description))
                await interaction.response.send_message(embed=embed)
            # 입력받은 key가 있으면 key 능력치를 보여준다. key 능력치가 없으면 KeyError 예외 처리를 한다.
            else:
                await interaction.response.send_message(f'{interaction.user.name}의 {key}: {jsonData[key]}')                
        except FileNotFoundError:
            await interaction.response.send_message('아직 능력치가 없는 것 같습니다.')
        except KeyError:
            await interaction.response.send_message('그 능력치는 없는 것 같습니다.')

    @app_commands.command(name='다운로드', description='능력치를 json 형식으로 다운로드합니다. json 파일은 메모장으로 열 수 있습니다.')
    async def download(self, interaction: discord.Interaction):
        try:
            guild_id = str(interaction.guild_id)
            user_id = str(interaction.user.id)
            # json 파일을 다운로드한다. 파일이 없으면 FileNotFoundError 예외 처리를 한다. 
            with open(f'Data/{guild_id}-{user_id}-stats.json', encoding='utf-8') as j:
                jsonFile = discord.File(j, filename='stats.json')
                await interaction.response.send_message(file=jsonFile)
        except FileNotFoundError:
            await interaction.response.send_message('아직 능력치가 없는 것 같습니다.')

    @app_commands.command(name='추가', description='key 능력치를 value 값으로 추가합니다. 이미 key 능력치가 있으면, key 능력치를 value 값으로 변경합니다.')
    async def add(self, interaction: discord.Interaction, key: str, value: str):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        # 능력치 json 파일을 찾아 json 데이터를 딕셔너리 변수로 불러온다. 없으면 빈 딕셔너리를 만든다.
        if os.path.exists(f'Data/{guild_id}-{user_id}-stats.json'):
            with open(f'Data/{guild_id}-{user_id}-stats.json', encoding='utf-8') as j:
                jsonData = json.load(j)
        else:
            jsonData = {}
        # key, value 쌍을 저장한 후, 다시 json 파일로 만든다.
        jsonData[key] = value
        with open(f'Data/{guild_id}-{user_id}-stats.json', 'w', encoding='utf-8') as j:
            json.dump(jsonData, j, ensure_ascii=False)

        await interaction.response.send_message(f'{interaction.user.name}의 {key}: {value}')

    @app_commands.command(name='삭제', description='key 능력치를 삭제합니다.')
    async def delete(self, interaction: discord.Interaction, key: str):
        try:
            guild_id = str(interaction.guild_id)
            user_id = str(interaction.user.id)
            # utf-8 형식으로 json 파일을 연다. 파일이 없으면 FileNotFoundError 예외 처리를 한다.
            with open(f'Data/{guild_id}-{user_id}-stats.json', encoding='utf-8') as j:
                jsonData = json.load(j)
            # 입력받은 key가 있으면 key 능력치를 제거한다. key 능력치가 없으면 KeyError 예외 처리를 한다.
            jsonData.pop(key)
            # 수정한 json 데이터를 다시 json 파일로 저장한다.
            with open(f'Data/{guild_id}-{user_id}-stats.json', 'w', encoding='utf-8') as j:
                json.dump(jsonData, j, ensure_ascii=False)
            await interaction.response.send_message(f'{key} 능력치가 정상적으로 삭제되었습니다.')
        except FileNotFoundError:
            await interaction.response.send_message('아직 능력치가 없는 것 같습니다.')
        except KeyError:
            await interaction.response.send_message('그 능력치는 없는 것 같습니다.')
     
async def setup(bot):
    await bot.add_cog(stats(bot))