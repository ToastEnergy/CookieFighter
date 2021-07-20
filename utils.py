import config, ast, random, asyncio

async def get_settings(db, guild):
    data = await (await db.execute("SELECT prefix, colour, timeout, emoji FROM settings WHERE guild=?", (guild,))).fetchone()
    if not data:
        await db.execute("INSERT INTO settings (guild, prefix, colour, timeout) VALUES (?, ?, ?, ?)", (guild, config.bot.prefix, config.bot.colour, config.bot.timeout))
        await db.commit()
        return {"prefix": config.bot.prefix, "colour": config.bot.colour, "timeout": config.bot.timeout, "emoji": random.choice(config.emojis.default)}

    emoji = data[3] or random.choice(config.emojis.default)
    return {"prefix": data[0], "colour": data[1], "timeout": data[2], "emoji": emoji}

async def check_db(db):
    await db.execute("CREATE TABLE IF NOT EXISTS entries (user id, guild id, duration id, type text)")
    await db.execute("CREATE TABLE IF NOT EXISTS settings (guild id, prefix text, colour id, timeout id, emoji text)")
    await db.execute("CREATE TABLE IF NOT EXISTS shop (guild id, role id, cookies id)")
    await db.commit()

async def countdown(message, embed):
    for number in config.bot.countdown:
        if number == config.bot.countdown[0]:
            pass
        else:
            embed.description = f"```\n{number}\n```"
            await message.edit(content=None, embed=embed)
        await asyncio.sleep(1)

async def add_cookie(db, user, guild, duration=None, type=None):
    await db.execute("INSERT INTO entries (user, guild, duration, type) VALUES (?, ?, ?, ?)", (user, guild, duration, type))
    await db.commit()

async def add_cookies(db, user, guild, cookies):
    for x in range(cookies):
        await db.execute("INSERT INTO entries (user, guild) VALUES (?, ?)", (user, guild))
    await db.commit()

async def check_other_users(user, message, embed):
    msg = await message.channel.fetch_message(message.id) # fetch it again to get new users
    users = await msg.reactions[0].users().flatten()
    others = "\n".join([str(u) for u in users if u.id != user.id and not u.bot])

    if len(others) >= 1:
        emb.description += f"Other players:\n{others}"
        await msg.edit(embed = emb)

async def get_users(db, guild):
    users = dict()
    entries = await (await db.execute("SELECT user FROM entries WHERE guild=?", (guild,))).fetchall()

    for entry in entries:
        try: users[entry[0]] += 1
        except KeyError: users[entry[0]] = 1

    return users if len(users) > 0 else None

async def get_cookies(db, user, guild):
    return (await (await db.execute("SELECT COUNT(*) FROM entries WHERE user=? AND guild=?", (user, guild))).fetchone())[0]

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
