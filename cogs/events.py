import asyncio
import json
import datetime
import config
import discord
from discord.ext import commands, tasks

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_stats.start()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        try:
            headers = {"Content-Type": "application/json",
                       "Authorization": config.botlists.discordbotsgg}
            await self.bot.session.post(f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats", headers=headers, data=json.dumps({"guildCount": len(self.bot.guilds)}))
            await self.bot.topggpy.post_guild_count()
        except Exception as e:
            print(f"Failed to post server count\n{e.__class__.__name__}: {e}")

async def setup(bot):
    await bot.add_cog(Events(bot))