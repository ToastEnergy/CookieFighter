import sqlite3, config, ast, random

def get_prefix(bot, message):

  if message.guild is None:
    prefix = commands.when_mentioned_or("c/ ", "c/")(bot, message)

  else:
    with sqlite3.connect("data/db.db") as db:
        data = db.execute(f"SELECT * from prefixes where guild = {message.guild.id}")
        data = data.fetchall()

    if len(data) >= 1:
      new_prefix = str(data[0][1])
      prefix = commands.when_mentioned_or(f"{new_prefix} ", new_prefix)(bot, message)

    else:
      prefix = commands.when_mentioned_or("c/ ", "c/")(bot, message)

  return prefix

def get_settings(ctx, data):
    if not data["guilds"].get(ctx.guild.id):
        data["guilds"][ctx.guild.id] = {"users": [], "settings": {"colour": 14200170, "timeout": 120, "emoji": random.choice(config.emojis.default), "emoji_default": True}}
    return data["guilds"][ctx.guild.id]["settings"]

async def check_db(db):
    await db.execute("create table if not exists CookieFighter (data text)")
    if not (await get_data(db)):
        await db.execute("insert into CookieFighter (data) VALUES (?)", (str({"guilds": {}}),))
    await db.commit()

async def get_data(db):
    data = await db.execute("select data from CookieFighter")
    data = await data.fetchone()
    if not data:
        return None
    return ast.literal_eval(data[0])

async def update_data(db, data):
    await db.execute("update CookieFighter set data=?", (str(data),))
    await db.commit()
