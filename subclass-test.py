import discord
from discord.ext import commands 
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path=".env")
token = os.environ.get("token")

class bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = commands.when_mentioned_or("c/"), case_insensitive = True, description = "Fight your friends and be the first to catch the cookie!")
        self.cookie = "<:mc_cookie:726184620164382741>"
        self.milk = "<:mc_milk:726522958847279174>"
        self.colour = 0xd8ad6a
        self.launchtime = datetime.now()
        self.remove_command("help")
        self.load_extension("jishaku")
        
    def run(self, *args, **kwargs):
        super().run(token)

    async def on_ready(self):
        print("ready as", bot.user)
        await self.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "c/help"), status = discord.Status.idle)
        cmd = self.get_command("jishaku")
        cmd.hidden = True

for a in os.listdir("./cogs"):
    if a.endswith(".py"):
        bot.load_extension(f"cogs.{a[:-3]}")

load_dotenv(dotenv_path=".env")
token = os.environ.get("token")
bot.run(token)