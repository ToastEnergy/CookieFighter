# ⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆ 
# ⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠁⠸⣼⡿ 
# ⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀ 
# ⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
# ⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉

import discord, os, functools, aiosqlite, random
from discord.ext import commands
from datetime import datetime

def check_perms():
    async def predicate(ctx):
        error = False
        emb = discord.Embed(description = f"I'm missing these permissions to run the command `{ctx.command}`:\n", colour = ctx.bot.colour)
        embed = True

        if not ctx.guild.me.permissions_in(ctx.channel).use_external_emojis:
            emb.description += "**• Use external emojis**\n"
            error = True

        if not ctx.guild.me.permissions_in(ctx.channel).add_reactions:
            emb.description += "**• Use external emojis**\n"
            error = True

        if not ctx.guild.me.permissions_in(ctx.channel).read_message_history:
            emb.description += "**• Read message history**\n"
            error = True
        
        if not ctx.guild.me.permissions_in(ctx.channel).embed_links:
            emb.description += "**• Embed links**"
            embed = False
            error = True

        if error:
            if embed:
                await ctx.send(embed = emb)
                return False

            else:
                await ctx.send(emb.description)
                return False

        return True
    return commands.check(predicate)


async def guild_prefix(guild_id):
    async with aiosqlite.connect("data/db.db") as db:
        data = await db.execute(f"select * from prefixes where guild = {guild_id}")
        data = await data.fetchall()

    if len(data) == 0:
        prefix = "c/"

    else:
        prefix = data[0][1]

    return prefix

async def quickembed(ctx, text):
    "Make a quick embed (automatically sends it)"
    emb = discord.Embed(description = text, colour = 0xd8ad6a)
    await ctx.channel.send(embed = emb)

async def guild_settings(guild_id):
    async with aiosqlite.connect("data/db.db") as db:
        data = await db.execute(f"select * from settings where id = {guild_id}")
        data = await data.fetchall()

    default = {"colour": 14200170, "timeout": 120, "emoji": "<:ChristmasCookie:790492019372982272>", "emoji_default": True}
    # random.choice(["<:mc_cookie:726184620164382741>", "<:gocciola:747247300803297290>", "<:oreo:761274120821276702>"])
    if len(data) == 0:
        options = default

    else:
        colour = data[0][1]
        emoji = data[0][2]
        timeout = data[0][3]
        
        if str(colour) == "0": colour = default["colour"]

        if str(emoji) == "0": 
            emoji = default["emoji"] 
            e_d = True

        else:
            e_d = False

        if str(timeout) == "0.0": timeout = default["timeout"]

        options = {
            "colour": int(colour),
            "emoji": int(emoji),
            "timeout": timeout,
            "emoji_default": e_d
        }

    return options

class Git:
    def __init__(self, loop):
        self.loop = loop

    def sync_pull(self):
        os.system("git pull origin master")

    def sync_push(self, commit):
        os.system("git add .")
        os.system(f'git commit -m "{commit}"')
        os.system("git push origin master")

    async def pull(self):
        sync_process = functools.partial(self.sync_pull)
        await self.loop.run_in_executor(None, sync_process)

    async def push(self, commit="auto push"):
        sync_process = functools.partial(self.sync_push, commit)
        await self.loop.run_in_executor(None, sync_process)

class Database:
    def __init__(self):
        pass

    async def add_cookies(self, user, cookies, message_id = None, duration = None):
        async with aiosqlite.connect("data/db.db") as db:
            data = await db.execute(f"SELECT * from users where user = '{user}'")
            data = await data.fetchall()

            if len(data) == 0:
                await db.execute(f"INSERT into users (user, cookies) VALUES ('{user}', {cookies})")

            else:
                final_data = int(data[0][1]) + int(cookies)
                await db.execute(f"UPDATE users set cookies = {final_data} where user = {user}")

            if message_id:
                await db.execute(f"INSERT into results (user, message, time) VALUES ('{user}', '{message_id}', '{duration:.4f}')")
            await db.commit()

    async def remove_cookies(self, user, cookies):
        async with aiosqlite.connect("data/db.db") as db:
            data = await db.execute(f"SELECT * from users where user = '{user}'")
            data = await data.fetchall()

            if len(data) == 0:
                raise KeyError(user)

            else:
                final_data = int(data[0][1]) - int(cookies)

                if final_data < 0:
                    final_data = 0

                await db.execute(f"UPDATE users set cookies = {final_data} where user = {user}")

            await db.commit()