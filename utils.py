import sqlite3, config, ast, random, asyncio

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
        data["guilds"][ctx.guild.id] = {"users": {}, "settings": {"colour": 14200170, "timeout": 120, "emoji": random.choice(config.emojis.default), "emoji_default": True}, "durations": []}
    if data["guilds"][ctx.guild.id]["settings"]["emoji_default"]:
        data["guilds"][ctx.guild.id]["settings"]["emoji"] = random.choice(config.emojis.default)
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

async def countdown(message, embed):
    for number in config.bot.countdown:
        if number == config.bot.countdown[0]:
            pass
        else:
            embed.description = f"```\n{number}\n```"
            await message.edit(content=None, embed=embed)
        await asyncio.sleep(1)

async def add_cookies(db, data: dict, guild_id: int, user_id: int, cookies: int, duration):
    user = data["guilds"][guild_id]["users"].get(user_id)
    if not user:
        data["guilds"][guild_id]["users"][user_id] = cookies
    else:
        data["guilds"][guild_id]["users"][user_id] += cookies
    data["guilds"][guild_id]["durations"].append({"user": user_id, "duration": f"{duration:.4f}"})
    await update_data(db, data)

async def check_other_users(user, message, embed):
    msg = await message.channel.fetch_message(message.id) # fetch it again to get new users
    users = await msg.reactions[0].users().flatten()
    others = "\n".join([str(u) for u in users if u.id != user.id and not u.bot])

    if len(others) >= 1:
        emb.description += f"Other players:\n{others}"
        await msg.edit(embed = emb)
