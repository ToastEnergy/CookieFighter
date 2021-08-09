import discord, utils, time, config
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def empty_shop(self, ctx, settings):
        emb = discord.Embed(title="Cookies Shop!", description=f"*The shop for {ctx.guild.name} is empty*", colour=settings["colour"])
        if ctx.author.guild_permissions.manage_guild:
            emb.description += f"\n\nUse `{settings['prefix']}additem <role> <cookies>` to add an item to the shop."

        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    async def invalid_role_id(self, ctx):
        emb = discord.Embed(description=f"{config.emojis.fail} | Invalid `role id`!", colour=discord.Colour.red())
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

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
            return await self.empty_shop(ctx, settings)

        emb = discord.Embed(title="Cookies Shop!", description=f"Use `{settings['prefix']}buy <item number>` to buy something.\n\n", colour=settings['colour'])
        count = 0
        for role in roles:
            count += 1
            emb.description += f"`{count}.` {role.mention} **{roles[role]} {settings['emoji']}**\n"

        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @cog_ext.cog_slash(name="add-item", description="Add an item to the shop", options=[
        create_option(
            name="role",
            required=True,
            type=8,
            description="The role to add to the shop"
        ),
        create_option(
            name="cookies",
            value=4,
            required=True,
            description="Number of cookies required to buy the role"
        )
    ])
    @commands.has_permissions(manage_guild=True)
    async def add_item_slash(self, ctx: SlashContext, role, cookies):
        "Add an item to the shop"

        await self.add_item(ctx, role, cookies)

    @commands.command(name="add-item", aliases=["additem"])
    @commands.has_permissions(manage_guild=True)
    async def add_item(self, ctx, role: discord.Role, cookies):
        "Add an item to the shop"
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

        await utils.add_to_shop(self.bot.db, ctx.guild, role.id, cookies)
        emb = discord.Embed(description=f"{config.emojis.check} | Item added to the shop", colour=settings["colour"])
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @cog_ext.cog_slash(name="remove-item", description="Remove an item from the shop", options=[
        create_option(
            name="role_id",
            required=True,
            type=4,
            description="The id of the role to remove from the shop"
        )
    ])
    @commands.has_permissions(manage_guild=True)
    async def remove_item_slash(self, ctx: SlashContext, role_id):
        "Remove an item from the shop"

        await self.remove_item(ctx, role_id)

    @commands.command(name="remove-item", aliases=["removeitem"])
    @commands.has_permissions(manage_guild=True)
    async def remove_item(self, ctx, role_id):
        "Add an item to the shop"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        roles = await utils.get_roles(self.bot.db, ctx.guild)

        try: role_id = int(role_id)
        except: return await self.invalid_role_id(ctx)

        try: role = list(roles.keys())[role_id-1]
        except: return await self.invalid_role_id(ctx)

        await utils.remove_from_shop(self.bot.db, ctx.guild.id, role.id)

        emb = discord.Embed(description=f"{config.emojis.check} | Item removed from the shop", colour=settings["colour"])
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @cog_ext.cog_slash(name="buy", description="Buy an item from the shop", options=[
        create_option(
            name="role_id",
            required=True,
            type=4,
            description="The id of the role to buy"
        )
    ])
    async def buy_slash(self, ctx: SlashContext, role_id):
        "Buy an item from the shop"

        await self.buy(ctx, role_id)

    @commands.command()
    async def buy(self, ctx, role_id):
        "Buy something from the shop"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        roles = await utils.get_roles(self.bot.db, ctx.guild)

        if not roles:
            return await self.empty_shop(ctx, settings)

        try: role_id = int(role_id)
        except: return await self.invalid_role_id(ctx)

        try: role = list(roles.keys())[role_id-1]
        except: return await self.invalid_role_id(ctx)

        inv = await utils.get_inventory(self.bot.db, ctx.author.id, ctx.guild.id)
        if inv:
            if role.id in inv:
                emb = discord.Embed(description=f"{config.emojis.fail} | You already have that item!", colour=discord.Colour.red())
                try: await ctx.reply(embed=emb, mention_author=False)
                except: await ctx.send(embed=emb)
                return

        cookies = roles[role]
        av_cookies = await utils.get_cookies(self.bot.db, ctx.author.id, ctx.guild.id)

        if av_cookies < cookies:
            emb = discord.Embed(description=f"{config.emojis.fail} | You don't have enough cookies to buy this item", colour=discord.Colour.red())
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        try: await ctx.author.add_roles(role)
        except:
            emb = discord.Embed(description=f"{config.emojis.fail} | It looks like I don't have enough permissions to add you that role...", colour=discord.Colour.red())
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        await utils.remove_cookies(self.bot.db, ctx.author.id, ctx.guild.id, cookies)
        await utils.update_inventory(self.bot.db, ctx.author.id, ctx.guild.id, role.id)
        emb = discord.Embed(description=f"{config.emojis.check} | You have successfully bought the role {role.mention}", colour=settings["colour"])

        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command()
    async def sell(self, ctx, role_id):
        "Sell an item (it must be in the shop)"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        try: role_id = int(role_id)
        except: return await self.invalid_role_id(ctx)

        roles = await utils.get_roles(self.bot.db, ctx.guild)

        try: role = list(roles.keys())[role_id-1]
        except: return await self.invalid_role_id(ctx)

        inv = await utils.get_inventory(self.bot.db, ctx.author.id, ctx.guild.id)
        if not inv or role.id not in inv:
            emb = discord.Embed(description=f"{config.emojis.fail} | That role isn't in your inventory!", colour=discord.Colour.red())
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        cookies = roles[role]
        await utils.remove_from_inventory(self.bot.db, ctx.author.id, ctx.guild.id, role.id)
        await utils.add_cookies(self.bot.db, ctx.author.id, ctx.guild.id, cookies)

        emb = discord.Embed(description=f"{config.emojis.check} | You have successfully sold the role {role.mention}", colour=settings['colour'])
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @cog_ext.cog_slash(name="inventory", description="Check the inventory of a member", options=[create_option(name="member", description="The member to check the inventory of", type=6, required=False)])
    async def inventory_slash(self, ctx: SlashContext, member=None):
        await self.inventory(ctx, member)

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx, *, member: discord.Member=None):
        "Check the inventory of a member"

        member = member or ctx.author
        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        inv = await utils.get_inventory(self.bot.db, member.id, ctx.guild.id)

        emb = discord.Embed(colour=settings["colour"])
        emb.set_author(name=str(member), icon_url=str(member.avatar_url_as(static_format="png")))

        if not inv:
            emb.description = "*Nothing to see here...*"
        else:
            emb.description = ""
            for role_id in inv:
                role = ctx.guild.get_role(role_id)
                if role:
                    emb.description += f"• {role.mention}\n"

        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Shop(bot))
