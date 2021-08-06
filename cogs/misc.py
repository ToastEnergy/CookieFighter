import discord, utils, time, config
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping", description="Check bot latency and response")
    async def ping_slash(self, ctx: SlashContext):
        "Check bot latency and response"

        await self.ping(ctx)

    @commands.command()
    async def ping(self, ctx):
        "Check bot latency and response"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        start = time.perf_counter()
        try: msg = await ctx.reply("Pinging...", mention_author=False)
        except: msg = await ctx.send("Pinging...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        pong = round(self.bot.latency * 1000)
        emb = discord.Embed(description = f"**{config.bot.loading} Response:** `{duration:.2f}ms`\n**🏓 Latency:** `{pong}ms`", colour = settings["colour"])
        await msg.edit(content=None, embed = emb)

    @cog_ext.cog_slash(name="invite", description="Invite the bot to your server")
    async def invite_slash(self, ctx: SlashContext):
        "Invite the bot to your server"

        await self.invite(ctx)

    @commands.command()
    async def invite(self, ctx):
        "Invite the bot to your server"
        
        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        url = discord.utils.oauth_url(self.bot.user.id, scopes=('bot','applications.commands'), permissions=discord.Permissions(permissions=280640))
        emb = discord.Embed(description=f"[Invite me]({url})", colour=settings["colour"])
        await utils.send_embed(ctx, emb)

def setup(bot):
    bot.add_cog(Misc(bot))
