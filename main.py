import discord
from discord.ext import commands 
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import sqlite3

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

bot = commands.AutoShardedBot(command_prefix = get_prefix, case_insensitive = True, description = "Fight your friends and be the first to catch the cookie!")
bot.cookie = "<:mc_cookie:726184620164382741>"
bot.milk = "<:mc_milk:726522958847279174>"
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

for a in os.listdir("./cogs"):
    if a.endswith(".py"):
        bot.load_extension(f"cogs.{a[:-3]}")

token = os.environ.get("token")
bot.run(token)