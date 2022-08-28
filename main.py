import discord
import os
import asyncpg
import aiohttp
import config
import topgg
import datetime
from discord.ext import commands
from discord import app_commands

os.environ['JISHAKU_NO_UNDERSCORE'] = 'true'
os.environ["JISHAKU_NO_DM_TRACEBACK"] = 'true'
os.environ["JISHAKU_HIDE"] = 'true'

intents = discord.Intents.default()

class CookieFighter(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

    async def setup_hook(self):
        self.remove_command('help')
        self.db = await asyncpg.create_pool(config.POSTGRES_URL)
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS cookies (guild_id BIGINT, user_id BIGINT, cookies BIGINT NOT NULL DEFAULT 0, PRIMARY KEY(guild_id, user_id));
        CREATE TABLE IF NOT EXISTS shop (guild_id BIGINT, role_id BIGINT, cookies BIGINT, PRIMARY KEY(guild_id, role_id));
        CREATE TABLE IF NOT EXISTS inventory (guild_id BIGINT, user_id BIGINT, role_id BIGINT, PRIMARY KEY(guild_id, user_id, role_id));
        """)

        self.session = aiohttp.ClientSession()
        self.topggpy = topgg.DBLClient(bot, config.botlists.topgg)

        for cog in os.listdir("cogs"):
            if cog.endswith(".py") and not cog.startswith("_"):
                cog = f"cogs.{cog.replace('.py', '')}"
                await self.load_extension(cog)

    async def on_ready(self):
        await self.load_extension('jishaku')
        await self.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="/cookie"))

        print('Logged in as', self.user)

bot = CookieFighter()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    emb = discord.Embed(description=config.emojis.fail + ' | ' + str(error), colour=discord.Color.red())
    await interaction.response.send_message(embed=emb, ephemeral=True)

    channel = bot.get_channel(config.logs.errors)
    
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

bot.run(config.token)
