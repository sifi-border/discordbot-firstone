# bot.py
import os
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))

import discord

import solver as solver

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
@bot.event
async def on_message(message):
    if "ほめて" in message.content or "褒めて" in message.content:
        await message.reply("えらいえらい💗")


@bot.command(description="始球式定期")
async def play_ball(ctx):
    img = discord.File("data/shikyusiki.gif")
    await ctx.respond(file=img)

@bot.command(description="挨拶", guild_ids=[GUILD_ID])
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"こんにちは、{name}様")

@bot.command(name="dice_roll", description="運命のダイスロール！", guild_ids=[GUILD_ID])
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    if number_of_dice <= 0 or number_of_sides <= 0:
        await ctx.respond("入力は1以上の整数でお願いしますね")
        return
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.respond(', '.join(dice))

@bot.command(name="solve_wordle", description="WORDLE...? よくわからないけどやってみたいです！")
async def solve_wordle(ctx):
    
    # なんかいい書き方募集
    if 'thread' in str(ctx.channel.type).lower():
        await ctx.respond("スレッドでこのコマンドは使えません...")
        return

    w_solver = solver.woldle_solver()
    command_user = ctx.author

    await ctx.respond("WORDLE を始めます！")

    wordle_thread = await ctx.channel.create_thread(name="わーどる",type=discord.ChannelType.public_thread)
    await wordle_thread.add_user(command_user)

    #TODO embed
    await wordle_thread.send(f">>> 🌟るーる説明🌟\n\
- 文字も位置も一致しているなら`2`\n\
- 単語中にその文字が存在するが位置が一致していないなら`1`\n\
- 単語中にその文字が存在しないなら`0`\n\の5桁の数字を入力してください\n\n\
- このゲームを中断したいときは`!stop`\n - 入力をやり直したい時は`!back`\n - 単語が存在しない時には`!none`\nと入力してくださいね")

    while True:
        cand_word = w_solver.answer()
        if cand_word == None:
            await wordle_thread.send("どうやら私の辞書に答えはないようです...")
            break
        await wordle_thread.send(f"答えは`{cand_word}`ですか？")

        # 入力を待つ
        while True:

            msg = await bot.wait_for('message', check=lambda x: x.author == command_user and x.channel == wordle_thread)
            check_str = msg.content

            if check_str in ["22222", "うん", "はい", "そうだよ", "y", "yes", "Yes", "YES"] :
                await wordle_thread.send("やりました！")
                return

            if check_str == "!stop":
                await wordle_thread.send(f"また遊んでくださいね♪")
                return
            
            if check_str == "!back":
                res = w_solver.back_word_list()
                if res == -1:
                    await wordle_thread.send(f"これ以上は戻れません")
                await wordle_thread.send(f"では一手戻りますね")
                continue

            if check_str == "!none":
                await wordle_thread.send(f"了解しました。では別の単語を...")
                break

            # コマンド受付ここまで
            if not w_solver.validate_checkstr(check_str):
                await wordle_thread.send(f"正しく入力してください😡")
                continue
            
            rest_count = len(w_solver.update_list(cand_word=cand_word, check_str=check_str))
            
            await wordle_thread.send(f"残りの候補数:{rest_count}")
            break
                
            
    return

@bot.command(name="play_wordle", descroption="wordleを出題")
async def play_wordle(ctx):
    # なんかいい書き方募集
    if 'thread' in str(ctx.channel.type).lower():
        await ctx.respond("スレッドでこのコマンドは使えません...")
        return

    w_solver = solver.woldle_solver()
    command_user = ctx.author

    await ctx.respond("WORDLE を始めます！")

    wordle_thread = await ctx.channel.create_thread(name="わーどる",type=discord.ChannelType.public_thread)
    await wordle_thread.add_user(command_user)

    wordle_player = solver.woldle_solver()
    ans = wordle_player.choose_ans()

    challeng_count = 6
    not_found = True

    while challeng_count > 0 and not_found:

        await wordle_thread.send(f"答えを入力してください")

        msg = await bot.wait_for('message', check=lambda x: x.author == command_user and x.channel == wordle_thread)
        msg_str = msg.content

        if msg_str == "!stop":
            await wordle_thread.send(f"また遊んでくださいね♪")
            return

        # コマンド受付ここまで
        if not wordle_player.validate_inputword(msg_str):
            await wordle_thread.send(f"正しく入力してください😡")
            continue

        state_str = wordle_player.check_state(msg_str.upper(), ans)

        await wordle_thread.send(f"{state_str}")
        challeng_count -= 1

        not_found = state_str != "🟩🟩🟩🟩🟩"

    if not_found:
        await wordle_thread.send(f"答えは{ans}でした～")
    else:
        await wordle_thread.send(f"おめでとうございます🎊")

    

bot.run(TOKEN)