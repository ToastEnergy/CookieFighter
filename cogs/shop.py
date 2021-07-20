import discord, utils, time, config
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="shop", description="Buy roles with cookies")
    async def shop_slash(self, ctx: SlashContext):
        "Check bot latency and response"

        await self.shop(ctx)

    @commands.command()
    async def shop(self, ctx):
        "Buy roles with cookies"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        roles = await utils.get_roles(self.bot.db, ctx.guild)

        if not roles:
            emb = discord.Embed(title="Cookie Shop!", description=f"*The shop for {ctx.guild.name} is empty*", colour=settings["colour"])
            if ctx.author.guild_permissions.manage_guild:
                emb.description += f"\n\nUse `{settings['prefix']}additem <role> <cookies>` to add an item to the shop."

            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        emb = discord.Embed(title="Cookie Shop!", description=f"Use `{settings['prefix']}buy <item number>` to buy something.\n\n", colour=settings['colour'])
        count = 0
        for role in roles:
            count += 1
            emb.description += f"`{count}.` {role.mention} **{roles[role]} {settings['emoji']}**\n"

        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def additem(self, ctx, role: discord.Role, cookies):
        "Add an item to the shop"

        roles = await utils.get_roles(self.bot.db, ctx.guild)
        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        try:
            cookies = int(cookies)
        except:
            emb = discord.Embed(description=f"{config.emojis.fail} | Please specify a number", colour=discord.Colour.red())
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        if cookies < 1:
            emb = discord.Embed(description=f"{config.emojis.fail} | Please specify a number higher than `0`", colour=discord.Colour.red())
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        if roles and role.id in [r.id for r in roles]:
            await self.bot.db.execute("UPDATE shop SET cookies=? WHERE role=?", (cookies, role.id,))

        else:
            await self.bot.db.execute("INSERT INTO SHOP (guild, role, cookies) VALUES (?, ?, ?)", (ctx.guild.id, role.id, cookies))
        await self.bot.db.commit()

        emb = discord.Embed(description=f"{config.emojis.check} | Item added to the shop", colour=settings["colour"])
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Shop(bot))
