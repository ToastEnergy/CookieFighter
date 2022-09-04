import datetime
import discord
import config
from discord.ext import commands
from discord import app_commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="invite")
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def invite(self, interaction: discord.Interaction) -> None:
        "Invite the bot to your server"

        url = discord.utils.oauth_url(self.bot.user.id, scopes=(
            'bot', 'applications.commands'), permissions=discord.Permissions(permissions=10304))
        await interaction.response.send_message(url)

    @app_commands.command(name="vote")
    async def vote(self, interaction: discord.Interaction) -> None:
        "Vote for the bot"

        await interaction.response.send_message(f"Thanks for voting!\n\nhttps://top.gg/bot/{self.bot.user.id}/vote")

    @commands.hybrid_command(name="help", with_app_command=True)
    # @app_commands.command(name="help")
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def help(self, ctx) -> None:
        "Get a list of commands"

        url = discord.utils.oauth_url(self.bot.user.id, scopes=(
            'bot', 'applications.commands'), permissions=discord.Permissions(permissions=10304))
        res = f"""
You can invite the bot to your server with [this link]({url})
If you need any help feel free to ask in the [support server](https://discord.gg/ayJn6Hys2r)

"""
        for command in self.bot._BotBase__tree.get_commands():
            if type(command) == discord.app_commands.Group:
                for sub_command in command.commands:
                    res += f"`/{command.name} {sub_command.name}` - {sub_command.description}\n"
            else:
                res += f"`/{command.name}` - {command.description}\n"

        emb = discord.Embed(description=res, color=config.colour)
        await ctx.send(embed=emb)

    @app_commands.command(name="about")
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def about(self, interaction: discord.Interaction) -> None:
        "About the bot"

        url = discord.utils.oauth_url(self.bot.user.id, scopes=(
            'bot', 'applications.commands'), permissions=discord.Permissions(permissions=10304))

        text = f"""
**Cookie Fighter** is a discord bot made by [Toast Energy](https://toastenergy.xyz)

You can invite the bot to your server with [this link]({url})
If you need any help feel free to ask in the [support server](https://discord.gg/ayJn6Hys2r)

The bot is currently in `{len(self.bot.guilds)}` servers.
It has been created <t:{round(datetime.datetime.timestamp(self.bot.user.created_at))}:R>
"""

        emb = discord.Embed(description=text, color=config.colour)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="support")
    async def support(self, interaction: discord.Interaction) -> None:
        "Get the support server invite"

        await interaction.response.send_message("https://discord.gg/ayJn6Hys2r")

async def setup(bot):
    await bot.add_cog(Misc(bot))
