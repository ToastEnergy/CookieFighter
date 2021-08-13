import discord, utils, config, asyncio
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def settings(self, ctx):
        "Check server settings"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        emoji = settings["emoji"] if settings["emoji"] not in config.emojis.default else " / ".join(config.emojis.default)
        emb = discord.Embed(description=f"• **Emoji:** {emoji}\n• **Colour:** `{str(discord.Colour(settings['colour']))}`\n• **Timeout:** `{settings['timeout']}`\n• **Spawn:** `{'enabled' if settings['spawn'] else 'disabled'}`\n• **Spawn Rate:** `{settings['spawnrate']}%`", colour=settings["colour"])
        emb.set_author(name=f"{ctx.guild.name} settings", icon_url=str(ctx.guild.icon_url_as(static_format="png")))
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command(name="edit-settings", aliases=["editsetting", "edit-setting", "editsettings"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def edit_settings(self, ctx, option, value):
        "Edit server settings"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        option = option.lower().replace("color", "colour").replace("spawn-rate", "spawnrate", )

        if option not in ["colour", "emoji", "timeout", "prefix", "spawn", "spawnrate"]:
            emb = discord.Embed(title="Invalid option!", description="Choose from `colour` `emoji` `timeout` `prefix` `spawn` `spawnrate`", colour=discord.Colour.red())
            try: await ctx.reply(embed=emb, mention_author=False)
            except: await ctx.send(embed=emb)
            return

        if option == "colour":
            if not value.startswith("#"):
                emb = discord.Embed(title="Invalid color!", description="Please specify a **HEX Color** like `#ffe930`, you can pick one from [here](https://htmlcolorcodes.com/).", colour=discord.Colour.red())
                try: await ctx.reply(embed=emb, mention_author=False)
                except: await ctx.send(embed=emb)
                return
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

        elif option == "emoji":
            emb = discord.Embed(description=f"{config.emojis.loading} |  This message will be used to test the emoji", colour=settings["colour"])
            try: msg = await ctx.reply(embed=emb, mention_author=False)
            except: msg = await ctx.send(embed=emb)

            try: await msg.add_reaction(value)
            except:
                emb.colour = discord.Colour.red()
                emb.description = f"{config.emojis.fail} | Invalid emoji!"
                return await msg.edit(embed=emb)

            await msg.remove_reaction(value, ctx.guild.me)
            await self.bot.db.execute(f"UPDATE settings SET {option}=? WHERE guild=?", (value, ctx.guild.id))
            await self.bot.db.commit()
            settings = await utils.get_settings(self.bot.db, ctx.guild.id)

            emb = discord.Embed(description=f"{config.emojis.check} | `{option}` updated to {value if option == 'emoji' else f'`{value}`'}", colour=settings["colour"])
            return await msg.edit(embed=emb)

        elif option == "spawn":
            if value.lower() in ["true", "yes", "enable", "enabled", "1"]:
                value = 1
            elif value.lower() in ["false", "no", "disable", "disabled", "0"]:
                value = 0
            else:
                return await utils.error(ctx, "Please specify `enabled` or `disabled`")

        elif option == "spawnrate":
            if "%" in value:
                if value[:-1].isdigit():
                    value = int(value[:-1])
            elif value.isdigit():
                value = int(value)
                if value not in range(1, 61):
                    return await utils.error(ctx, "Please specify a percentage between `1%` and `60%`")
            else:
                return await utils.error(ctx, "Please specify a percentage between `1%` and `60%`")

        await self.bot.db.execute(f"UPDATE settings SET {option}=? WHERE guild=?", (value, ctx.guild.id))
        await self.bot.db.commit()
        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        if option == "colour":
            value = str(discord.Colour(value))
        elif option == "spawn":
            value = 'enabled' if value == 1 else 'disabled'
        elif option == 'spawnrate':
            value = str(value) + "%"

        emb = discord.Embed(description=f"{config.emojis.check} | `{option}` updated to {value if option == 'emoji' else f'`{value}`'}", colour=settings["colour"])
        try: await ctx.reply(embed=emb, mention_author=False)
        except: await ctx.send(embed=emb)

    @commands.command(name="reset-settings", aliases=["resetsettings", "resetsetting", "reset-setting"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def reset_settings(self, ctx):
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
