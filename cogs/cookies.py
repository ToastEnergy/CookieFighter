import discord, config, utils, asyncio, time
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="cookie", description="Catch the cookie!")
    async def cookie_slash(self, ctx: SlashContext):
        "Catch the cookie!"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        emb = discord.Embed(description=f"```\n{config.bot.countdown[0]}\n```", colour=settings["colour"])
        emb.set_footer(text="First one to take the cookie wins 🍪!")
        msg = await ctx.send(embeds=[emb])
        await utils.countdown(msg, emb)

        def check(reaction, user):
            return str(reaction.emoji) == settings["emoji"] and not user.bot

        emb = discord.Embed(description = f"First to catch the cookie {settings['emoji']} wins!", colour=settings['colour'])
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

        await utils.add_cookies(self.bot.db, self.bot.db_cache, ctx.guild.id, user.id, 1, duration)
        emb.description = f"**{str(user)}** won in `{duration:.2f}` seconds!"
        await msg.edit(embed=emb)
        await utils.check_other_users(user, msg, emb)

    @commands.command(aliases=["c"])
    @commands.guild_only()
    async def cookie(self, ctx):
        "Catch the cookie!"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        emb = discord.Embed(description=f"```\n{config.bot.countdown[0]}\n```", colour=settings["colour"])
        emb.set_footer(text="First one to take the cookie wins 🍪!")
        msg = await ctx.reply(embed=emb, mention_author=False)
        await utils.countdown(msg, emb)

        def check(reaction, user):
            return str(reaction.emoji) == settings["emoji"] and not user.bot

        emb = discord.Embed(description = f"First to catch the cookie {settings['emoji']} wins!", colour=settings['colour'])
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

        await utils.add_cookies(self.bot.db, self.bot.db_cache, ctx.guild.id, user.id, 1, duration)
        emb.description = f"**{str(user)}** won in `{duration:.2f}` seconds!"
        await msg.edit(embed=emb)
        await utils.check_other_users(user, msg, emb)

    @cog_ext.cog_slash(name="leaderboard", description="Who's the best?")
    async def leaderboard_slash(self, ctx: SlashContext):
        "Who's the best?"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        users = self.bot.db_cache["guilds"][ctx.guild.id]["users"]
        lb = sorted(users, key=lambda x : users[x], reverse=True)

        emb = discord.Embed(description="", colour=settings["colour"])
        emb.set_author(name=f"{ctx.guild.name}'s Leaderboard", icon_url=str(ctx.guild.icon_url_as(static_format="png")))
        count = 0
        for x in lb:
            count += 1
            if count > 10:
                break
            u = self.bot.get_user(x)
            if not u:
                u = await self.bot.fetch_user(x)
            emb.description += f"**{count}.** `{str(u)}` - **{users[x]}** {settings['emoji']}\n"
        await ctx.send(embed=emb)

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx):
        "Who's the best?"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        users = self.bot.db_cache["guilds"][ctx.guild.id]["users"]
        lb = sorted(users, key=lambda x : users[x], reverse=True)

        emb = discord.Embed(description="", colour=settings["colour"])
        emb.set_author(name=f"{ctx.guild.name}'s Leaderboard", icon_url=str(ctx.guild.icon_url_as(static_format="png")))
        count = 0
        for x in lb:
            count += 1
            if count > 10:
                break
            u = self.bot.get_user(x)
            if not u:
                u = await self.bot.fetch_user(x)
            emb.description += f"**{count}.** `{str(u)}` - **{users[x]}** {settings['emoji']}\n"
        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Cookies(bot))
