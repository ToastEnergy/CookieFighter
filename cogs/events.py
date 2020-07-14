import discord
from discord.ext import commands, tasks
import aiohttp
import os
import aiosqlite

class Events(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()

    @tasks.loop(minutes = 30)
    async def update_stats(self):
        try:
            url = f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats"
            headers = {"Authorization": str(os.environ.get("discordbotlist"))}

            async with aiohttp.ClientSession() as cs:
                await cs.post(url, headers = headers, data = {"guilds": len(self.bot.guilds), "users": len(self.bot.users), "voice_connections": 0})
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
                            if not role in m.roles:
                                await m.add_roles(role)

            for a in role.members:
                if a.id not in lb:
                    await a.remove_roles(role)

        except Exception as e:
            print("TASK ERROR")
            print(e)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.MaxConcurrencyReached) or isinstance(error, commands.CommandOnCooldown):
            emb = discord.Embed(description = f"```sh\n{error}\n```", colour = self.bot.colour)
            return await ctx.send(embed = emb, delete_after = 3)
        
        emb = discord.Embed(description = f"```sh\n{error}\n```", colour = self.bot.colour)
        await ctx.send(embed = emb)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        ch = self.bot.get_channel(725906561394016336)
        emb = discord.Embed(description = f"""<:member_join:596576726163914752> | {self.bot.user.mention} joined **{guild.name}**!
🆔 | {guild.id}
👤 | {guild.owner}
🔢 | {guild.member_count} Members
🍰 | Created at {guild.created_at.strftime("%m / %d / %Y (%H:%M)")}""", colour = discord.Colour.green())
        emb.set_footer(text = f"{len(self.bot.guilds)} guilds", icon_url = self.bot.user.avatar_url)
        emb.set_thumbnail(url = guild.icon_url)
        if guild.banner:
            emb.set_image(url = guild.banner_url)
        
        await ch.send(embed = emb)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        ch = self.bot.get_channel(725906561394016336)
        emb = discord.Embed(description = f"""<:leave:727610879792906302> | {self.bot.user.mention} left **{guild.name}**!
🆔 | {guild.id}
👤 | {guild.owner}
🔢 | {guild.member_count} Members
🍰 | Created at {guild.created_at.strftime("%m / %d / %Y (%H:%M)")}""", colour = discord.Colour.red())
        emb.set_footer(text = f"{len(self.bot.guilds)} guilds", icon_url = self.bot.user.avatar_url)
        emb.set_thumbnail(url = guild.icon_url)
        if guild.banner:
            emb.set_image(url = guild.banner_url)
        
        await ch.send(embed = emb)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 725860467964248075:
            if member.bot:
                r = member.guild.get_role(726172396062769182)
                await member.add_roles(r)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = self.bot.get_channel(728052077007470673)
        emb = discord.Embed(title = ctx.guild.name, url = ctx.message.jump_url, description = ctx.message.content, colour = ctx.author.colour, timestamp = ctx.message.created_at)
        emb.set_author(name = ctx.author, icon_url = str(ctx.author.avatar_url_as(static_format = "png")))
        emb.set_footer(text = "#" + ctx.channel.name)
        await channel.send(embed = emb)

def setup(bot):
    bot.add_cog(Events(bot))