import discord, config, utils, asyncio
from discord.ext import commands

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["c"])
    @commands.guild_only()
    async def cookie(self, ctx):
        settings = utils.get_settings(ctx, self.bot.db_cache)
        emb = discord.Embed(description=f"```\n{config.bot.countdown[0]}\n```", colour=settings["colour"])
        emb.set_footer(text="First one to take the cookie wins 🍪!")

        msg = await ctx.reply(embed=emb, mention_author=False)
        for number in config.bot.countdown:
            if number == config.bot.countdown[0]:
                pass
            else:
                emb.description = f"```\n{number}\n```"
                await msg.edit(content=None, embed=emb)
            await asyncio.sleep(1)

        await msg.add_reaction(settings["emoji"])

def setup(bot):
    bot.add_cog(Cookies(bot))
