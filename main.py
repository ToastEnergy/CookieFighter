import discord
from discord.ext import commands 
import os
from dotenv import load_dotenv
from datetime import datetime

bot = commands.Bot(command_prefix = commands.when_mentioned_or("c/"), case_insensitive = True, description = "Fight your friends and be the first to catch the cookie!")
bot.cookie = "<:mc_cookie:726184620164382741>"
bot.milk = "<:mc_milk:726522958847279174>"
bot.colour = 0xd8ad6a
bot.launchtime = datetime.now()
bot.remove_command("help")
bot.load_extension("jishaku")

@bot.event
async def on_ready():
    print("ready as", bot.user)
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "c/help"))
    cmd = bot.get_command("jishaku")
    cmd.hidden = True

for a in os.listdir("./cogs"):
    if a.endswith(".py"):
        bot.load_extension(f"cogs.{a[:-3]}")

load_dotenv(dotenv_path=".env")
token = os.environ.get("token")
bot.run(token)