import discord, config, utils, asyncio, time
from discord.ext import commands

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx):
        "Who's the best?"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        users = await utils.get_users(self.bot.db, ctx.guild.id)

        emb = discord.Embed(description="", colour=settings["colour"])
        emb.set_author(name=f"{ctx.guild.name}'s Leaderboard", icon_url=str(ctx.guild.icon_url_as(static_format="png", size=1024)))

        if not users:
            emb.description = "*no one's here*"
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        lb = sorted(users, key=lambda x : users[x], reverse=True)
        count = 0
        for x in lb:
            count += 1
            if count > 10:
                break
            u = self.bot.get_user(x)
            if not u:
                u = await self.bot.fetch_user(x)
            emb.description += f"**{count}.** `{str(u)}` - **{users[x]}** {settings['emoji']}\n"

        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command(aliases=["info", "stats", "stat", "bal", "balance"])
    async def cookies(self, ctx, member: discord.Member=None):
        "Get how many cookies a member has"

        member = member or ctx.author

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        cookies = await utils.get_cookies(self.bot.db, member.id, ctx.guild.id)
        emb = discord.Embed(description=f"**{cookies}** Cookies {settings['emoji']}", colour=settings['colour'])
        emb.set_author(name=str(member), icon_url=str(member.avatar_url_as(static_format="png", size=1024)))
        await ctx.reply(embed=emb, mention_author=False)

    @commands.command(name="reset-leaderboard", aliases=["resetleaderboard"])
    @commands.has_permissions(manage_guild=True)
    async def reset_leaderboard(self, ctx):
        "Reset the leaderboard, everyone in the server will lose their cookies"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(description="You are going to reset the leaderboard, are you sure?", colour=settings['colour'])
        try: msg = await ctx.reply(embed=emb, mention_author=False)
        except: msg = await ctx.send(embed=emb)

        [await msg.add_reaction(r) for r in [config.emojis.check, config.emojis.fail]]

        def check(reaction, user):
            return str(reaction.emoji) in [config.emojis.check, config.emojis.fail] and user.id == ctx.author.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=120)
        except asyncio.TimeoutError:
            emb = discord.Embed(description=f"{config.emojis.fail} | Timeout!", colour=discord.Colour.red())
            return await msg.edit(content=None, embed=emb)

        await utils.reset_leaderboard(self.bot.db, ctx.guild.id)

        emb = discord.Embed(description=f"The leaderboard has been reset", colour=settings['colour'])
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command()
    async def halloffame(self, ctx):
        "The Cookie Fighter Hall of Fame, from the old version, when cookies were global"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        users = await utils.halloffame(self.bot.db)
        emb = discord.Embed(description="", colour=settings["colour"])
        emb.set_author(name="Hall of Fame", icon_url=self.bot.user.avatar_url_as(static_format="png"))

        count = 1
        for user in users:
            u = self.bot.get_user(user)
            if not u:
                try:
                    u = await self.bot.fetch_user(user)
                except discord.errors.NotFound:
                    pass
            if u:
                emb.description += f"**{count}.** `{str(u)}` - **{users[user]} {settings['emoji']}**\n"
                count += 1

def setup(bot):
    bot.add_cog(Stats(bot))
