import asyncio
import discord
import config
from discord.ext import commands
from discord import app_commands

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="cookie")
    @app_commands.guild_only()
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def cookie(self, interaction: discord.Interaction) -> None:
        "Catch the cookie!"

        await interaction.response.send_message('catch the cookie in: 3')
        msg = await interaction.original_response()

        await asyncio.sleep(1)
        for x in range(2):
            await msg.edit(content=f'catch the cookie in: {2 - x}')
            await asyncio.sleep(1)

        await msg.edit(content=f'catch the cookie!')
        await msg.add_reaction(config.emojis.cookie)

        def check(reaction, user):
            return reaction.message.channel == interaction.channel and str(reaction.emoji) == config.emojis.cookie and not user.bot and reaction.message.id == msg.id

        try:
            _, user = await self.bot.wait_for('reaction_add', check=check, timeout=10)
        except asyncio.TimeoutError:
            await msg.edit(content="you're all losers")
            if interaction.channel.permissions_for(interaction.guild.me).manage_messages:
                await msg.clear_reactions()
            else:
                await msg.remove_reaction(config.emojis.cookie, self.bot.user)
            return

        if interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await msg.clear_reactions()
        else:
            await msg.remove_reaction(config.emojis.cookie, self.bot.user)

        data = await self.bot.db.fetchrow("INSERT INTO cookies (guild_id, user_id, cookies) VALUES ($1, $2, 1) ON CONFLICT (guild_id, user_id) DO UPDATE SET cookies = cookies.cookies + 1 RETURNING cookies", interaction.guild.id, user.id)
        await msg.edit(content=f"{user.mention} won, they now have a total of {data['cookies']} cookies")

    @app_commands.command(name="leaderboard")
    @app_commands.guild_only()
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        "Users with more cookies in the current server"

        data = await self.bot.db.fetch("SELECT user_id, cookies FROM cookies WHERE guild_id = $1 ORDER BY cookies DESC LIMIT 10", interaction.guild.id)
        if not data:
            await interaction.response.send_message("no one has any cookies")
            return
        text = "\n".join(f"`{i + 1}.` <@{user_id}> - {cookies} {config.emojis.cookie}" for i,
                         (user_id, cookies) in enumerate(data))
        await interaction.response.send_message(text, allowed_mentions=discord.AllowedMentions().none())

    @app_commands.command(name="balance")
    @app_commands.guild_only()
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        "Check how many cookies do you have"

        member = member or interaction.user;

        data = await self.bot.db.fetchrow("SELECT cookies FROM cookies WHERE guild_id = $1 AND user_id = $2", interaction.guild.id, member.id)
        cookies = 0
        if data:
            cookies = data['cookies']
        emb = discord.Embed(description=f"**{cookies}** {'cookie' if cookies == 1 else 'cookies'} {config.emojis.cookie}", color=config.colour)
        emb.set_author(name=str(member), icon_url=member.avatar.url)

        await interaction.response.send_message(embed=emb)

async def setup(bot):
    await bot.add_cog(Cookies(bot))
