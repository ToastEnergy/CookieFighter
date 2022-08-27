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