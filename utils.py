import discord, config, random, asyncio, datetime

async def error(ctx, message):
    emb = discord.Embed(description=f"{config.emojis.fail} | {message}", colour=discord.Colour.red())
    try: await ctx.reply(embed=emb, mention_author=False)
    except: await ctx.send(embed=emb)

async def success(ctx, message, colour=None):
    emb = discord.Embed(description=f"{config.emojis.check} | {message}", colour=colour or discord.Colour.green())
    try: await ctx.reply(embed=emb, mention_author=False)
    except: await ctx.send(embed=emb)

async def get_settings(db, guild=None):
    if not guild:
        return {"prefix": config.bot.prefix, "colour": config.bot.colour, "timeout": config.bot.timeout, "emoji": random.choice(config.emojis.default), "spawn": config.bot.spawn, "spawnrate": config.bot.spawnrate}
        
    data = await (await db.execute("SELECT prefix, colour, timeout, emoji, spawn, spawnrate FROM settings WHERE guild=?", (guild,))).fetchone()
    if not data:
        await db.execute("INSERT INTO settings (guild, prefix, colour, timeout, spawn, spawnrate) VALUES (?, ?, ?, ?, ?, ?)", (guild, config.bot.prefix, config.bot.colour, config.bot.timeout, config.bot.spawn, config.bot.spawnrate))
        await db.commit()
        return {"prefix": config.bot.prefix, "colour": config.bot.colour, "timeout": config.bot.timeout, "emoji": random.choice(config.emojis.default), "spawn": config.bot.spawn, "spawnrate": config.bot.spawnrate}

    emoji = data[3] or random.choice(config.emojis.default)
    spawn = True if int(data[4]) == 1 else False
    return {"prefix": data[0], "colour": data[1], "timeout": data[2], "emoji": emoji, "spawn": spawn, "spawnrate": data[5]}

async def check_db(db):
    await db.execute("CREATE TABLE IF NOT EXISTS users (user id, guild id, cookies id)")
    await db.execute("CREATE TABLE IF NOT EXISTS entries (user id, guild id, duration id, type text)")
    await db.execute("CREATE TABLE IF NOT EXISTS settings (guild id, prefix text, colour id, timeout id, emoji text, spawn id, spawnrate id)")
    await db.execute("CREATE TABLE IF NOT EXISTS shop (guild id, role id, cookies id)")
    await db.execute("CREATE TABLE IF NOT EXISTS inventory (user id, guild id, role id)")
    await db.execute("CREATE TABLE IF NOT EXISTS spawn (guild id, enabled id, spawn_perc id)")
    await db.execute("CREATE TABLE IF NOT EXISTS spawn_channels (channel id)")
    await db.execute("CREATE TABLE IF NOT EXISTS spawn_messages (guild id, channel id, message id, time text, emoji text)")
    await db.commit()

async def countdown(message, embed):
    for number in config.bot.countdown:
        if number == config.bot.countdown[0]:
            pass
        else:
            embed.description = f"```\n{number}\n```"
            await message.edit(content=None, embed=embed)
        await asyncio.sleep(1)

async def check_user(db, user, guild):
    data = await (await db.execute("SELECT cookies FROM users WHERE user=? AND guild=?", (user, guild))).fetchone()
    return False if not data else True

async def add_cookie(db, user, guild, duration=None, type=None):

    if await check_user(db, user, guild):
        await db.execute("UPDATE users SET cookies=cookies+? WHERE user=? AND guild=?", (1, user, guild))
    else:
        await db.execute("INSERT INTO users (user, guild, cookies) VALUES (?, ?, ?)", (user, guild, 1))
    await db.execute("INSERT INTO entries (user, guild, duration, type) VALUES (?, ?, ?, ?)", (user, guild, duration, type))
    await db.commit()

async def add_cookies(db, user, guild, cookies):
    if await check_user(db, user, guild):
        await db.execute("UPDATE users SET cookies=cookies+? WHERE user=? AND guild=?", (cookies, user, guild))
    else:
        await db.execute("INSERT INTO users (user, guild, cookies) VALUES (?, ?, ?)", (user, guild, cookies))
    await db.commit()

async def remove_cookies(db, user, guild, cookies):
    await db.execute("UPDATE users SET cookies=cookies-? WHERE user=? AND guild=?", (cookies, user, guild))
    await db.commit()

async def check_other_users(user, message, embed):
    msg = await message.channel.fetch_message(message.id) # fetch it again to get new users
    users = await msg.reactions[0].users().flatten()
    others = "\n".join([f"**{str(u)}**" for u in users if u.id != user.id and not u.bot])

    if len(others) >= 1:
        embed.description += f"\n__Other players:__\n\n>>> {others}"
        await msg.edit(embed=embed)

async def get_users(db, guild):
    users = dict()
    entries = await (await db.execute("SELECT user, cookies FROM users WHERE guild=?", (guild,))).fetchall()

    for entry in entries:
        users[int(entry[0])] = int(entry[1])

    return users if len(users) > 0 else None

async def get_cookies(db, user, guild):
    data = await (await db.execute("SELECT cookies FROM users WHERE user=? AND guild=?", (user, guild))).fetchone()
    return 0 if not data else data[0]

