import discord, traceback, io, textwrap, sys, copy, subprocess, asyncio, cookies, aiosqlite, os, aiohttp
from discord.ext import commands
from contextlib import redirect_stdout
from dotenv import load_dotenv

load_dotenv(dotenv_path = ".env")

class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.git = cookies.Git(self.bot.loop)

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    @commands.command()
    async def eval(self, ctx, *, body: str):
        "Evaluates a code"

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        body = "import cookies\nimport aiohttp\nimport aiosqlite\n" + body
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.message.add_reaction("<:redtick:726040662411313204>")
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('<a:check:726040431539912744>')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(value)
            else:
                self._last_result = ret
                await ctx.send(f'{value}{ret}')

    @commands.command()
    async def old_set(self, ctx):
        emb = discord.Embed(description = """```
╔═╗╔═╗╔═╗╦╔═╦╔═╗  ╔═╗╦╔═╗╦ ╦╔╦╗╔═╗╦═╗
║  ║ ║║ ║╠╩╗║║╣   ╠╣ ║║ ╦╠═╣ ║ ║╣ ╠╦╝
╚═╝╚═╝╚═╝╩ ╩╩╚═╝  ╚  ╩╚═╝╩ ╩ ╩ ╚═╝╩╚═```
**Welcome to the Cookie Fighter Support Server!**
> Check Bot news in <#725860610805334046>! 
> Ask for support in <#726027699600097280>!
> Chat and fight people in <#726027856462872576>!
> Use other commands in <#726027884036096011>!

```
╦═╗╦ ╦╦  ╔═╗╔═╗
╠╦╝║ ║║  ║╣ ╚═╗
╩╚═╚═╝╩═╝╚═╝╚═╝```
**Follow these rules to not get banned / kicked / muted.**
> `1.` Don't advertise anything (Servers, YouTube channels, Twitch channels etc..)
> `2.` Don't be a dick with the community.
> `3.` Don't spam commands in <#726027856462872576> (`cookie` command is ok), pls use <#726027884036096011>.
> `4.` Don't insult anyone, for any reason.

```
╦  ╦╔╗╔╦╔═╔═╗
║  ║║║║╠╩╗╚═╗
╩═╝╩╝╚╝╩ ╩╚═╝```
**Some links that could help you.**
> Support Server: https://discord.gg/vCUpW9E
> Bot Invite: https://bit.ly/cookiefighter
> Top.GG: [Click Here](https://top.gg/bot/638483485417406495)
""", colour = self.bot.colour)
        emb.set_author(name = self.bot.user.name, icon_url = str(self.bot.user.avatar_url_as(static_format = "png")))
        await ctx.send(embed = emb)

    @commands.command()
    async def restart(self, ctx):
        "Restart the bot"
        emb = discord.Embed(description = "Restarting the bot...", colour = self.bot.colour)
        await ctx.send(embed = emb)
        subprocess.call('python3 main.py', shell=True)
        await self.bot.close()  

    @commands.command()
    async def test(self, ctx):
        async with aiosqlite.connect("data/db.db") as db:
            data = await db.execute("tables")
            return await ctx.send(await data.fetchall())

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        emb = discord.Embed(title = 'Loading...', colour = self.bot.colour)
        emb1 = discord.Embed(title = f'Loaded {extension}!', colour = self.bot.colour)
        msg = await ctx.send(embed = emb)
        await asyncio.sleep(0.5)
        
        try:
            self.bot.load_extension(f'cogs.{extension}')
            await msg.edit(embed = emb1)

        except Exception as e:
            traceback.print_exc()
            error = discord.Embed(title = f"""UH! There was an error with {extension}!""", description = str(e), colour = self.bot.colour)
            await msg.edit(embed = error)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension=None):

        if not extension:
            emb = discord.Embed(title = f"{self.bot.clock} | reloading extensions", colour = self.bot.colour, description = "")
            msg = await ctx.send(embed = emb)

            await self.git.pull()

            errors = ""
            for ext in os.listdir("./cogs"):
                if ext.endswith(".py"):
                    try:
                        self.bot.unload_extension(f'cogs.{ext[:-3]}')
                        self.bot.load_extension(f'cogs.{ext[:-3]}')
                        emb.description += f"<a:check:726040431539912744> | {ext}\n"

                    except Exception as e:
                        emb.description += f"<a:fail:727212831782731796> | {ext}\n"
                        errors += f"• {e}\n"

            emb.description += f"\n{errors}"
            emb.title = None
            return await msg.edit(embed = emb, content = None)
        
        emb = discord.Embed(title = 'Loading...', colour = self.bot.colour)
        emb1 = discord.Embed(title = f'Reloaded {extension}!', colour = self.bot.colour)
        msg = await ctx.send(embed = emb)
        await self.git.pull()
        
        try:    
            self.bot.unload_extension(f'cogs.{extension}')
            self.bot.load_extension(f'cogs.{extension}')
        
            await msg.edit(embed = emb1)

        except Exception as e:
            traceback.print_exc()

            error = discord.Embed(title = f"""UH! There was an error with {extension}!""", description = str(e), colour = self.bot.colour)
            await msg.edit(embed = error)

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        emb = discord.Embed(title = 'Loading...', colour = self.bot.colour)
        emb1 = discord.Embed(title = f'Unloaded {extension}!', colour = self.bot.colour)
        msg = await ctx.send(embed = emb)
        await asyncio.sleep(0.5)
        
        try:
            self.bot.unload_extension(f'cogs.{extension}')
            await msg.edit(embed = emb1)

        except Exception as e:
            traceback.print_exc()
            error = discord.Embed(title = f"""UH! There was an error with {extension}!""", description = str(e), colour = self.bot.colour)
            await msg.edit(embed = error)

    @commands.command(aliases = ["post"])
    @commands.is_owner()
    async def post_guild_count(self, ctx):
            url = f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats"
            headers = {"Authorization": str(os.environ.get("discordbotsgg"))}
            url1 = f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats"    
            headers1 = {"Authorization": str(os.environ.get("discordbotlist"))}
            url2 = f"https://api.discordextremelist.xyz/v2/bot/{self.bot.user.id}/stats"
            headers2 = {"Authorization": str(os.environ.get("discordextremelist")), "Content-Type": "application/json"}

            async with aiohttp.ClientSession() as cs:
                    await cs.post(url, headers = headers, data = {"guildCount": len(self.bot.guilds)})
                    await cs.post(url1, headers = headers1, data = {"guilds": len(self.bot.guilds), "users": len(self.bot.users), "voice_connections": 0})
                    await cs.post(url2, headers = headers2, data = {"guildCount": len(self.bot.guilds)})
            await cs.close()
            await ctx.send("""**Posted guild count on**
> - <https://discord.bots.gg/bots/638483485417406495>
> - <https://discordbotlist.com/bots/cookie-fighter>
> - <https://discordextremelist.xyz/en-US/bots/638483485417406495>""")

    @commands.command()
    @commands.is_owner()
    async def add(self, ctx, user: discord.User, cookies: int):
        "Add some cookies to a user"

        winner = str(user.id)

        emb = discord.Embed(description = f"Adding **{cookies} {self.bot.cookie}** to {user.mention}...", colour = self.bot.colour)
        msg = await ctx.send(embed = emb)
      
        async with aiosqlite.connect("data/db.db") as db:
            try:
                data = await db.execute(f"SELECT * from '{winner}'")
                data = await data.fetchall()
                final_data = int(data[0][0]) + cookies
                await db.execute(f"UPDATE '{winner}' set cookies = '{final_data}'")
                await db.commit()
            except aiosqlite.OperationalError:
                await db.execute(f"CREATE table '{winner}' (cookies id)")
                await db.execute(f"INSERT into '{winner}' (cookies) values ('{cookies}')")
                await db.execute(f"INSERT into ids (ids) values ('{winner}')")
                await db.commit()

        emb.description = f"<a:check:726040431539912744> | Added **{cookies} {self.bot.cookie}** to {user.mention}!"
        await msg.edit(embed = emb)

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, user: discord.User, cookies: int):
        "Remove some cookies to a user"

        winner = str(user.id)

        emb = discord.Embed(description = f"Removing **{cookies} {self.bot.cookie}** to {user.mention}...", colour = self.bot.colour)
        msg = await ctx.send(embed = emb)
      
        async with aiosqlite.connect("data/db.db") as db:
            try:
                data = await db.execute(f"SELECT * from '{winner}'")
                data = await data.fetchall()
                final_data = int(data[0][0]) - cookies
                await db.execute(f"UPDATE '{winner}' set cookies = '{final_data}'")
                await db.commit()
            except aiosqlite.OperationalError:
                await db.execute(f"CREATE table '{winner}' (cookies id)")
                await db.execute(f"INSERT into '{winner}' (cookies) values ('1')")
                await db.execute(f"INSERT into ids (ids) values ('{winner}')")
                await db.commit()

        emb.description = f"<a:check:726040431539912744> | Removed **{cookies} {self.bot.cookie}** to {user.mention}!"
        await msg.edit(embed = emb)

    @commands.command(name = "set")
    @commands.is_owner()
    async def set_(self, ctx, user: discord.User, cookies: int):
        "Set some cookies to a user"

        winner = str(user.id)

        emb = discord.Embed(description = f"Setting **{cookies} {self.bot.cookie}** to {user.mention}...", colour = self.bot.colour)
        msg = await ctx.send(embed = emb)
      
        async with aiosqlite.connect("data/db.db") as db:
            try:
                data = await db.execute(f"SELECT * from '{winner}'")
                data = await data.fetchall()
                final_data = cookies
                await db.execute(f"UPDATE '{winner}' set cookies = '{final_data}'")
                await db.commit()
            except aiosqlite.OperationalError:
                await db.execute(f"CREATE table '{winner}' (cookies id)")
                await db.execute(f"INSERT into '{winner}' (cookies) values ('{cookies}')")
                await db.execute(f"INSERT into ids (ids) values ('{winner}')")
                await db.commit()

        emb.description = f"<a:check:726040431539912744> | Set **{cookies} {self.bot.cookie}** to {user.mention}!"
        await msg.edit(embed = emb)

    @commands.group(invoke_without_command = True, aliases = ["sql"])
    @commands.is_owner()
    async def sqlite(self, ctx, *, command):
        "run a sqlite command"

        command = eval(f"f'{command}'")
        
        async with aiosqlite.connect("data/db.db") as db:
            data = await db.execute(command)

            if command.lower().startswith("select"):
                data = await data.fetchall()
                emb = discord.Embed(description = f"```py\n{data}\n```", colour = self.bot.colour)
                await ctx.send(embed = emb)

            await db.commit()

        await ctx.message.add_reaction("<a:check:726040431539912744>")
    
def setup(bot):
    bot.add_cog(Owner(bot))