import discord, config, aiosqlite, utils, os
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

async def get_prefix(bot, message):

  if message.guild is None:
    prefix = commands.when_mentioned_or(f"{config.bot.prefix} ", config.bot.prefix)(bot, message)

  else:
    data = await (await bot.db.execute("SELECT prefix FROM settings WHERE guild=?", (message.guild.id,))).fetchone()

    if data:
      new_prefix = str(data[0])
      prefix = commands.when_mentioned_or(f"{new_prefix} ", new_prefix)(bot, message)

    else:
      prefix = commands.when_mentioned_or(f"{config.bot.prefix} ", config.bot.prefix)(bot, message)

  return prefix

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=None, description=config.bot.description, intents=intents, case_insensitive=True)
slash = SlashCommand(bot, sync_commands=True, override_type=True)
bot.load_extension("jishaku")

@bot.event
async def on_ready():
    bot.db = await aiosqlite.connect("db.db")
    await utils.check_db(bot.db)
    bot.command_prefix=get_prefix
    bot.remove_command("help")
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")

    print("ready as", bot.user)

bot.run(config.tokens.bot)