async def get_roles(db, guild):
    data = await (await db.execute("SELECT role, cookies FROM shop WHERE guild=?", (guild.id,))).fetchall()

    if not data:
        return None

    roles = dict()
    for raw in data:
        role = guild.get_role(raw[0])
        if role:
            roles[role] = raw[1]

    roles_list = sorted(roles, key=lambda role : roles[role])

    return {r: roles[r] for r in roles_list}

async def update_inventory(db, user, guild, role):
    await db.execute("INSERT INTO inventory (user, guild, role) VALUES (?, ?, ?)", (user, guild, role))
    await db.commit()

async def remove_from_inventory(db, user, guild, role):
    await db.execute("DELETE FROM inventory WHERE user=? AND guild=? AND role=?", (user, guild, role))
    await db.commit()

async def get_inventory(db, user, guild):
    data = await (await db.execute("SELECT role FROM inventory WHERE user=? AND guild=?", (user, guild))).fetchall()
    return None if not data else [d[0] for d in data]

async def add_to_shop(db, guild, role, cookies):
    roles = await get_roles(db, guild)
    if roles and role in [r.id for r in roles]:
        await db.execute("UPDATE shop SET cookies=? WHERE role=? AND guild=?", (cookies, role, guild.id))
    else:
        await db.execute("INSERT INTO SHOP (guild, role, cookies) VALUES (?, ?, ?)", (guild.id, role, cookies))
    await db.commit()

async def remove_from_shop(db, guild, role):
    await db.execute("DELETE FROM shop WHERE role=? AND guild=?", (role, guild))

async def reset_leaderboard(db, guild):
    await db.execute("DELETE FROM users WHERE guild=?", (guild,))
    await db.execute("DELETE FROM entries WHERE guild=?", (guild,))
    await db.commit()

async def get_spawn_status(db, guild):
    data = await (await db.execute("SELECT spawn FROM settings WHERE guild=?", (guild,))).fetchone()
    return 'disabled' if not data or int(data[0]) == 0 else 'enabled'

async def enable_spawn(db, guild):
    data = await (await db.execute("SELECT enabled FROM spawn WHERE guild=?", (guild,))).fetchone()
    if not data:
        await db.execute("INSERT INTO spawn (guild,enabled,spawn_perc) VALUES (?,1,?)", (guild,config.bot.default_spawn_rate))
    else:
        await db.execute("UPDATE spawn SET enabled=1 WHERE guild=?", (guild,))
    await db.commit()

async def disable_spawn(db, guild):
    data = await (await db.execute("SELECT enabled FROM spawn WHERE guild=?", (guild,))).fetchone()
    if not data:
        await db.execute("INSERT INTO spawn (guild,enabled,spawn_perc) VALUES (?,0,?)", (guild,config.bot.default_spawn_rate))
    else:
        await db.execute("UPDATE spawn SET enabled=0 WHERE guild=?", (guild,))
    await db.commit()

async def calc_spawn(perc):
    prob = list()
    [prob.append(False) for x in range(100-perc)]
    [prob.append(True) for x in range(perc)]
    return random.choice(prob)

async def add_timer(db, guild, channel, message, date, emoji):
    await db.execute("INSERT INTO spawn_messages (guild,channel,message,time,emoji) VALUES (?,?,?,?,?)", (guild, channel, message, date.strftime("%x %X"),emoji))
    await db.commit()

async def remove_timer(db, message):
    await db.execute("DELETE FROM spawn_messages WHERE message=?", (message,))
    await db.commit()

class SpawnMessage:
    def __init__(self, guild, channel, message, date, emoji):
        self.guild = guild
        self.channel = channel
        self.message = message
        self.date = date
        self.emoji = emoji

async def get_spawn_messages(db):
    data = await (await db.execute("SELECT * FROM spawn_messages")).fetchall()
    return [SpawnMessage(int(d[0]), int(d[1]), int(d[2]), datetime.datetime.strptime(d[3], "%x %X"), d[4]) for d in data]

async def check_message_spawn(db, message):
    data = await (await db.execute("SELECT message FROM spawn_messages WHERE message=?", (message,))).fetchone()
    return False if not data else True

async def edit_spawn_rate(db, guild, rate):
    data = await (await db.execute("SELECT enabled FROM spawn WHERE guild=?", (guild,))).fetchone()
    if not data:
        await db.execute("INSERT INTO spawn (guild,enabled,spawn_perc) VALUES (?,0,?)", (guild,rate))
    else:
        await db.execute("UPDATE spawn SET spawn_perc=? WHERE guild=?", (rate,guild))
    await db.commit()

async def add_ignored_channel(db, channel):
    await db.execute("INSERT INTO spawn_channels (channel) VALUES (?)", (channel,))
    await db.commit()

async def remove_ignored_channel(db, channel):
    await db.execute("DELETE FROM spawn_channels WHERE channel=?", (channel,))
    await db.commit()

async def is_ignored(db, channel):
    data = await (await db.execute("SELECT channel FROM spawn_channels WHERE channel=?", (channel,))).fetchone()
    return False if not data else True

async def send_embed(ctx, embed, components=None):
    try: msg = await ctx.reply(embed=embed, mention_author=False, components=components)
    except: msg = await ctx.send(embed=embed, components=components)
    return msg

def get_emoji(bot, emoji):
    return discord.utils.get(bot.emojis, id=int(emoji.split(":")[2][:-1]))

def invite_url(id):
    return discord.utils.oauth_url(id, scopes=('bot','applications.commands'), permissions=discord.Permissions(permissions=280640))
