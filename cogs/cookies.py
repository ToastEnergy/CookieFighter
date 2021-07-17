import discord, config, utils, asyncio, time
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="cookie", description="Catch the cookie!")
    async def cookie_slash(self, ctx: SlashContext):
        "Catch the cookie!"

        await self.cookie(ctx)

    @commands.command(aliases=["c"])
    @commands.guild_only()
    async def cookie(self, ctx):
        "Catch the cookie!"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(description=f"```\n{config.bot.countdown[0]}\n```", colour=settings["colour"])
        emb.set_footer(text="First one to take the cookie wins 🍪!")
        try: msg = await ctx.reply(embed=emb, mention_author=False)
        except:  msg = await ctx.send(embed=emb)
        await utils.countdown(msg, emb)

        def check(reaction, user):
            return str(reaction.emoji) == settings["emoji"] and not user.bot

        emb = discord.Embed(description = f"First to **catch** the cookie {settings['emoji']} wins!", colour=settings['colour'])
        await msg.edit(embed=emb)
        start = time.perf_counter()
        await msg.add_reaction(settings["emoji"])

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=settings["timeout"])
        except asyncio.TimeoutError:
            emb.description = ":clock: | Timeout!"
            await msg.clear_reactions()
            return await msg.edit(embed=emb)

        end = time.perf_counter()
        duration = end - start

        await utils.add_cookie(self.bot.db, user.id, ctx.guild.id, duration, "cookie")
        emb.description = f"**{str(user)}** won in `{duration:.2f}` seconds!"
        await msg.edit(embed=emb)
        await utils.check_other_users(user, msg, emb)

    @cog_ext.cog_slash(name="type", description="Send the cookie!")
    async def type_slash(self, ctx: SlashContext):
        "Send the cookie!"

        await self.type_(ctx)

    @commands.command(name="type", aliases=["t"])
    async def type_(self, ctx):
        "Send the cookie!"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(description=f"```\n{config.bot.countdown[0]}\n```", colour=settings["colour"])
        emb.set_footer(text="First one to send a cookie wins 🍪!")
        try: msg = await ctx.reply(embed=emb, mention_author=False)
        except: msg = await ctx.send(embed=emb)
        await utils.countdown(msg, emb)

        def check(m):
            return m.content in [config.emojis.default_cookie, settings["emoji"]] and m.channel.id == ctx.channel.id and not m.author.bot

        emb = discord.Embed(description = f"First to **send** a cookie {config.emojis.default_cookie} wins!", colour=settings['colour'])
        await msg.edit(embed=emb)
        start = time.perf_counter()

        try:
            m = await self.bot.wait_for("message", check=check, timeout=settings["timeout"])
        except asyncio.TimeoutError:
            emb.description = ":clock: | Timeout!"
            await msg.clear_reactions()
            return await msg.edit(embed=emb)

        end = time.perf_counter()
        duration = end - start

        await utils.add_cookie(self.bot.db, m.author.id, ctx.guild.id, duration, "type")
        emb.description = f"**{str(m.author)}** won in `{duration:.2f}` seconds!"
        await msg.edit(embed=emb)

def setup(bot):
    bot.add_cog(Cookies(bot))
