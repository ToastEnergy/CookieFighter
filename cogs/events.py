import asyncio
import json
import datetime
from typing import Union
import config
import discord
from discord.ext import commands, tasks

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.tree.on_error = self.on_command_error

    async def on_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        emb = discord.Embed(description=config.emojis.fail + ' | ' + str(error), colour=discord.Color.red())
        await interaction.response.send_message(embed=emb, ephemeral=True)

        channel = self.bot.get_channel(config.logs.errors)
        
        emb = discord.Embed(colour=discord.Colour.red())
        emb.add_field(name="Command", value=f"`{interaction.command.name}`", inline=False)
        emb.add_field(name="Author", value=f"`{str(interaction.user)}` (`{interaction.user.id}`)", inline=False)
        if interaction.guild:
            emb.add_field(name="Channel", value=f"`#{interaction.channel.name}` (`{interaction.channel.id}`)", inline=False)
            emb.add_field(name="Guild", value=f"`{interaction.guild.name}` (`{interaction.guild.id}`)", inline=False)
            emb.set_thumbnail(url=interaction.guild.icon.replace(static_format="png", size=1024))
        else:
            emb.add_field(name="Channel", value=f"`DM Channel`", inline=False)
        emb.add_field(name="When", value=f"<t:{int(datetime.datetime.now().timestamp())}:f>", inline=False)
        emb.add_field(name="Error", value=f"```py\n{str(error)}\n```")
        emb.set_author(name=str(interaction.user), icon_url=str(interaction.user.avatar))
        await channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_stats.start()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        try:
            headers = {"Content-Type": "application/json",
                       "Authorization": config.botlists.discordbotsgg}
            await self.bot.session.post(f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats", headers=headers, data=json.dumps({"guildCount": len(self.bot.guilds)}))
            await self.bot.topggpy.post_guild_count()
        except Exception as e:
            print(f"Failed to post server count\n{e.__class__.__name__}: {e}")

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: Union[discord.app_commands.Command, discord.app_commands.ContextMenu]):
        channel = self.bot.get_channel(config.logs.commands)

        message = await interaction.original_response()

        emb = discord.Embed(description=f"**`/{command.name}`**\n\n**message id**: `{message.id}`\n**{str(interaction.user)}** (`{interaction.user.id}`)\n**#{interaction.channel.name}** (`{interaction.channel.id}`)\n**{interaction.guild.name}** (`{interaction.guild.id}`)\n\n<t:{int(datetime.datetime.now().timestamp())}:f>", colour=config.colour)
        emb.set_author(name=str(interaction.user), icon_url=interaction.user.avatar)
        emb.set_thumbnail(url=interaction.guild.icon)
        await channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = self.bot.get_channel(config.logs.guilds)
        emb = discord.Embed(description=f"new guild <:ToastyHappy:876936241520705546>\n\n**{guild.name}** `{guild.id}`\nowner id: `{guild.owner_id}`\n`{guild.member_count}` members\nCreated: <t:{int(guild.created_at.timestamp())}:R>", colour=discord.Colour.green())
        emb.set_thumbnail(url=guild.icon)
        await channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        channel = self.bot.get_channel(config.logs.guilds)
        emb = discord.Embed(description=f"lost a guild <:ToastySad:876936241348771900>\n\n**{guild.name}** `{guild.id}`\nowner id: `{guild.owner_id}`\n`{guild.member_count}` members\nCreated: <t:{int(guild.created_at.timestamp())}:R>", colour=discord.Colour.red())
        emb.set_thumbnail(url=guild.icon)
        await channel.send(embed=emb)

async def setup(bot):
    await bot.add_cog(Events(bot))