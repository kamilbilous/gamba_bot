import sqlite3
import discord

def connect():
    return sqlite3.connect("users.db")
def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(''' 
      CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE,
          balance INTEGER DEFAULT 0,
          level INTEGER DEFAULT 1,
          xp INTEGER DEFAULT 0
      )''')

    # Create the stats table
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS stats (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE,
          balance INTEGER DEFAULT 0,
          level INTEGER DEFAULT 1,
          xp INTEGER DEFAULT 0,
          wins INTEGER DEFAULT 0,
          losses INTEGER DEFAULT 0,
          winrate REAL DEFAULT 0.0,
          FOREIGN KEY (name) REFERENCES users (name),
          foreign key (balance) REFERENCES levels (balance),
          foreign key (level) REFERENCES users (level),
          FOREIGN KEY (xp) REFERENCES users (xp),
          FOREIGN KEY (level) REFERENCES users (level)
      )''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
    conn.commit()
    conn.close()




def insert_server(guild):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO servers (id, name) VALUES (?, ?)", (guild.id, guild.name))
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()


def insert_users_into_db(users):
    conn = connect()
    cursor = conn.cursor()

    for member in users:
        name = member.name
        balance = 0

        try:
            cursor.execute("INSERT INTO users (name, balance) VALUES (?, ?)", (name, balance))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

#Fetch users
def get_user(name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, level, balance,xp FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute("INSERT INTO users (name, balance) VALUES (?, ?)", (name, 0))
        conn.commit()
        return get_user(name)  # Fetch again after insertion

    conn.close()
    return user
def get_level(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_balance(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()
    conn.close()
    return user

# Fetch or create user stats
def get_stats(name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name,level,balance,xp, wins, losses, winrate FROM stats WHERE name = ?", [name])
    stats = cursor.fetchone()

    if stats is None:
        cursor.execute("INSERT INTO stats (id, name,level,balance,xp, wins, losses, winrate) VALUES (?, ?, ?, ?, ?,?,?,?)",
                       (get_user(name)[0], name, 0,1,0,0, 0, 0.0))
        conn.commit()
        return get_stats(name)

    conn.close()
    return stats


async def sort_leaderboard(message, choice):
    if choice not in ["money", "level"]:
        await message.reply("❌ Invalid choice! Use `money` or `level`.")
        return

    if choice == "money":
        try:
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, level, balance from users
                    ORDER BY balance DESC
                    LIMIT 10
                """)
                users = cursor.fetchall()
            embed = discord.Embed(
                title="Leaderboard",
                description= "TOP 10 users sorted by balance\n",
                colour=discord.Colour.gold()
            )
            for rank, (name, balance, level) in enumerate(users, start=1):
                embed.add_field(
                    name=f"#{rank} {name}",
                    value=f"**Balance: {balance} sancoins** \n📈 **Level: `{level}`**",
                    inline=False
                )

            await message.reply(embed=embed)
        except Exception as e:
            print(e)

    if choice == "level":
        try:
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, level, balance from users
                    ORDER BY level DESC
                    LIMIT 10
                """)
                users = cursor.fetchall()
            embed = discord.Embed(
                title="Leaderboard",
                description= "TOP 10 users sorted by level\n",
                colour=discord.Colour.gold()
            )
            for rank, (name, balance, level) in enumerate(users, start=1):
                embed.add_field(
                    name=f"#{rank} {name}",
                    value=f"**Level: {level} ** \n📈 **Balance: `{balance} sancoins`**",
                    inline=False
                )

            await message.reply(embed=embed)
        except Exception as e:
            print(e)




# Update user balance
def update_balance(name, amount):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE name = ?", (amount, name))
    conn.commit()
    conn.close()

def update_level(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET level = level + 1, xp = 0 WHERE name = ?", (name,))
    conn.commit()
    conn.close()
def update_xp(name, xp_gain):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = xp + ? WHERE name = ?", (xp_gain, name))
    conn.commit()
    conn.close()

# Update stats
def update_stats(name, won):
    conn = connect()
    cursor = conn.cursor()

    if won:
        cursor.execute("UPDATE stats SET wins = wins + 1 WHERE name = ?", (name,))
    else:
        cursor.execute("UPDATE stats SET losses = losses + 1 WHERE name = ?", (name,))

    # Update winrate
    cursor.execute("""
            UPDATE stats 
            SET winrate = CASE 
                WHEN (wins + losses) > 0 THEN (wins * 100.0) / (wins + losses)
                ELSE 0.0 
            END 
            WHERE name = ?
        """, (name,))

    conn.commit()
    conn.close()

init_db()