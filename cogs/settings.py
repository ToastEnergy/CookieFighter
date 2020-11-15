import discord, aiosqlite, cookies, random
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases = ["setting"], invoke_without_command = True, hidden = True)
    @commands.is_owner()
    @commands.has_permissions(manage_messages = True)
    async def settings(self, ctx, option=None, value=None):
        "setup the bot for your guild"

        if not option:
            guild_options = await cookies.guild_settings(ctx.guild.id)
            prefix = await cookies.guild_prefix(ctx.guild.id)

            options = ["__colour__", "__emoji__", "__timeout__"]
            cookie = random.choice([self.bot.cookie, self.bot.gocciola, self.bot.oreo])
            a = f"\n{cookie} " # cuz \n raise an error with f-strings

            emb = discord.Embed(description=f"""**Available Settings**
            
{cookie} {a.join(options)}

**use** `{prefix}settings [setting name] [option]` to set-up the bot
**example**: `{prefix}settings colour #ffffff`

**Current Settings**

{cookie} {a.join([f'__{opt}__: `{guild_options[opt]}`' for opt in guild_options])}
""", colour=self.bot.colour)
            emb.set_author(name=f"{ctx.guild.name} settings",icon_url=str(ctx.guild.icon_url_as(static_format="png")))

            return await ctx.send(embed=emb)

        else:
            async with ctx.typing():
                option = str(option).lower()

                if option == "color":
                    option == "colour"

                options = ["colour", "emoji", "timeout"]
                if option not in options:
                    emb = discord.Embed(description=f"<a:fail:727212831782731796> | **{option}** is not a valid option")
                    return await ctx.send(embed=emb)

                async with aiosqlite.connect("data/db.db") as db:
                    data = await db.execute(f"select * from settings where id={ctx.guild.id}")
                    data = await data.fetchall()

                    options.remove(option)

                    if len(data) == 0:
                        await db.execute(f"insert into settings (id, {option}, {options[0]}, {options[1]}) VALUES ('{ctx.guild.id}', '{value}' '0', '0')")
                        await db.commit()

                    else:
                        await db.execute(f"update settings set colour={value} where id={ctx.guild.id}")
                        await db.commit()
                
            emb = discord.Embed(title = "<a:check:726040431539912744> | done!", description = f"**{option}** for **{ctx.guild.name}** updated to **{value}**")
            await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Settings(bot))