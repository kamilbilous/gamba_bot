import discord
from database import update_balance,get_balance

pic_perms = 1304859996336427068
cannon_minion = 1349869095163658381
millionaire = 1349869357949517948

async def shop_main_page(message):
    embed = discord.Embed(
        title="**The Sancshop**",
        description="1. Pic perms - gives pic perms 🤷‍♂️ **10 000 sancoins**\n"
                    "2. Cannon minion - gives you a little bit of coins every 30 mins **100 000 sancoins**\n "
                    "3. Millionaire - show off your degeneracy **1 000 000 sancoins**\n"
                    "4. Tip the dealer - pay for the dealer's therapy **777 sancoins**\n",
        colour=discord.Colour.purple()
    )
    message.reply(embed=embed)

async def buy_pic_perms(message,username):
    balance = get_balance(username)
    amount = 10000

    if balance < amount:
        await message.reply(f"You don't have enough sancoins. Your balance is **{balance} sancoins**")
    else:
        if pic_perms not in [role.id for role in message.author.roles]:
            update_balance(username, -amount)
            message.author.add_roles(pic_perms)
            embed = discord.Embed(
                title="**Success**",
                description="You have been granted pic perms!",
                colour=discord.Colour.pink()
            )
            await message.reply(embed=embed)
        elif pic_perms in [role.id for role in message.author.roles]:
            await message.reply("❌ You already have pic perms")
            return
async def buy_cannon_minion(message,username):
    amount = 100000
    balance = get_balance(username)
    if balance < amount:
        await message.reply(f"You don't have enough sancoins. Your balance is **{balance} sancoins**")
    else:
        if cannon_minion not in [role.id for role in message.author.roles]:
            update_balance(username, -amount)
            message.author.add_roles(cannon_minion)
            embed = discord.Embed(
                title="**Success**",
                description="You have been granted a cannon minion!",
                colour=discord.Colour.pink()
            )
            await message.reply(embed=embed)
        elif cannon_minion in [role.id for role in message.author.roles]:
            await message.reply("❌ You already own a cannon minion!")
            return
async def buy_millionaire(message,username):
    amount = 1000000
    balance = get_balance(username)
    if balance < amount:
        await message.reply(f"You don't have enough sancoins. Your balance is **{balance} sancoins**")
    else:
        if millionaire not in [role.id for role in message.author.roles]:
            update_balance(username,-amount)
            message.author.add_roles(millionaire)
            embed = discord.Embed(
                title="**Success**",
                description="You have become a millionaire!",
                colour=discord.Colour.pink()
            )
            await message.reply(embed=embed)
        elif millionaire in [role.id for role in message.author.roles]:
            await message.reply("❌ You're already a millionaire!")
            return
async def buy_tip(message,username):
    amount = 777
    balance = get_balance(username)
    if balance < amount:
        message.reply(f"You don't have enough sancoins. Your balance is **{balance} sancoins**")
    else:
        embed = discord.Embed(
            title="**Thank you!**",
            description="**Thank you for the tip!**",
            colour=discord.Colour.pink()
        )
        await message.reply(embed=embed)

