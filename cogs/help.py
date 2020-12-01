import discord
from discord.ext import commands
import aiosqlite

class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    async def help(self, ctx, *, command = None):
        "Get some help"

        async with aiosqlite.connect("data/db.db") as db:
            data = await db.execute(f"select * from prefixes where guild = {ctx.guild.id}")
            data = await data.fetchall()

        if len(data) == 0:
            prefix = "c/"

        else:
            prefix = data[0][1]

        emb = discord.Embed(colour = self.bot.colour)
        emb.set_author(name = self.bot.user.name, icon_url = str(self.bot.user.avatar_url_as(static_format = "png")))
        emb.set_footer(text = ctx.author, icon_url = str(ctx.author.avatar_url_as(static_format = "png")))
        error = discord.Embed(description = f"""```sh
Command "{command}" not found
```""", colour = self.bot.colour)

        if command:
            command = self.bot.get_command(command)

            if not command or command.name == "jishaku":
                return await ctx.send(embed = error)

            res =  f"```{command.help}```"

            if command.parent:
                name = command.parent.name + " " + command.name
                res += f"\n**Parent**: __`{command.parent}`__"
            
            else:
                name = command.name

            if command.signature:
                usage = f"{name} {command.signature}"
            else:
                usage = name

            res += f"**\nUsage:** __`{usage}`__"

            if command.aliases:
                al = [f"__`{a}`__" for a in command.aliases]
                res += f"\n**Aliases:** {' '.join(al)}"

            try:
                sub = [f"__`{a}`__" for a in command.commands]
                res += f"\n**Subcommands:** {' '.join(sub)}"
            except:
                pass

            emb.description = res
            return await ctx.send(embed = emb)
        
        res = ""
        for a in self.bot.cogs:
            if str(a) != "Jishaku":
                res_ = f"__`{str(a)}`__\n"
                cog = self.bot.get_cog(a)
                cog_cmds = cog.get_commands()
                act_cmds = [a for a in cog_cmds if not a.hidden]
                if len(act_cmds) >= 1:
                    for b in cog_cmds:
                        if not b.hidden:
                            if b.signature:
                                res_ += f"> `{prefix}{b.name} {b.signature}`\n"
                            else:
                                res_ += f"> `{prefix}{b.name}`\n"
                            try:
                                for c in b.commands:
                                    if not c.hidden:
                                        if c.signature:
                                            res_ += f"> `{prefix}{c.parent} {c.name} {c.signature}`\n"
                                        else:
                                            res_ += f"> `{prefix}{c.parent} {c.name}`\n"
                            except:
                                pass
                                    
                    res += f"{res_}\n"

        emb.description = f"""```
╔═╗╔═╗╔═╗╦╔═╦╔═╗  ╔═╗╦╔═╗╦ ╦╔╦╗╔═╗╦═╗
║  ║ ║║ ║╠╩╗║║╣   ╠╣ ║║ ╦╠═╣ ║ ║╣ ╠╦╝
╚═╝╚═╝╚═╝╩ ╩╩╚═╝  ╚  ╩╚═╝╩ ╩ ╩ ╚═╝╩╚═```
[Invite me]({discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 84032))})
[Support Server](https://discord.gg/vCUpW9E)
Server Prefix: **{prefix}**

**Christmas Art Contest!**
hello artists! we have a challenge for you!
draw a cookie emoji Christmas-Based for the bot!
the winner will get a special role in our discord server, 100 cookies and his name on our future credit command! 
join the support server and post your art in the art-contest channel!


{res}"""
        emb.set_footer(text = f"Need more help? Use \"{prefix}help <command>\".", icon_url = str(ctx.author.avatar_url_as(static_format = "png")))
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Help(bot))