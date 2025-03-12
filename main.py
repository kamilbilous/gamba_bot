import discord
import os
import re

from database import insert_users_into_db, insert_server, get_server_id
from roulette import game
from keep_alive import keep_alive
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)
bets = r"^\d+$"
valid_colors = ["red", "black", "green"]
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
        GUILD = get_server_id(guild.name)
        print(f"Bot is connected to {guild.name} (ID: {GUILD})")

        # Fetch and insert all members into the database
        insert_users_into_db(guild.members)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$roulette '):
        username = message.author.name
        content = message.content[len("$roulette "):].strip()
        parts = content.split()
        if len(parts) == 2:
            bet_color = parts[0].lower()
            bet_value = parts[1]
            if re.fullmatch(bets, bet_value):
                bet_amount = int(bet_value)
                if bet_color in valid_colors:
                    # Get the username of the person who sent the message
                    username = message.author.name

                    # Place the bet and get the result
                    result = game(username, bet_amount, bet_color)

                    # Send the result to the channel
                    await message.channel.send(result)
                else:
                    # Send an error message if the color is invalid
                    await message.channel.send('❌ Invalid color. Please choose from "red", "black", or "green".')
            else:
                # Send an error message if the bet amount is invalid
                await message.channel.send('❌ Invalid bet amount. Please enter a valid number.')
        else:
            # Send an error message if the format is incorrect
             await message.channel.send('❌ Invalid command format. Use: $roulette <color> <amount>')


bot.run(os.getenv('TOKEN'))
