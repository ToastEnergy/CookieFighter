import discord, config, aiomysql, utils, os
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=config.bot.default_prefix, description=config.bot.description, intents=intents)
slash = SlashCommand(bot, sync_commands=True, override_type=True)
bot.load_extension("jishaku")

@bot.event
async def on_ready():
    bot.db = await aiomysql.connect(
      host=config.db.host,
      user=config.db.user,
      password=config.db.password,
      db=config.db.db
    )
    bot.cursor = await bot.db.cursor()
    await utils.check_db(bot.cursor, bot.db)
    bot.db_cache = await utils.get_data(bot.cursor)
    print("ready as", bot.user)

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run(config.tokens.bot)
