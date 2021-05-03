import discord, utils
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    async def settings(self, ctx):
        "Check server settings"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        emb = discord.Embed(description=f"• **Emoji:** {settings['emoji']}\n• **Colour:** `{str(discord.Colour(settings['colour']))}`\n• **Timeout:** `{settings['timeout']}`", colour=settings["colour"])
        await ctx.reply(embed=emb, mention_author=False)

def setup(bot):
    bot.add_cog(Settings(bot))
