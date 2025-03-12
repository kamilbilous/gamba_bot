import sqlite3

def connect():
    return sqlite3.connect("users.db")
def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(''' 
      CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE,
          balance INTEGER DEFAULT 100
      )''')

    # Create the stats table
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS stats (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE,
          wins INTEGER DEFAULT 0,
          losses INTEGER DEFAULT 0,
          winrate REAL DEFAULT 0.0,
          FOREIGN KEY (name) REFERENCES users (name)
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

    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute("INSERT INTO users (name, balance) VALUES (?, ?)", (name, 1000))
        conn.commit()
        return get_user(name)  # Fetch again after insertion

    conn.close()
    return user


# Fetch or create user stats
def get_stats(name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stats WHERE name = ?", (name,))
    stats = cursor.fetchone()

    if stats is None:
        cursor.execute("INSERT INTO stats (id, name, wins, losses, winrate) VALUES (?, ?, ?, ?, ?)",
                       (get_user(name)[0], name, 0, 0, 0.0))
        conn.commit()
        return get_stats(name)  # Fetch again

    conn.close()
    return stats


# Update user balance
def update_balance(name, amount):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE name = ?", (amount, name))
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
    cursor.execute("UPDATE stats SET winrate = (wins * 100.0) / (wins + losses) WHERE name = ?", (name,))

    conn.commit()
    conn.close()

init_db()