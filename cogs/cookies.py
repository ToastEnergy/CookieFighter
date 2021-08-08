import discord, config, utils, asyncio, time, random
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
import discord_components as dc

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
        try: await msg.clear_reactions()
        except: pass

    @cog_ext.cog_slash(name="milk", description="Drink the milk!")
    async def milk_slash(self, ctx: SlashContext):
        "Drink the milk!"

        await self.milk(ctx)

    @commands.command(aliases=["m"])
    @commands.guild_only()
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

    @commands.command(aliases=["coin", "flip"])
    async def bet(self, ctx, cookies):
        "Bet come cookies!"

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

        await utils.send_embed(ctx, emb)

    @commands.command()
    async def party(self, ctx):
        "Who's ready to party?"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(title=f"Party {config.emojis.tada}", colour=settings["colour"])
        emb.add_field(name="• **__How does this work__**", value="> I'll chose a random emoji, you have to be fast to find the emoji and send it before the others", inline=False)
        emb.add_field(name="• **__Joined Members__**", value="> *No one joined yet, use the button below to join*", inline=False)
        emb.set_footer(text="Party will start in 10 seconds")
        components = [dc.Button(label="Join", style=dc.ButtonStyle.blue, emoji=discord.utils.get(self.bot.emojis, id=int(config.emojis.check.split(":")[2][:-1])))]
        msg = await utils.send_embed(ctx, emb, components=components)
        members = list( )
        slashn = "\n"

        def check(i):
            if i.message.id == msg.id and not i.user.bot and i.component.label == "Join":
                members.append(i.user)
                new_emb = discord.Embed(title=emb.title, colour=emb.colour)
                new_emb.add_field(name="• **__How does this work__**", value="> I'll chose a random emoji, you have to be fast to find the emoji and send it before the others", inline=False)
                new_emb.add_field(name="• **__Joined Members__**", value=f"> • {f'{slashn}• '.join([f'**{str(m)}**' for m in members])}", inline=False)
                new_emb.set_footer(text="Party will start in 10 seconds")
                self.bot.loop.create_task(msg.edit(embed=new_emb, content=None, components=components))
                self.bot.loop.create_task(i.respond(embed=discord.Embed(description=f"{config.emojis.check} | You joined the party", colour=settings['colour'])))
            return False

        try: interaction = await self.bot.wait_for("button_click", check=check, timeout=10)
        except asyncio.TimeoutError: pass

        if len(members) == 0:
            emb = discord.Embed(description="*No one joined the party*", colour=settings['colour'])
            return await msg.edit(embed=emb)

        emoji = random.choice(config.emojis.discord)
        emb = discord.Embed(title=emb.title, description=f"First one to send the emoji {emoji} wins", colour=emb.colour)
        await msg.edit(content=None, embed=emb, components=None)

        def check_message(m):
            return m.author.id in [m_.id for m_ in members] and m.content.lower() == emoji

        start = time.perf_counter()
        try: message = await self.bot.wait_for("message", check=check_message, timeout=settings['timeout'])
        except asyncio.TimeoutError:
            error = discord.Embed(description=":clock: | Timeout!", colour=settings['colour'])
            return await msg.edit(embed=emb, content=None)

        end = time.perf_counter()
        duration = end - start

        await utils.add_cookie(self.bot.db, message.author.id, ctx.guild.id, duration, 'party')
        emb.description = f"**{str(message.author)}** won in `{duration:.2f}` seconds!"
        await msg.edit(embed=emb)

def setup(bot):
    bot.add_cog(Cookies(bot))
