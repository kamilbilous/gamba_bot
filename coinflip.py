import random
import database
import discord

async def coinflip(username, bet, choice, auth_id):
    user = database.get_user(username)

    user_id, name, level, balance, xp = user
    if balance < bet:
        return f"❌ <@{auth_id}>, you don't have enough sancoins to place this bet! Your balance: {balance} sancoins."

    database.update_balance(name, -bet)
    valid_choices = ["heads", "tails"]
    winning_choice = random.choice(valid_choices)
    if choice in valid_choices:
        if choice == winning_choice:
            win_amount = bet * 2

            database.update_balance(name, win_amount)
            database.update_stats(name, won=True)

            new_balance = database.get_user(name)[2]
            embed = discord.Embed(
                title="Coinflip result",
                description=f"The coin landed on **{winning_choice}**! You won **{win_amount} sancoins**. Your new balance is **{new_balance} sancoins**.",
                color=discord.Color.green()
            )

            return embed
        else:
            database.update_stats(name, won=False)

            # Fetch updated balance
            new_balance = database.get_user(name)[2]
            embed = discord.Embed(
                title="Roulette result",
                description=f"The coin landed on **{winning_choice}**! You lost **{bet} sancoins**. Your new balance is **{new_balance} sancoins**.",
                color=discord.Color.red()
            )
            return embed

    return "❌ Invalid bet choice. Please choose heads or tails."
