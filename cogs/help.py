import discord
from discord.ext import commands

class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    async def help(self, ctx, *, command = None):
        "Get some help"

        emb = discord.Embed(colour = self.bot.colour)
        emb.set_author(name = self.bot.user.name, icon_url = str(self.bot.user.avatar_url_as(static_format = "png")))
        emb.set_footer(text = ctx.author, icon_url = str(ctx.author.avatar_url_as(static_format = "png")))
        error = discord.Embed(description = f"""```sh
Command "{command}" not found
```""", colour = self.bot.colour)

        if command:
            command = self.bot.get_command(command)

            if not command:
                return await ctx.send(embed = error)

            res =  f"```{command.help}```"

            if command.parent:
                name = command.parent, command.name
                res += f"\n**Parent**: __`{command.parent}`__"
            
            else:
                name = command.name

            if command.signature:
                usage = f"{name} {command.signature}"
            else:
                usage = command.name

            res += f"**\nUsage:** __`{usage}`__"

            if command.aliases:
                al = [f"__`{a}`__" for a in command.aliases]
                res += f"\n**Aliases:** {' '.join(al)}"

            emb.description = res
            return await ctx.send(embed = emb)
        
        res = ""
        for a in self.bot.cogs:
            res_ = f"__`{str(a)}`__\n"
            cog = self.bot.get_cog(a)
            cog_cmds = cog.get_commands()
            act_cmds = [a for a in cog_cmds if not a.hidden]
            if len(act_cmds) >= 1:
                for b in cog_cmds:
                    if not b.hidden:
                        if b.signature:
                            res_ += f"> `c/{b.name} {b.signature}`\n"
                        else:
                            res_ += f"> `c/{b.name}`\n"
                        try:
                            for c in b.commands:
                                if not c.hidden:
                                    if c.signature:
                                        res_ += f"> `c/{c.parent} {c.name} {c.signature}`\n"
                                    else:
                                        res_ += f"> `c/{c.parent} {c.name}`\n"
                        except:
                            pass
                                
                res += f"{res_}\n"

        emb.description = f"""```
╔═╗╔═╗╔═╗╦╔═╦╔═╗  ╔═╗╦╔═╗╦ ╦╔╦╗╔═╗╦═╗
║  ║ ║║ ║╠╩╗║║╣   ╠╣ ║║ ╦╠═╣ ║ ║╣ ╠╦╝
╚═╝╚═╝╚═╝╩ ╩╩╚═╝  ╚  ╩╚═╝╩ ╩ ╩ ╚═╝╩╚═```
[Invite me]({discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 84032))})
[Support Server](https://discord.gg/vCUpW9E)

{res}"""
        emb.set_footer(text = f"Need more help? Use \"c/help <command>\".", icon_url = str(ctx.author.avatar_url_as(static_format = "png")))
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Help(bot))