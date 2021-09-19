import discord, utils, time, config
from discord.ext import commands

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
        emb = discord.Embed(description=f"{config.emojis.fail} | Invalid `role id`!\nYou can find the role ID before the role name in the `shop` command", colour=discord.Colour.red())
        await ctx.reply(embed=emb, mention_author=False)

    @commands.command()
    async def shop(self, ctx):
        "Buy roles with cookies"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        roles = await utils.get_roles(self.bot.db, ctx.guild)
        cookies = await utils.get_cookies(self.bot.db, ctx.author.id, ctx.guild.id)

        if not roles:
            return await self.empty_shop(ctx, settings)

        emb = discord.Embed(title="Cookies Shop!", description=f"__Your cookies:__ `{cookies}` {settings['emoji']}\n\nUse `{settings['prefix']}buy <item number>` to buy something.\n\n", colour=settings['colour'])
        count = 0
        for role in roles:
            count += 1
            emb.description += f"`{count}.` {role.mention} **{roles[role]} {settings['emoji']}**\n"

        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

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

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx, *, member: discord.Member=None):
        "Check the inventory of a member"

        member = member or ctx.author
        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        inv = await utils.get_inventory(self.bot.db, member.id, ctx.guild.id)

        emb = discord.Embed(colour=settings["colour"])
        emb.set_author(name=str(member), icon_url=str(member.avatar.replace(static_format="png", size=1024)))

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
