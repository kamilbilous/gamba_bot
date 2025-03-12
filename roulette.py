import random
import database

def game(username,bet,choice):
    user = database.get_user(username)
    user_id, name, balance = user

    if balance < bet:
        return f"❌ {name}, you don't have enough balance to place this bet!"
    database.update_balance(name,-bet)
    valid_colors = ["red","black","green"]
    colors = random.choices(["red", "black", "green"], weights=[47.5, 47.5, 5])[0]

    if choice in valid_colors:
        if choice == colors:
            if colors == "green":
                win = bet * 14
            else:
                win = bet * 2
            database.update_balance(name, +win)
            database.update_stats(name, won=True)
            return f"🎉 {name} bet on {choice} and won! The ball landed on {colors}. New balance: {balance}"
        else:
            database.update_stats(name, won=False)
            return f"💀 {name} bet on {choice} but lost! The ball landed on {colors}. New balance: {balance}"
    return "❌ Invalid bet choice."
