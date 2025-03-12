import random
import database


def game(username, bet, choice, auth_id):
    user = database.get_user(username)

    user_id, name, balance = user

    if balance < bet:
        return f"❌ <@{auth_id}>, you don't have enough balance to place this bet! Your balance: {balance}."

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
            new_balance = database.get_user(name)[2]

            return f"🎉 <@{auth_id}> bet on {choice} and won! 🎊 The ball landed on {winning_color}. New balance: {new_balance}"
        else:
            database.update_stats(name, won=False)

            # Fetch updated balance
            new_balance = database.get_user(name)[2]

            return f"💀 <@{auth_id}> bet on {choice} but lost. The ball landed on {winning_color}. New balance: {new_balance}"

    return "❌ Invalid bet choice. Please choose red, black, or green."
