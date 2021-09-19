import discord, config, utils, asyncio, time, random
from discord.ext import commands

class PartyView(discord.ui.View):
    def __init__(self, ctx, embed):
        self.ctx = ctx
        self.embed = embed
        self.users = list()
        super().__init__(timeout=10)

    async def interaction_check(self, interaction):
        if interaction.user.bot:
            await interaction.response.send_message("this isn't for u", ephemeral=True)
            return False
        return True

    async def update_embed(self, interaction):
        slashn = "\n"
        new_emb = discord.Embed(title=self.embed.title, colour=self.embed.colour)
        new_emb.add_field(name="• **__How does this work__**", value="> I'll chose a random emoji, you have to be fast to find the emoji and send it before the others", inline=False)
        new_emb.add_field(name="• **__Joined Members__**", value=f"> • {f'{slashn}> • '.join([f'**{str(u)}**' for u in self.users]) if len(self.users) > 0 else '''*No one's here...*'''}", inline=False)
        new_emb.set_footer(text="Party will start in 10 seconds")

        await interaction.response.edit_message(content=None, embed=new_emb)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.blurple, emoji=config.emojis.check)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):

        if interaction.user in self.users:
            self.users.remove(interaction.user)
        else:
            self.users.append(interaction.user)

        await self.update_embed(interaction)

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["c"])
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def cookie(self, ctx):
        "Catch the cookie!"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(description=f"```\n{config.bot.countdown[0]}\n```", colour=settings["colour"])
        emb.set_footer(text="First one to take the cookie wins 🍪!")
        try: msg = await ctx.reply(embed=emb, mention_author=False)
        except:  msg = await ctx.send(embed=emb)
        await utils.countdown(msg, emb)

        def check(reaction, user):
            print(str(reaction.emoji))
            print(settings['emoji'])
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
        try: await msg.clear_reactions()
        except: pass

    @commands.command(aliases=["m"])
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def milk(self, ctx):
        "Drink the milk!"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(description=f"```\n{config.bot.countdown[0]}\n```", colour=settings["colour"])
        emb.set_footer(text="First one to drink the milk wins 🥛!")
        try: msg = await ctx.reply(embed=emb, mention_author=False)
        except:  msg = await ctx.send(embed=emb)
        await utils.countdown(msg, emb)

        def check(reaction, user):
            return str(reaction.emoji) == "🥛" and not user.bot

        emb = discord.Embed(description = f"First to **drink** the milk 🥛 wins!", colour=settings['colour'])
        await msg.edit(embed=emb)
        start = time.perf_counter()
        await msg.add_reaction("🥛")

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=settings["timeout"])
        except asyncio.TimeoutError:
            emb.description = ":clock: | Timeout!"
            await msg.clear_reactions()
            return await msg.edit(embed=emb)

        end = time.perf_counter()
        duration = end - start

        await utils.add_cookie(self.bot.db, user.id, ctx.guild.id, duration, "milk")
        emb.description = f"**{str(user)}** won in `{duration:.2f}` seconds!"
        await msg.edit(embed=emb)
        await utils.check_other_users(user, msg, emb)
        try: await msg.clear_reactions()
        except: pass

    @commands.command(name="type", aliases=["t"])
    @commands.max_concurrency(1, commands.BucketType.guild)
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

    @commands.command(aliases=["coin", "flip"])
    async def bet(self, ctx, cookies):
        "Bet some cookies!"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        av_cookies = await utils.get_cookies(self.bot.db, ctx.author.id, ctx.guild.id)

        if not cookies.isdigit():
            return await utils.error(ctx, "Please specify a number")

        cookies = int(cookies)

        if cookies <= 0:
            return await utils.error(ctx, "Please specify a number higher than `0`")

        if av_cookies < cookies:
            return await utils.error(ctx, f"You don't have `{cookies}` {'cookie' if cookies == 1 else 'cookies'}")

        won = random.choice([True, False])
        if won:
            await utils.add_cookies(self.bot.db, ctx.author.id, ctx.guild.id, cookies)
            emb = discord.Embed(title="You won!", description=f"I added you `{cookies}` {'cookie' if cookies == 1 else 'cookies'}", colour=settings["colour"])
        else:
            await utils.remove_cookies(self.bot.db, ctx.author.id, ctx.guild.id, cookies)
            emb = discord.Embed(title="You lost!", description=f"I removed you `{cookies}` {'cookie' if cookies == 1 else 'cookies'}", colour=settings["colour"])

        await ctx.reply(embed=emb, mention_author=False)

    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.command()
    async def party(self, ctx):
        "Who's ready to party?"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(title=f"Party {config.emojis.tada}", colour=settings["colour"])
        emb.add_field(name="• **__How does this work__**", value="> I'll chose a random emoji, you have to be fast to find the emoji and send it before the others", inline=False)
        emb.add_field(name="• **__Joined Members__**", value="> *No one joined yet, use the button below to join*", inline=False)
        emb.set_footer(text="Party will start in 10 seconds")
        
        view = PartyView(ctx=ctx, embed=emb)
        msg = await ctx.reply(embed=emb, view=view, mention_author=False)

        await asyncio.sleep(10)

        if len(view.users) == 0:
            emb = discord.Embed(description="*No one joined the party*", colour=settings['colour'])
            return await msg.edit(embed=emb, view=None)

        elif len(view.users) == 1:
            emb = discord.Embed(description="The party can't start with `1` member", colour=settings['colour'])
            return await msg.edit(embed=emb, view=None)

        emoji = random.choice(config.emojis.discord)
        emb = discord.Embed(title=emb.title, description=f"First one to send the emoji {emoji} wins", colour=emb.colour)
        await msg.edit(content=None, embed=emb, view=None)

        def check_message(m):
            return m.author.id in [m_.id for m_ in view.users] and m.content.lower() == emoji

        start = time.perf_counter()
        try: message = await self.bot.wait_for("message", check=check_message, timeout=settings['timeout'])
        except asyncio.TimeoutError:
            error = discord.Embed(description=":clock: | Timeout!", colour=settings['colour'])
            return await msg.edit(embed=emb, content=None, components=[])

        end = time.perf_counter()
        duration = end - start

        await message.add_reaction(config.emojis.tada)
        await utils.add_cookie(self.bot.db, message.author.id, ctx.guild.id, duration, 'party')
        emb.description = f"**{str(message.author)}** won in `{duration:.2f}` seconds!"
        await msg.edit(content=None, embed=emb, view=None)

    @commands.command(aliases=["send", "pay"])
    async def gift(self, ctx, member: discord.Member, cookies):
        "Gift some cookies to a member"

        if member.bot:
            return await utils.error(ctx, "You can't send cookies to a bot")

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        av_cookies = await utils.get_cookies(self.bot.db, ctx.author.id, ctx.guild.id)

        if not cookies.isdigit():
            return await utils.error(ctx, "Please specify a number")

        cookies = int(cookies)

        if cookies <= 0:
            return await utils.error(ctx, "Please specify a number higher than `0`")

        if av_cookies < cookies:
            return await utils.error(ctx, f"You don't have `{cookies}` {'cookie' if cookies == 1 else 'cookies'}")

        await utils.remove_cookies(self.bot.db, ctx.author.id, ctx.guild.id, cookies)
        await utils.add_cookies(self.bot.db, member.id, ctx.guild.id, cookies)

        await utils.success(ctx, f"Transfered `{cookies}` {'cookie' if cookies == 1 else 'cookies'} from {ctx.author.mention} to {member.mention}")

    @commands.command(name="add-cookies", aliases=["addcookies"])
    @commands.has_permissions(manage_guild=True)
    async def add_cookies(self, ctx, member: discord.Member, cookies):
        "Add cookies to a member"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        if not cookies.isdigit():
            return await utils.error(ctx, 'Please specify a number')

        cookies = int(cookies)

        if cookies > 9223372036854775807:
            return await utils.error(ctx, "You can't add more than `9223372036854775807` at time")

        if cookies <= 0:
            return await utils.error(ctx, 'Please specify a number higher than `0`')

        await utils.add_cookies(self.bot.db, member.id, ctx.guild.id, cookies)
        await ctx.message.add_reaction(config.emojis.check)

    @commands.command(name="remove-cookies", aliases=["removecookies"])
    @commands.has_permissions(manage_guild=True)
    async def remove_cookies(self, ctx, member: discord.Member, cookies):
        "Remove cookies from a member"

        if not cookies.isdigit():
            return await utils.error(ctx, 'Please specify a number')

        cookies = int(cookies)

        if cookies <= 0:
            return await utils.error(ctx, 'Please specify a number higher than `0`')

        await utils.remove_cookies(self.bot.db, member.id, ctx.guild.id, cookies)
        await ctx.message.add_reaction(config.emojis.check)

def setup(bot):
    bot.add_cog(Cookies(bot))
