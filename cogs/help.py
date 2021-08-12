import discord, utils, config
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

command_names = []

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global command_names
        command_names = [create_choice(name=command.name, value=command.name) for command in self.bot.commands if not command.hidden]

    @cog_ext.cog_slash(name="help", description="Get some help", options=[
        create_option(
            name="command",
            description="Need help for a single command?",
            option_type=3,
            required=False,
            choices=command_names
        )
    ])
    async def helpslash(self, ctx: SlashContext, command=None):
        "Get some help"

        print(command_names)
        await self.help(ctx, command=command)

    @commands.command(hidden = True)
    async def help(self, ctx, *, command=None):
        "Get some help"

        if ctx.guild:
            settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        else:
            settings = await utils.get_settings(self.bot.db)
        prefix = settings['prefix']
        emb = discord.Embed(colour=settings['colour'])
        emb.set_author(name=self.bot.user.name, icon_url=str(self.bot.user.avatar.replace(static_format="png", size=1024)))
        emb.set_footer(text=ctx.author, icon_url=str(ctx.author.avatar.replace(static_format="png", size=1024)))
        error = discord.Embed(description=f"""```sh
Command "{command}" not found
```""", colour=settings['colour'])

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
            return await utils.send_embed(ctx, embed=emb)

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
{config.bot.banner}```
[Invite me]({utils.invite_url(self.bot.user.id)})
[Support Server]({config.bot.support_server})
Server Prefix: **{prefix}**

{res}"""
        emb.set_footer(text=f"Need more help? Use \"{prefix}help <command>\".", icon_url=str(ctx.author.avatar.replace(static_format="png", size=1024)))
        await utils.send_embed(ctx, embed=emb)

def setup(bot):
    bot.add_cog(Help(bot))
