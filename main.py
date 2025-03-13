import discord
import os
import re
from discord.ext import commands,tasks
import time
from database import insert_users_into_db, insert_server, get_user, update_xp, get_stats, get_level, get_balance
from level import level_up
from roulette import game
from dotenv import load_dotenv
from coinflip import coinflip
from work import work



load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="$", intents=intents)
bets = r"^\d+$"
valid_colors = ["red", "black", "green"]
valid_choices = ["heads", "tails"]
user_voice_times = {}
@bot.event
async def on_guild_join(guild):
    insert_server(guild)

@bot.event
async def on_member_join(member):
    insert_users_into_db(member)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for guild in bot.guilds:
        GUILD = guild.id
        print(f"Bot is connected to {guild.name} (ID: {GUILD})")

        insert_users_into_db(guild.members)
    if not update_xp_loop.is_running():
        update_xp_loop.start()
@bot.event
async def on_voice_state_update(member, before, after):
    user = get_user(member.name)
    user_id, name, balance, level, xp = user

    if before.channel is None and after.channel is not None:
        user_voice_times[name] = time.time()

    elif before.channel is not None and after.channel is None:
        if name in user_voice_times:
            join_time = user_voice_times.pop(name)
            leave_time = time.time()
            duration = leave_time - join_time

            xp_gained = duration/15
            update_xp(name, xp_gained)

@tasks.loop(seconds=5)  # Loop every 5 seconds
async def update_xp_loop():
    for name, join_time in user_voice_times.items():
        user = get_user(name)
        if not user:
            print("User not found")
        if user:
            user_id, name, balance, level, xp = user
            current_time = time.time()
            duration = current_time - join_time
            xp_gained = duration / 15

            update_xp(name, xp_gained)
        if level_up(name):
            member = discord.utils.get(bot.get_all_members(), name=name)
            curr_level = get_level(name)
            if member:
                embed = discord.Embed(
                    title="**LEVEL UP**",
                    description=f"Congratulations {member.mention}, you have leveled up to level **{curr_level}**!",
                )

                channel_id = 1349555789139935253
                channel = bot.get_channel(channel_id)
                await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower().strip()
    username = message.author.name
    auth_id = message.author.id

    # Command handlers dictionary
    command_handlers = {
        "$roulette": handle_roulette,
        "$coinflip": handle_coinflip,
        "$cf": handle_coinflip,
        "$balance": handle_balance,
        "$bal": handle_balance,
        "$work": handle_work,
        "$stats": handle_stats,
        "$help" : handle_help
    }

    # Detect command and execute corresponding function
    for command, handler in command_handlers.items():
        if content.startswith(command):
            await handler(message, username, auth_id, content[len(command):].strip())
            return


def parse_bet_command(content):
    parts = content.split()
    if len(parts) != 2:
        return None, None
    bet_choice, bet_value = parts[0].lower(), parts[1]
    return bet_choice, bet_value if re.fullmatch(bets, bet_value) else None



async def reply_with_result(message, result):
    if isinstance(result, discord.Embed):
        await message.reply(embed=result)
    else:
        await message.reply(result)


async def handle_help(message):
    embed = discord.Embed(
        title="**Help**",
        description="**$work** - gives anywhere from 100 to 700 sancoins\n"
                    "**$roulette** - simulates a game of roulette. Example: $roulette red 100\n"
                    "**$coinflip** or **$cf** - simulates a coin toss. Example: $coinflip heads 100\n"
                    "**$stats** - shows your stats\n"
                    "**$bal** or **$balance** - shows your balance",
        color = discord.Color.blurple()
    )
    await message.reply(embed=embed)

async def handle_roulette(message, username, auth_id, content):
    bet_choice, bet_value = parse_bet_command(content)
    if bet_value == "all":
        bet_value = get_balance(username)[0]
    if not bet_value:
        await message.reply("❌ Invalid command format. Use: `$roulette <color> <amount>`")
        return

    if bet_choice not in valid_colors:
        await message.reply("❌ Invalid color. Choose **red**, **black**, or **green**.")
        return

    result = await game(username, int(bet_value), bet_choice, auth_id)
    await reply_with_result(message, result)


async def handle_coinflip(message, username, auth_id, content):
    bet_choice, bet_value = parse_bet_command(content)
    if bet_value == "all":
        bet_value = get_balance(username)[0]
    if not bet_value:
        await message.reply("❌ Invalid command format. Use: `$coinflip <heads/tails> <amount>`")
        return

    if bet_choice not in valid_choices:
        await message.reply("❌ Invalid choice. Choose **heads** or **tails**.")
        return

    result = await coinflip(username, int(bet_value), bet_choice, auth_id)
    await reply_with_result(message, result)


async def handle_balance(message, username, *_):
    balance = get_balance(username)[0]
    embed = discord.Embed(title="**BALANCE**", description=f"Your balance is **{balance} sancoins** !", colour=discord.Color.blue())
    await message.reply(embed=embed)


async def handle_work(message, username, *_):
    result = await work(username)
    await reply_with_result(message, result)


async def handle_stats(message, username, *_):
    stats = get_stats(username)
    xp_needed = 100 * stats[2]
    embed = discord.Embed(
        title="**STATS**",
        description=(
            f"**Name**: {stats[1]}\n"
            f"**Level**: {stats[2]}\n"
            f"**Balance**: {get_balance(username)[0]} sancoins\n"
            f"**XP**: {stats[4]} / {xp_needed}\n"
            f"**Wins**: {stats[5]}\n"
            f"**Losses**: {stats[6]}\n"
            f"**Winrate**: {stats[7]}%"
        ),
        color=discord.Color.brand_green()
    )
    await message.reply(embed=embed)

bot.run(os.getenv('TOKEN'))

