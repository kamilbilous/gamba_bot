import random
import database
import discord
import time

work_cooldowns = {}

async def work(username):
    current_time = time.time()
    cooldown_period = 3 * 3600


    if username in work_cooldowns:

        last_used = work_cooldowns[username]
        time_remaining = cooldown_period - (current_time - last_used)

        if time_remaining > 0:
            cooldown_hours = time_remaining // 3600
            cooldown_minutes = (time_remaining % 3600) // 60
            embed2 = discord.Embed(
                title="Cooldown",
                description=f"❌ You must wait {int(cooldown_hours)} hour(s) and {int(cooldown_minutes)} minute(s) before working again.",
                colour=discord.Colour.red()
            )
            return embed2
    user = database.get_user(username)
    user_id, name, balance, level = user
    paycheck = random.randint(100, 700)
    database.update_balance(name,paycheck)
    new_balance = database.get_user(name)[2]
    embed = discord.Embed(
        title= "Paycheck",
        description= f"Congratulation! You've earned {paycheck} sancoins! Your balance is {new_balance}.",
        colour=discord.Colour.green()
    )
    return embed
