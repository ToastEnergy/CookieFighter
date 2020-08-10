import dbl
import discord
from discord.ext import commands
import os 
from dotenv import load_dotenv

load_dotenv(dotenv_path = ".env")

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = os.environ.get("topgg")
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True) # Autopost will post your guild count every 30 minutes

    async def on_guild_post(self):
        print("Server count posted successfully")

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        ch = self.bot.get_channel(725860667772502016)
        await ch.send(data)

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        ch = self.bot.get_channel(725860667772502016)
        await ch.send(data)

def setup(bot):
    bot.add_cog(TopGG(bot))