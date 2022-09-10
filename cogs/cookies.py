import asyncio
import discord
import config
from discord.ext import commands
from discord import app_commands

class Cookies(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.busy_channels = []

    @app_commands.command(name="cookie")
    @app_commands.guild_only()
    # @app_commands.guilds(discord.Object(id=config.test_guild))
    async def cookie(self, interaction: discord.Interaction) -> None:
        "Catch the cookie!"

        if interaction.channel.id in self.busy_channels:
            await interaction.response.send_message("Someone is already playing in this channel.", ephemeral=True)
            return

        self.busy_channels.append(interaction.channel.id)

        emb = discord.Embed(description="Catch the cookie in: **3**", color=config.colour)

        await interaction.response.send_message(embed=emb)
        msg = await interaction.original_response()

        await asyncio.sleep(1)
        for x in range(2):
            emb.description = f'Catch the cookie in: **{2 - x}**'
            await msg.edit(content=None, embed=emb)
            await asyncio.sleep(1)

        emb.description = "Catch the cookie!"

        await msg.edit(content=None, embed=emb)
        await msg.add_reaction(config.emojis.cookie)

        def check(reaction, user):
            return reaction.message.channel == interaction.channel and str(reaction.emoji) == config.emojis.cookie and not user.bot and reaction.message.id == msg.id

        try:
            _, user = await self.bot.wait_for('reaction_add', check=check, timeout=10)
        except asyncio.TimeoutError:
            self.busy_channels.remove(interaction.channel.id)
            emb.description = "you're all losers!"
            await msg.edit(content=None, embed=emb)

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
        emb.description = f"{user.mention} won, they now have a total of `{data['cookies']}` {'cookie' if data['cookies'] == 1 else 'cookies'} {config.emojis.cookie}\n\n*Like the bot? Help us by [voting it](https://top.gg/bot/{self.bot.user.id}/vote)!*"
        await msg.edit(content=None, embed=emb)

        self.busy_channels.remove(interaction.channel.id)

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
    @app_commands.describe(member="The member you want to check the balance of, ignore if you want to check your own balance")
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

    @commands.command(name="cookie", aliases=['c'])
    async def old_cookie(self, ctx):
        await ctx.send("This command is now an application command, use `/cookie` instead")

async def setup(bot):
    await bot.add_cog(Cookies(bot))
