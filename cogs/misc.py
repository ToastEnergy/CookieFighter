import discord, utils, time, config, random, psutil, datetime
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
        await ctx.reply(embed=emb, components=[dc.Button(label="Invite me", style=dc.ButtonStyle.URL, url=url, emoji=utils.get_emoji(self.bot, config.emojis.invite))], mention_author=False)

    @commands.command(hidden=True)
    async def cock(self, ctx):
        await ctx.reply(random.choice(["why", "no u", "°-°", "¿.¿", "•_•", ">.<"]), mention_author=False)

    @commands.command()
    async def about(self, ctx):
        "About the bot"

        async with ctx.typing():
            settings = await utils.get_settings(self.bot.db, ctx.guild.id)
            library = discord.__version__
            memory = psutil.virtual_memory()[2]
            cpu = psutil.cpu_percent()
            owners = [str(await self.bot.fetch_user(a)) for a in self.bot.owner_ids]
            invite_url = utils.invite_url(self.bot.user.id)
            emb = discord.Embed(colour=settings['colour'], description=f"""```
{config.bot.banner}
```
> Default Prefix: `{config.bot.prefix}`
> Server Prefix: `{settings['prefix']}`

[Invite Me]({invite_url}) | [Vote the Bot](https://top.gg/bot/{self.bot.user.id}/vote) | [Support Server]({config.bot.support_server})""")
            emb.add_field(name = "Info", value = f"""```prolog
Devs: {" & ".join(owners)}
Guilds: {len(self.bot.guilds)}
```""")
            emb.add_field(name="Stats", value=f"""```prolog
discord.py: {library}
CPU: {cpu}%
Memory: {memory}%```""")

            await ctx.reply(embed=emb, mention_author=False, components=[[dc.Button(style=dc.ButtonStyle.URL, url=invite_url, label='Invite Me', emoji=utils.get_emoji(self.bot, config.emojis.invite)), dc.Button(style=dc.ButtonStyle.URL, url=f"https://top.gg/bot/{self.bot.user.id}/vote", label='Vote me', emoji=utils.get_emoji(self.bot, config.emojis.upvote)),  dc.Button(style=dc.ButtonStyle.URL, url=config.bot.support_server, label='Support Server', emoji=utils.get_emoji(self.bot, config.emojis.support))]])

    @commands.command(aliases = ["ut"])
    async def uptime(self, ctx):
        "Check bot uptime"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        uptime = datetime.datetime.utcnow() - self.bot.launchtime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        emb = discord.Embed(description=f"**`{days}` days `{hours}` hours `{minutes}` minutes `{seconds}` seconds**", colour=settings['colour'])
        await ctx.reply(embed=emb, mention_author=False)

def setup(bot):
    bot.add_cog(Misc(bot))
