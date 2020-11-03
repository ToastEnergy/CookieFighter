import discord
from discord.ext import commands 
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import sqlite3
import aiosqlite

load_dotenv(dotenv_path=".env")

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

def get_prefix(bot, message):

  if message.guild is None:
    prefix = commands.when_mentioned_or("c/ ", "c/")(bot, message)
  
  else:
    with sqlite3.connect("data/db.db") as db:
        data = db.execute(f"SELECT * from prefixes where guild = {message.guild.id}")
        data = data.fetchall()

    if len(data) >= 1:
      new_prefix = str(data[0][1])
      prefix = commands.when_mentioned_or(f"{new_prefix} ", new_prefix)(bot, message)

    else:
      prefix = commands.when_mentioned_or("c/ ", "c/")(bot, message)

  return prefix

intents = discord.Intents.default()
# intents.members = True

bot = commands.AutoShardedBot(command_prefix = get_prefix, case_insensitive = True, description = "Fight your friends and be the first to catch the cookie!", intents = intents, owner_ids = [488398758812319745, 326736523494031360, 771316465789960203])
bot.cookie = "<:mc_cookie:726184620164382741>"
bot.oreo = "<:oreo:761274120821276702>"
bot.gocciola = "<:gocciola:747247300803297290>"
bot.milk = "<:mc_milk:726522958847279174>"
bot.clock = "<a:mc_clock:748835359991005215>"
bot.colour = 0xd8ad6a
bot.launchtime = datetime.now()
bot.remove_command("help")
bot.load_extension("jishaku")

@bot.event
async def on_ready():
    print("ready as", bot.user)
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "c/help"), status = discord.Status.idle)
    cmd = bot.get_command("jishaku")
    cmd.hidden = True

@bot.check
async def blacklist(ctx):
  async with aiosqlite.connect("data/db.db") as db:
    data = await db.execute(f"SELECT * from blacklist where user = {ctx.author.id}")
    data = await data.fetchall()

  if len(data) == 1:
    emb = discord.Embed(description = f"<a:fail:727212831782731796> | {ctx.author.mention} you can't use the bot because you are blacklisted!", colour = bot.colour)
    await ctx.send(embed = emb, delete_after = 5)
    return False

  else:
    return True

for a in os.listdir("./cogs"):
    if a.endswith(".py"):
        bot.load_extension(f"cogs.{a[:-3]}")

token = os.environ.get("token")
bot.run(token)