import discord, utils, time, config, random
from discord.ext import commands
import discord_components as dc

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        "Check bot latency and response"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        start = time.perf_counter()
        msg = await ctx.reply("Pinging...", mention_author=False)
        end = time.perf_counter()
        duration = (end - start) * 1000
        pong = round(self.bot.latency * 1000)
        emb = discord.Embed(description = f"**{config.bot.loading} Response:** `{duration:.2f}ms`\n**🏓 Latency:** `{pong}ms`", colour = settings["colour"])
        await msg.edit(content="", embed=emb)

    @commands.command()
    async def invite(self, ctx):
        "Invite the bot to your server"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        url = utils.invite_url(self.bot.user.id)
        emb = discord.Embed(description="Thanks for inviting me!", colour=settings["colour"])
        await ctx.reply(embed=emb, components=[dc.Button(label="Invite me", style=dc.ButtonStyle.URL, url=url, emoji=utils.get_emoji(self.bot, config.emojis.zigzag))], mention_author=False)

    @commands.command(hidden=True)
    async def cock(self, ctx):
        await ctx.reply(random.choice(["why", "no u", "°-°", "¿.¿", "•_•", ">.<"]), mention_author=False)

def setup(bot):
    bot.add_cog(Misc(bot))
