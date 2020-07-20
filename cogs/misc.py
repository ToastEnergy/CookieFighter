import discord
from discord.ext import commands
import platform
import psutil
from datetime import datetime
import time

class Misc(commands.Cog):
        
        def __init__(self, bot):
                self.bot = bot

        @commands.command()
        async def about(self, ctx):
                "About the bot"

                library = discord.__version__
                memory = psutil.virtual_memory()[2]
                cpu = psutil.cpu_percent()
                owners = [str(self.bot.get_user(a)) for a in self.bot.owner_ids]

                emb = discord.Embed(colour = self.bot.colour, description = f"""```
╔═╗╔═╗╔═╗╦╔═╦╔═╗  ╔═╗╦╔═╗╦ ╦╔╦╗╔═╗╦═╗
║  ║ ║║ ║╠╩╗║║╣   ╠╣ ║║ ╦╠═╣ ║ ║╣ ╠╦╝
╚═╝╚═╝╚═╝╩ ╩╩╚═╝  ╚  ╩╚═╝╩ ╩ ╩ ╚═╝╩╚═

Fight your friends and be the first to catch the cookie!
```
Prefix: `c/`
[Invite Me]({discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 84032))})
[Support Server](https://discord.gg/vCUpW9E)
[Vote the Bot](https://top.gg/bot/638483485417406495/vote)
[Support Bot Development](https://www.paypal.me/cookiefighterbot)""")
                emb.add_field(name = "Info", value = f"""```prolog
Devs: {" & ".join(owners)}
Guilds: {len(self.bot.guilds)}
Users: {len(self.bot.users)}```""")
                emb.add_field(name = "Stats", value = f"""```prolog
discord.py: {library}
Cpu: {cpu}%
Memory: {memory}%```""")

                await ctx.send(embed = emb)

        @commands.command(aliases = ["ut"])
        async def uptime(self, ctx):
                "Check bot uptime"

                uptime = datetime.now() - self.bot.launchtime
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                days, hours = divmod(hours, 24)
                
                emb = discord.Embed(description = f"**`{days}` days `{hours}` hours `{minutes}` minutes `{seconds}` seconds**", colour = self.bot.colour)
                await ctx.send(embed = emb)

        @commands.command(aliases = ["join"])
        async def invite(self, ctx):
                "Invite the bot to your server"

                await ctx.send(f"<{discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 84032))}>")
        
        @commands.command()
        async def ping(self, ctx):
                "Check Bot latency and response"

                start = time.perf_counter()
                msg = await ctx.send("Pinging...")
                end = time.perf_counter()
                duration = (end - start) * 1000
                pong = round(self.bot.latency * 1000)
                emb = discord.Embed(description = f"**Response:** `{duration:.2f}ms`\n**Latency:** `{pong}ms`", colour = self.bot.colour)
                await msg.edit(content=None, embed = emb)

def setup(bot):
    bot.add_cog(Misc(bot))