import discord
import os
import re
from roulette import game

bot = discord.Client()
bets = r"^\d+$"
valid_colors = ["red", "black", "green"]
@bot.event
async def on_ready():
    print('We have logged in as {bot.user}')

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
