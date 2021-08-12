import discord, traceback, io, textwrap, sys, copy, subprocess, asyncio, os, aiohttp, utils, config
from discord.ext import commands
from contextlib import redirect_stdout

class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""

        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    @commands.command()
    @commands.is_owner()
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
            await ctx.message.add_reaction(config.emojis.fail)
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction(config.emojis.check)
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(value)
            else:
                self._last_result = ret
                await ctx.send(f'{value}{ret}')

    @commands.group(invoke_without_command = True, aliases = ["sql", "db"])
    @commands.is_owner()
    async def sqlite(self, ctx, *, command):
        "run a sqlite command"

        command = eval(f"f'{command}'")
        data = await self.bot.db.execute(command)
        if command.lower().startswith("select"):
            settings = await utils.get_settings(self.bot.db, ctx.guild.id)
            data = await data.fetchall()
            emb = discord.Embed(description=f"```py\n{data}\n```", colour=settings["colour"])
            await ctx.send(embed = emb)

        await db.commit()
        await ctx.message.add_reaction(config.emojis.check)

    @commands.command(name="add-cookies", aliases=["addcookies"])
    @commands.is_owner()
    async def add_cookies(self, ctx, member: discord.Member, cookies):
        "Add cookies to a member"

        if not cookies.isdigit():
            return await utils.error(ctx, 'not a number')

        cookies = int(cookies)

        if cookies <= 0:
            return await utils.error(ctx, 'not a number higher than `0`')

        await utils.add_cookies(self.bot.db, member.id, ctx.guild.id, cookies)
        await ctx.message.add_reaction(config.emojis.check)

    @commands.command(name="remove-cookies", aliases=["removecookies"])
    @commands.is_owner()
    async def remove_cookies(self, ctx, member: discord.Member, cookies):
        "Remove cookies from a member"

        if not cookies.isdigit():
            return await utils.error(ctx, 'not a number')

        cookies = int(cookies)

        if cookies <= 0:
            return await utils.error(ctx, 'not a number higher than `0`')

        await utils.remove_cookies(self.bot.db, member.id, ctx.guild.id, cookies)
        await ctx.message.add_reaction(config.emojis.check)

def setup(bot):
    bot.add_cog(Owner(bot))
