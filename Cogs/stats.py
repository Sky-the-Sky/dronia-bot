with open('guilds.txt', 'r') as f:
    # guilds.txt의 내용을 읽어서 '\n' 대신 ', '으로 바꿔치기
    GUILDS_ID = f.read().replace('\n', ', ')

with open('Cogs/originalCode/stats.py', 'r', encoding='utf-8') as py:
    DECORATOR_INPUT = '# 여기에 데코레이터 입력'
    DECORATOR = f'@app_commands.guilds({GUILDS_ID})'
    code = py.read().replace(DECORATOR_INPUT, DECORATOR)

exec(code)