import discord
import os
import re

from database import insert_users_into_db, insert_server
from roulette import game
from keep_alive import keep_alive
from dotenv import load_dotenv
from coinflip import coinflip


load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)
bets = r"^\d+$"
valid_colors = ["red", "black", "green"]
valid_choices = ["heads", "tails"]
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

keep_alive()
bot.run(os.getenv('TOKEN'))

