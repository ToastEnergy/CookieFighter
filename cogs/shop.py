import discord
import utils
import config
from discord.ext import commands
from discord import app_commands


class Shop(commands.GroupCog, name="shop"):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        super().__init__()

    async def empty_shop(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="Cookies Shop!", description=f"*The shop for {interaction.guild.name} is empty*", colour=config.colour)
        if interaction.user.guild_permissions.manage_guild:
            emb.description += f"\n\nUse `/shop add <role> <cookies>` to add an item to the shop."

        await interaction.response.send_message(embed=emb)

    async def invalid_role_id(self, interaction: discord.Interaction):
        emb = discord.Embed(
            description=f"{config.emojis.fail} | Invalid `role id`!\nYou can find the role ID before the role name in the `/shop list` command", colour=discord.Colour.red())
        await interaction.response.send_message(embed=emb, ephemeral=True)

    @app_commands.command(name="list")
    @app_commands.guild_only()
    async def shop_list(self, interaction: discord.Interaction) -> None:
        "Buy roles with cookies"

        roles = await utils.get_roles(self.bot.db, interaction.guild)

        if not roles:
            return await self.empty_shop(interaction)

        user_cookies_query = await self.bot.db.fetchrow("SELECT cookies FROM cookies WHERE guild_id = $1 AND user_id = $2", interaction.guild.id, interaction.user.id)
        cookies = 0
        if user_cookies_query:
            cookies = user_cookies_query['cookies']

        emb = discord.Embed(
            title="Cookies Shop!", description=f"__Your cookies:__ `{cookies}` {config.emojis.cookie}\n\nUse `/buy <item number>` to buy something.\n\n", colour=config.colour)
        count = 0
        for role in roles:
            count += 1
            emb.description += f"`{count}.` {role.mention} **{roles[role]} {config.emojis.cookie}**\n"

        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="add")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def add_item(self, interaction: discord.Interaction, role: discord.Role, cookies: int):
        "Add an item to the shop"

        if cookies < 1:
            emb = discord.Embed(
                description=f"{config.emojis.fail} | Please specify a number higher than `0`", colour=discord.Colour.red())
            await interaction.response.send_message(embed=emb)
            return

        await self.bot.db.execute("INSERT INTO shop (guild_id, role_id, cookies) VALUES ($1, $2, $3) ON CONFLICT (guild_id, role_id) DO UPDATE SET cookies=$3", interaction.guild.id, role.id, cookies)
        emb = discord.Embed(
            description=f"{config.emojis.success} | {role.mention} is now available on the shop for **{cookies} {config.emojis.cookie}**", colour=config.colour)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="remove")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def remove_item(self, interaction: discord.Interaction, role: discord.Role):
        "Remove an item from the shop"

        await self.bot.db.execute("DELETE FROM shop WHERE guild_id = $1 AND role_id = $2", interaction.guild.id, role.id)

        emb = discord.Embed(
            description=f"{config.emojis.success} | Item removed from the shop", colour=config.colour)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="buy")
    @app_commands.guild_only()
    async def buy(self, interaction: discord.Interaction, role_id: int):
        "Buy something from the shop"

        roles = await utils.get_roles(self.bot.db, interaction.guild)

        if not roles:
            return await self.empty_shop(interaction)

        try:
            role_id = int(role_id)
        except:
            return await self.invalid_role_id(interaction)

        try:
            role = list(roles.keys())[role_id-1]
        except:
            return await self.invalid_role_id(interaction)

        data = await self.bot.db.fetchrow("SELECT role_id FROM inventory WHERE user_id = $1 AND guild_id = $2 AND role_id = $3", interaction.user.id, interaction.guild.id, role.id)

        if data:
            emb = discord.Embed(
                description=f"{config.emojis.fail} | You already have that item!", colour=discord.Colour.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        cookies = roles[role]
        data = await self.bot.db.fetchrow("SELECT cookies FROM cookies WHERE guild_id = $1 AND user_id = $2", interaction.guild.id, interaction.user.id)

        av_cookies = 0
        if data:
            av_cookies = data['cookies']

        if av_cookies < cookies:
            emb = discord.Embed(
                description=f"{config.emojis.fail} | You don't have enough cookies to buy this item", colour=discord.Colour.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        try:
            await interaction.user.add_roles(role)
        except:
            emb = discord.Embed(
                description=f"{config.emojis.fail} | It looks like I don't have enough permissions to add you that role...", colour=discord.Colour.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        await self.bot.db.execute("INSERT INTO cookies (guild_id, user_id, cookies) VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id) DO UPDATE SET cookies=cookies.cookies + $3", interaction.guild.id, interaction.user.id, -cookies)
        await self.bot.db.execute("INSERT INTO inventory (guild_id, user_id, role_id) VALUES ($1, $2, $3)", interaction.guild.id, interaction.user.id, role.id)
        emb = discord.Embed(
            description=f"{config.emojis.success} | You have successfully bought the role {role.mention}", colour=config.colour)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="sell")
    @app_commands.guild_only()
    async def sell(self, interaction: discord.Interaction, role_id: int):
        "Sell an item (it must be in the shop)"

        roles = await utils.get_roles(self.bot.db, interaction.guild)

        try:
            role = list(roles.keys())[role_id-1]
        except:
            return await self.invalid_role_id(interaction)

        data = await self.bot.db.fetchrow("SELECT role_id FROM inventory WHERE user_id = $1 AND guild_id = $2 AND role_id = $3", interaction.user.id, interaction.guild.id, role.id)
        if not data:
            emb = discord.Embed(
                description=f"{config.emojis.fail} | That role isn't in your inventory!", colour=discord.Colour.red())
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

        cookies = roles[role]
        await self.bot.db.execute("DELETE FROM inventory WHERE guild_id = $1 AND user_id = $2 AND role_id = $3", interaction.guild.id, interaction.user.id, role.id)
        await self.bot.db.execute("INSERT INTO cookies (guild_id, user_id, cookies) VALUES ($1, $2, $3) ON CONFLICT (guild_id, user_id) DO UPDATE SET cookies=cookies.cookies + $3", interaction.guild.id, interaction.user.id, cookies)

        emb = discord.Embed(
            description=f"{config.emojis.success} | You have successfully sold the role {role.mention}", colour=config.colour)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="inventory")
    @app_commands.guild_only()
    async def inventory(self, interaction: discord.Interaction, member: discord.Member = None):
        "Check the inventory of a member"

        member = member or interaction.user
        inv = await self.bot.db.fetch("SELECT role_id FROM inventory WHERE guild_id = $1 AND user_id = $2", interaction.guild.id, member.id)

        emb = discord.Embed(colour=config.colour)
        emb.set_author(name=str(member), icon_url=str(
            member.avatar.replace(static_format="png", size=1024)))

        if len(inv) == 0:
            emb.description = "*Nothing to see here...*"
        else:
            emb.description = ""
            for item in inv:
                role = interaction.guild.get_role(item['role_id'])
                if role:
                    emb.description += f"• {role.mention}\n"

        await interaction.response.send_message(embed=emb)


async def setup(bot):
    # await bot.add_cog(Shop(bot), guilds=[discord.Object(id=config.test_guild)])
    await bot.add_cog(Shop(bot))
