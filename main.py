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

        # Fetch and insert all members into the database
        insert_users_into_db(guild.members)
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
    # Go through all users in the voice channel and update XP
    for name, join_time in user_voice_times.items():
        user = get_user(name)  # Function to fetch user by ID
        if user:
            user_id, name, balance, level, xp = user
            current_time = time.time()
            duration = current_time - join_time
            xp_gained = duration / 15  # XP gained based on time

            # Update XP every 5 seconds
            update_xp(name, xp_gained)
        if level_up(name):
            member = discord.utils.get(bot.get_all_members(), name=name)
            curr_level = get_level(name)
            if member:
                # Create the embed
                embed = discord.Embed(
                    title="**LEVEL UP**",
                    description=f"Congratulations {member.mention}, you have leveled up to level **{curr_level}**!",
                )

                channel_id = 14234
                channel = bot.get_channel(channel_id)
                await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$roulette '):
        auth_id = message.author.id
        content = message.content[len("$roulette "):].strip()
        parts = content.split()
        if len(parts) == 2:
            bet_color = parts[0].lower()
            bet_value = parts[1]
            if re.fullmatch(bets, bet_value):
                bet_amount = int(bet_value)
                if bet_color in valid_colors:
                    username = message.author.name

                    result = await game(username, bet_amount, bet_color,auth_id)

                    if isinstance(result, discord.Embed):
                        await message.reply(embed=result)
                    else:
                        await message.reply(result)
                else:
                    await message.reply('❌ Invalid color. Please choose from **red**, **black** or **green**.')
            else:
                await message.reply('❌ Invalid bet amount. Please enter a valid number.')
        else:
             await message.reply('❌ Invalid command format. Use: $roulette **color** **amount**')
    if message.content.startswith('$coinflip ') or message.content.startswith('$cf '):
        auth_id = message.author.id
        content = message.content[len("$coinflip "):].strip() if message.content.startswith('$coinflip ') else message.content[len("$cf "):].strip()
        parts = content.split()
        if len(parts) == 2:
            bet = parts[0].lower()
            bet_value = parts[1]
            if re.fullmatch(bets, bet_value):
                bet_amount = int(bet_value)
                if bet in valid_choices:
                    username = message.author.name
                    result = await coinflip(username, bet_amount,bet,auth_id)

                    if isinstance(result, discord.Embed):
                        await message.reply(embed=result)
                    else:
                        await message.reply(result)
                else:
                    await message.reply('❌ Invalid choice. Please choose **heads** or **tails**.')
            else:
                await message.reply('❌ Invalid bet amount. Please enter a valid number.')
        else:
            await message.reply('❌ Invalid command format. Use: $coinflip **side** **amount**')
    if message.content.startswith('$balance') or message.content.startswith('$bal'):
        auth_id = message.author.id
        username = message.author.name
        content = message.content[len("$balance "):].strip() if message.content.startswith('$balance ') else message.content[len("$bal "):].strip()
        parts = content.split()
        if len(parts) == 0:
            balance = get_balance(username)
            embed = discord.Embed(
                title="**BALANCE**",
                description=f"Your balance is **{balance}**!",
            )
            await message.reply(embed=embed)
    if message.content.startswith('$work'):
        username = message.author.name
        result = await work(username)
        await message.reply(result)
    if message.content.startswith('$stats '):
        username = message.author.name
        stats = get_stats(username)
        xp_needed = 100 * stats[2]
        embed = discord.Embed(
            title="**STATS**",
            description=f"**Name** : {stats[1]} "
                        f"**Level** : {stats[2]} "
                        f"**XP** : {stats[3]} / {xp_needed}"
                        f"**Wins** : {stats[4]}"
                        f"**Losses : {stats[5]}"
                        f"**Winrate : {stats[6]} ",
        )
        await message.reply(embed=embed)

bot.run(os.getenv('TOKEN'))

