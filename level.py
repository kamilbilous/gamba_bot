from database import update_level,update_xp,get_user

async def level_up(username):
    user = get_user(username)
    user_id, name, level, balance, xp = user
    xp_needed = 100 * level

    if xp >= xp_needed:
        update_level(name)
        excess_xp = xp - xp_needed
        update_xp(name, excess_xp)
        return True
    return False



