import discord, humanize, psutil, platform, time, aiosqlite, cookies
from discord.ext import commands
from datetime import datetime

class Misc(commands.Cog):
        def __init__(self, bot):
                self.bot = bot

        @commands.command()
        async def about(self, ctx):
                "About the bot"

                opt = await cookies.guild_settings(ctx.guild.id)
                colour = int(opt["colour"])

                library = discord.__version__
                memory = psutil.virtual_memory()[2]
                cpu = psutil.cpu_percent()
                owners = [str(await self.bot.fetch_user(a)) for a in self.bot.owner_ids]

                emb = discord.Embed(colour = colour, description = f"""```
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

                opt = await cookies.guild_settings(ctx.guild.id)
                colour = int(opt["colour"])
                
                emb = discord.Embed(description = f"**`{days}` days `{hours}` hours `{minutes}` minutes `{seconds}` seconds**", colour = colour)
                await ctx.send(embed = emb)

        @commands.command(aliases = ["join"])
        async def invite(self, ctx):
                "Invite the bot to your server"

                await ctx.send(f"<{discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 84032))}>")
        
        @commands.command()
        async def ping(self, ctx):
                "Check Bot latency and response"

                opt = await cookies.guild_settings(ctx.guild.id)
                colour = int(opt["colour"])

                start = time.perf_counter()
                msg = await ctx.send("Pinging...")
                end = time.perf_counter()
                duration = (end - start) * 1000
                pong = round(self.bot.latency * 1000)
                emb = discord.Embed(description = f"**Response:** `{duration:.2f}ms`\n**Latency:** `{pong}ms`", colour = colour)
                await msg.edit(content=None, embed = emb)

        @commands.command()
        async def vote(self, ctx):
                "Vote the bot on top.gg"
                await ctx.send(f"https://top.gg/bot/{self.bot.user.id}/vote")

        @commands.group(aliases = ["setprefix"], invoke_without_command = True)
        @commands.has_permissions(manage_roles = True)
        async def prefix(self, ctx, *, prefix):
                "Change server prefix"

                opt = await cookies.guild_settings(ctx.guild.id)
                colour = int(opt["colour"])

                if len(prefix) > 36:
                        emb = discord.Embed(description = f"<a:fail:727212831782731796> | The prefix can't be longer than **36** characters!", colour = colour)
                        return await ctx.send(embed = emb)

                async with aiosqlite.connect("data/db.db") as db:
                        await db.execute(f"delete from prefixes where guild = {ctx.guild.id}")
                        await db.execute(f"INSERT into prefixes (guild, prefix) VALUES ({ctx.guild.id}, '{prefix}')")
                        await db.commit()

                emb = discord.Embed(description = f"<a:check:726040431539912744> | Prefix changed to **{prefix}**", colour = colour)
                await ctx.send(embed = emb)

        @prefix.command()
        @commands.has_permissions(manage_roles = True)
        async def reset(self, ctx):
                "reset the prefix to the default one"

                opt = await cookies.guild_settings(ctx.guild.id)
                colour = int(opt["colour"])

                async with aiosqlite.connect("data/db.db") as db:
                        await db.execute(f"delete from prefixes where guild = {ctx.guild.id}")
                        await db.commit()

                emb = discord.Embed(description = f"<a:check:726040431539912744> | Prefix reset to **c/**", colour = colour)
                await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Misc(bot))