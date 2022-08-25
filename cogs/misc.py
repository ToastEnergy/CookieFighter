import asyncio
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

        url = discord.utils.oauth_url(self.bot.user.id, scopes=('bot', 'applications.commands'), permissions=discord.Permissions(permissions=10304))
        await interaction.response.send_message(url)

    @app_commands.command(name="help")
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def help(self, interaction: discord.Interaction) -> None:
        "Get a list of commands"

        res = ""
        for command in self.bot._BotBase__tree.get_commands():
            if type(command) == discord.app_commands.Group:
                for sub_command in command.commands:
                    res += f"`/{command.name} {sub_command.name}` - {sub_command.description}\n"
            else:
                res += f"`/{command.name}` - {command.description}\n"

        emb = discord.Embed(description=res, color=config.colour)
        await interaction.response.send_message(embed=emb)

async def setup(bot):
    await bot.add_cog(Misc(bot))
