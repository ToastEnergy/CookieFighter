import discord, utils, config, asyncio
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="settings", description="Check server settings")
    async def settings_slash(self, ctx: SlashContext):
        await self.settings(ctx)

    @commands.command()
    @commands.guild_only()
    async def settings(self, ctx):
        "Check server settings"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emoji = settings["emoji"] if settings["emoji"] not in config.emojis.default else " / ".join(config.emojis.default)
        emb = discord.Embed(description=f"• **Emoji:** {emoji}\n• **Colour:** `{str(discord.Colour(settings['colour']))}`\n• **Timeout:** `{settings['timeout']}`", colour=settings["colour"])
        emb.set_author(name=f"{ctx.guild.name} settings", icon_url=str(ctx.guild.icon_url_as(static_format="png")))
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command(aliases=["editsetting"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def editsettings(self, ctx, option, value):
        "Edit server settings"

        option = option.lower().replace("color", "colour")

        if option not in ["colour", "emoji", "timeout", "prefix"]:
            emb = discord.Embed(title="Invalid option!", description="Choose from `colour` `emoji` `timeout` `prefix`", colour=discord.Colour.red())
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        if option == "colour":
            value = f"0x{value[1:]}"
            value = int(value, 16)

        elif option == "timeout":
            try: value = int(value)
            except:
                emb = discord.Embed(title="Invalid Timeout!", description="Please specify the amount of seconds.", colour=discord.Colour.red())
                try: await ctx.reply(embed=emb, mention_author=False)
                except: await ctx.send(embed=emb)
                return

            if value > 300 or value < 1:
                emb = discord.Embed(title="Invalid Timeout!", description="Timeout must be between `1` and `300`", colour=discord.Colour.red())
                try: await ctx.reply(embed=emb, mention_author=False)
                except: await ctx.send(embed=emb)
                return

            value = round(value)

        await utils.get_settings(self.bot.db, ctx.guild.id) # generate column if none
        await self.bot.db.execute(f"UPDATE settings SET {option}=? WHERE guild=?", (value, ctx.guild.id))
        await self.bot.db.commit()
        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        if option == "colour":
            value = str(discord.Colour(value))

        emb = discord.Embed(description=f"{config.emojis.check} | `{option}` updated to {value if option == 'emoji' else f'`{value}`'}", colour=settings["colour"])
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command(aliases=["reset"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def resetsettings(self, ctx):
        "Reset server settings"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(description="You are going to reset guild settings, are you sure?", colour=settings['colour'])
        try: msg = await ctx.reply(embed=emb, mention_author=False)
        except: msg = await ctx.send(embed=emb)

        [await msg.add_reaction(r) for r in [config.emojis.check, config.emojis.fail]]

        def check(reaction, user):
            return str(reaction.emoji) in [config.emojis.check, config.emojis.fail] and user.id == ctx.author.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=120)
        except asyncio.TimeoutError:
            emb = discord.Embed(description=f"{config.emojis.fail} | Timeout!", colour=discord.Colour.red())
            try: msg = await ctx.reply(embed=emb, mention_author=False)
            except: msg = await ctx.send(embed=emb)
            return

        if str(reaction.emoji) == config.emojis.fail:
            emb = discord.Embed(description="Ok, I won't reset anything.", colour=settings['colour'])
            try: msg = await ctx.reply(embed=emb, mention_author=False)
            except: msg = await ctx.send(embed=emb)
            return

        await self.bot.db.execute("DELETE FROM settings WHERE guild=?", (ctx.guild.id,))
        await self.bot.db.commit()

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emb = discord.Embed(description="Done, everything has been reset.", colour=settings['colour'])
        try: msg = await ctx.reply(embed=emb, mention_author=False)
        except: msg = await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Settings(bot))
