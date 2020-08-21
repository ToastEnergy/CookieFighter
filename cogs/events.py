import discord
from discord.ext import commands, tasks
import aiohttp
import os
import aiosqlite
import traceback
import humanize

class Events(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()

    @tasks.loop(minutes = 30)
    async def update_stats(self):
        try:
            url = f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats"
            headers = {"Authorization": str(os.environ.get("discordbotsgg"))}
            url1 = f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats"    
            headers1 = {"Authorization": str(os.environ.get("discordbotlist"))}
            url2 = f"https://api.discordextremelist.xyz/v2/bot/{self.bot.user.id}/stats"
            headers2 = {"Authorization": str(os.environ.get("discordextremelist")), "Content-Type": "application/json"}

            async with aiohttp.ClientSession() as cs:
                    await cs.post(url, headers = headers, data = {"guildCount": len(self.bot.guilds)})
                    await cs.post(url1, headers = headers1, data = {"guilds": len(self.bot.guilds), "users": len(self.bot.users), "voice_connections": 0})
                    await cs.post(url2, headers = headers2, data = {"guildCount": len(self.bot.guilds)})
            await cs.close()

        except Exception as e:
            print(e)

        try:
            guild = self.bot.get_guild(725860467964248075)
            stats = {}

            async with aiosqlite.connect("data/db.db") as db:
                data = await db.execute("SELECT * from ids")
                data = await data.fetchall()

                for a in data:
                    data = await db.execute(f"SELECT * from '{a[0]}'")
                    data = await data.fetchall()
                    stats[str(a[0])] = int(data[0][0])
            
            lb = sorted(stats, key=lambda x : stats[x], reverse=True)
            role = guild.get_role(732621593112608809)

            counter = 0
            for a in lb:
                if counter >= 10:
                    pass
                else:
                    u = self.bot.get_user(int(a))
                    if u:
                        counter += 1
                        m = guild.get_member(int(a))
                        if m:
                            if role.id not in [a.id for a in m.roles]:
                                await m.add_roles(role)

            for a in role.members:
                print(a)
                if int(a.id) not in [int(b) for b in lb]:
                    await a.remove_roles(role)
                    print("Role removed to", a)
                    
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        if ctx.command in [self.bot.get_command("cookie"), self.bot.get_command("milk"), self.bot.get_command("type")]:
            if isinstance(error, commands.BadArgument):
                emb = discord.Embed(description = f"<a:fail:727212831782731796> | To set a timeout you need to use a number, if want a decimal number, use this format: `10.4`.", colour = self.bot.colour)
                return await ctx.send(embed = emb)
            
            else: pass

        elif ctx.command == self.bot.get_command("send"):
            if isinstance(error, commands.BadArgument):
                emb = discord.Embed(description = f"<a:fail:727212831782731796> | Please use this format: `send @user 40`", colour = self.bot.colour)
                return await ctx.send(embed = emb)
            
            else: pass

        elif isinstance(error, commands.MaxConcurrencyReached) or isinstance(error, commands.CommandOnCooldown):
            emb = discord.Embed(description = f"```sh\n{error}\n```", colour = self.bot.colour)
            return await ctx.send(embed = emb, delete_after = 3)

        elif isinstance(error, commands.NotOwner):
            if ctx.command == self.bot.get_command("prefix"):
                if ctx.author.id in [488398758812319745, 326736523494031360]:
                    await ctx.reinvoke()
                else:
                    pass
        
        emb = discord.Embed(description = f"```sh\n{error}\n```", colour = self.bot.colour)
        await ctx.send(embed = emb)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        ch = self.bot.get_channel(725906561394016336)
        emb = discord.Embed(description = f"""<:member_join:596576726163914752> | {self.bot.user.mention} joined **{guild.name}**!
🆔 | {guild.id}
👤 | {guild.owner}
🔢 | {guild.member_count} Members
🍰 | Created {humanize.naturaltime(guild.created_at)}""", colour = discord.Colour.green())
        emb.set_footer(text = f"{len(self.bot.guilds)} guilds", icon_url = self.bot.user.avatar_url)
        emb.set_thumbnail(url = guild.icon_url)
        if guild.banner:
            emb.set_image(url = guild.banner_url)
        
        await ch.send(embed = emb)
        await ch.edit(topic = f"{len(self.bot.guilds)} servers\n{len(self.bot.users)} users")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        ch = self.bot.get_channel(725906561394016336)
        emb = discord.Embed(description = f"""<:leave:727610879792906302> | {self.bot.user.mention} left **{guild.name}**!
🆔 | {guild.id}
👤 | {guild.owner}
🔢 | {guild.member_count} Members
🍰 | Created {humanize.naturaltime(guild.created_at)}""", colour = discord.Colour.red())
        emb.set_footer(text = f"{len(self.bot.guilds)} guilds", icon_url = self.bot.user.avatar_url)
        emb.set_thumbnail(url = guild.icon_url)
        if guild.banner:
            emb.set_image(url = guild.banner_url)
        
        await ch.send(embed = emb)
        await ch.edit(topic = f"{len(self.bot.guilds)} servers\n{len(self.bot.users)} users")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 725860467964248075:
            if member.bot:
                r = member.guild.get_role(726172396062769182)
                await member.add_roles(r)

            ch = self.bot.get_channel(725909095017873492)
            await ch.edit(topic = f"Hello new people!\n{member.guild.member_count} members")
    
    @commands.Cog.listener()
    async def on_member_removed(self, member):
        if member.guild.id == 725860467964248075:
            ch = self.bot.get_channel(725909095017873492)
            await ch.edit(topic = f"Hello new people!\n{member.guild.member_count} members")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = self.bot.get_channel(728052077007470673)
        emb = discord.Embed(title = ctx.guild.name, url = ctx.message.jump_url, description = ctx.message.content, colour = ctx.author.colour, timestamp = ctx.message.created_at)
        emb.set_author(name = ctx.author, icon_url = str(ctx.author.avatar_url_as(static_format = "png")))
        emb.set_footer(text = "#" + ctx.channel.name)
        await channel.send(embed = emb)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id != 725860467964248075:
            return 
        if payload.message_id == 734861410567192628:
            if payload.emoji.name == "📰":
                guild = self.bot.get_guild(payload.guild_id)
                r = guild.get_role(734859787388321854)
                m = guild.get_member(payload.user_id)
                await m.add_roles(r)

            elif payload.emoji.name == "🎉":
                guild = self.bot.get_guild(payload.guild_id)
                r = guild.get_role(734859719482671145)
                m = guild.get_member(payload.user_id)
                await m.add_roles(r)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id != 725860467964248075:
            return 
        if payload.message_id == 734861410567192628:
            if payload.emoji.name == "📰":
                guild = self.bot.get_guild(payload.guild_id)
                r = guild.get_role(734859787388321854)
                m = guild.get_member(payload.user_id)
                await m.remove_roles(r)

            elif payload.emoji.name == "🎉":
                guild = self.bot.get_guild(payload.guild_id)
                r = guild.get_role(734859719482671145)
                m = guild.get_member(payload.user_id)
                await m.remove_roles(r)

def setup(bot):
    bot.add_cog(Events(bot))