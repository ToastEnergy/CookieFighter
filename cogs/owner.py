import discord
from discord.ext import commands
import traceback
import io
from contextlib import redirect_stdout
import textwrap
import sys
import copy
import subprocess
import asyncio
import cookies
import aiosqlite

class Owner(commands.Cog, command_attrs=dict(hidden=True)):

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
    
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

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

    @commands.command(name='set')
    async def _set(self, ctx):
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
    async def reload(self, ctx, extension):
        
        emb = discord.Embed(title = 'Loading...', colour = self.bot.colour)
        emb1 = discord.Embed(title = f'Reloaded {extension}!', colour = self.bot.colour)
        msg = await ctx.send(embed = emb)
        await asyncio.sleep(0.5)
        
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
    
def setup(bot):
    bot.add_cog(Owner(bot))