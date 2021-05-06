import discord, utils, time, config
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping", description="Check bot latency and response")
    async def ping_slash(self, ctx: SlashContext):
        "Check bot latency and response"

        settings = utils.get_settings(ctx, self.bot.db_cache)

        start = time.perf_counter()
        msg = await ctx.send("Pinging...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        pong = round(self.bot.latency * 1000)
        emb = discord.Embed(description = f"**{config.bot.loading} Response:** `{duration:.2f}ms`\n**🏓 Latency:** `{pong}ms`", colour = settings["colour"])
        await msg.edit(content=None, embed = emb)

    @commands.command()
    async def ping(self, ctx):
        "Check bot latency and response"

        settings = utils.get_settings(ctx, self.bot.db_cache)

        start = time.perf_counter()
        msg = await ctx.reply("Pinging...", mention_author=False)
        end = time.perf_counter()
        duration = (end - start) * 1000
        pong = round(self.bot.latency * 1000)
        emb = discord.Embed(description = f"**{config.bot.loading} Response:** `{duration:.2f}ms`\n**🏓 Latency:** `{pong}ms`", colour = settings["colour"])
        await msg.edit(content=None, embed = emb)

def setup(bot):
    bot.add_cog(Misc(bot))
