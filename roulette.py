import random
import database
import discord

async def game(username, bet, choice, auth_id):
    user = database.get_user(username)

    user_id, name, level, balance,xp = user

    if balance < bet:
        return f"❌ <@{auth_id}>, you don't have enough sancoins to place this bet! Your balance: {balance} sancoins."

    database.update_balance(name, -bet)

    valid_colors = ["red", "black", "green"]
    winning_color = random.choices(["red", "black", "green"], weights=[47.5, 47.5, 5])[0]

    if choice in valid_colors:
        if choice == winning_color:
            if winning_color == "green":
                win_amount = bet * 14
            else:
                win_amount = bet * 2

            database.update_balance(name, win_amount)
            database.update_stats(name, won=True)

            # Fetch updated balance
            new_balance = database.get_user(name)[3]
            embed = discord.Embed(
                title = "Roulette result",
                description = f"The ball landed on **{winning_color}**! You won **{win_amount} sancoins**. Your new balance is **{new_balance} sancoins**.",
                color = discord.Color.green()
            )

            return embed
        else:
            database.update_stats(name, won=False)

            # Fetch updated balance
            new_balance = database.get_user(name)[3]
            embed = discord.Embed(
                title="Roulette result",
                description=f"The ball landed on **{winning_color}**! You lost **{bet} sancoins**. Your new balance is **{new_balance} sancoins**.",
                color=discord.Color.red()
            )
            return embed

    return "❌ Invalid bet choice. Please choose red, black, or green."
