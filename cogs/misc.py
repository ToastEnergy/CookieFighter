import discord, utils
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping", description="Bot latency")
    async def ping_slash(self, ctx: SlashContext):
        settings = utils.get_settings(ctx, self.bot.db_cache)
        emb = discord.Embed(description=f"Pong! `{round(self.bot.latency * 1000)}`ms", colour=settings["colour"])
        await ctx.send(embeds=[emb])

def setup(bot):
    bot.add_cog(Misc(bot))
