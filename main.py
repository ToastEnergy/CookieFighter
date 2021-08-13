import discord, config, aiosqlite, utils, os
from discord.ext import commands
import discord_components as dc

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

async def get_prefix(bot, message):
  if message.guild is None:
    prefix = commands.when_mentioned_or(f"{config.bot.prefix} ",  f"{config.bot.prefix[0].upper()}{config.bot.prefix[1:]} ",  f"{config.bot.prefix[0].upper()}{config.bot.prefix[1:]}" ,config.bot.prefix)(bot, message)
  else:
    data = await (await bot.db.execute("SELECT prefix FROM settings WHERE guild=?", (message.guild.id,))).fetchone()
    if data:
      new_prefix = str(data[0])
      prefix = commands.when_mentioned_or(f"{new_prefix} ",  f"{new_prefix[0].upper()}{new_prefix[1:]} ",  f"{new_prefix[0].upper()}{new_prefix[1:]}" , new_prefix)(bot, message)
    else:
      prefix = commands.when_mentioned_or(f"{config.bot.prefix} ",  f"{config.bot.prefix[0].upper()}{config.bot.prefix[1:]} ",  f"{config.bot.prefix[0].upper()}{config.bot.prefix[1:]}" ,config.bot.prefix)(bot, message)
  return prefix

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=None, description=config.bot.description, intents=intents, case_insensitive=True)
bot.load_extension("jishaku")
bot.remove_command("help")

@bot.event
async def on_ready():
    dc.DiscordComponents(bot)
    bot.db = await aiosqlite.connect("db.db")
    await utils.check_db(bot.db)
    bot.command_prefix=get_prefix
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{config.bot.prefix}help"), status=discord.Status.idle)
    print("ready as", bot.user)

@bot.check
async def bot_check(ctx):
    if not ctx.guild and ctx.command.name != "help":
        return False
    return True

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run(config.tokens.bot)
