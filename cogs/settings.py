import discord, aiosqlite, cookies, random
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_converter = commands.EmojiConverter()

    @commands.group(aliases = ["setting"], invoke_without_command = True, hidden = True)
    @commands.is_owner()
    @commands.has_permissions(manage_messages = True)
    async def settings(self, ctx, option=None, value=None):
        "setup the bot for your guild"

        guild_options = await cookies.guild_settings(ctx.guild.id)

        if not option:
            embed_colour = int(guild_options["colour"])
            guild_options["colour"] = str(discord.Colour(int(guild_options["colour"])))

            if guild_options["emoji_default"] == True:
                guild_options["emoji"] = f"{self.bot.cookie} / {self.bot.oreo} / {self.bot.gocciola}"

            else:
                emoji = self.bot.get_emoji(guild_options["emoji"]) if self.bot.get_emoji(guild_options["emoji"]) else f"{self.bot.cookie} / {self.bot.oreo} / {self.bot.gocciola}"
                guild_options["emoji"] = str(emoji)

            prefix = await cookies.guild_prefix(ctx.guild.id)

            options = ["__colour__", "__emoji__", "__timeout__"]
            cookie = random.choice([self.bot.cookie, self.bot.gocciola, self.bot.oreo])
            a = f"\n{cookie} " # cuz \n raise an error with f-strings

            emb = discord.Embed(description=f"""**Available Settings**
            
{cookie} {a.join(options)}

**use** `{prefix}settings [setting name] [option]` to set-up the bot
**example**: `{prefix}settings colour #ffffff`

**Current Settings**

{cookie} __colour__: `{guild_options['colour']}`
{cookie} __emoji__: {guild_options['emoji']}
{cookie} __timeout__: `{guild_options['timeout']}s`
""", colour=embed_colour)
            emb.set_author(name=f"{ctx.guild.name} settings",icon_url=str(ctx.guild.icon_url_as(static_format="png")))

            return await ctx.send(embed=emb)

        else:
            await ctx.trigger_typing()

            option = str(option).lower()

            options = ["colour", "emoji", "timeout"]
            if option not in options:
                emb = discord.Embed(description=f"<a:fail:727212831782731796> | **{option}** is not a valid option", colour = int(guild_options["colour"]))
                return await ctx.send(embed=emb)

            if not value:
                emb = discord.Embed(description=f"<a:fail:727212831782731796> | please specify a value!", colour = int(guild_options["colour"]))
                return await ctx.send(embed=emb)

            if option == "color":
                option == "colour"

            if option == "colour":
                value = f"0x{value[1:]}"
                value = int(value, 16)
                # value = hex(value)

            elif option == "emoji":
                try:
                    emoji = await self.emoji_converter.convert(ctx, value)

                except commands.errors.EmojiNotFound:
                    emb = discord.Embed(description=f"<a:fail:727212831782731796> | **{value}** is not a valid emoji", colour = int(guild_options["colour"]))
                    return await ctx.send(embed=emb)

                value = emoji.id

            elif option == "timeout":
                try:
                    value = int(value)

                except:
                    try:
                        value = float(value)
                    except:
                        emb = discord.Embed(description=f"<a:fail:727212831782731796> | **{value}** is not a valid timeout", colour = int(guild_options["colour"]))
                        return await ctx.send(embed=emb)

                if type(value) not in [int, float]:
                    emb = discord.Embed(description=f"<a:fail:727212831782731796> | max timeout is **300** seconds!", colour = int(guild_options["colour"]))
                    return await ctx.send(embed=emb)

            async with aiosqlite.connect("data/db.db") as db:
                data = await db.execute(f"select * from settings where id={ctx.guild.id}")
                data = await data.fetchall()

                options.remove(option)

                if len(data) == 0:
                    await db.execute(f"insert into settings (id, {option}, {options[0]}, {options[1]}) VALUES ('{ctx.guild.id}', '{value}', '0', '0')")
                    await db.commit()

                else:
                    await db.execute(f"update settings set {option}={value} where id={ctx.guild.id}")
                    await db.commit()

            guild_options = await cookies.guild_settings(ctx.guild.id)

            if option == "colour": 
                value = str(discord.Colour(int(value)))

            elif option == "emoji": 
                value = str(self.bot.get_emoji(guild_options["emoji"]))

            elif option == "timeout":
                value = f"{value} seconds"
                
            emb = discord.Embed(description = f"<a:check:726040431539912744> | **{option}** for **{ctx.guild.name}** updated to **{value}**", colour = discord.Colour(int(guild_options["colour"])))
            await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Settings(bot))