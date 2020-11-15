import discord, aiosqlite, cookies
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases = ["setting"], invoke_without_command = True, hidden = True)
    @commands.is_owner()
    @commands.has_permissions(manage_messages = True)
    async def settings(self, ctx):
        "setup the bot for your guild"
        
        options = ["colour", "emoji", "timeout"]
        a = "\n" # cuz \n raise an error with f-strings
        prefix = await cookies.guild_prefix(ctx.guild.id)

        emb = discord.Embed(description=f"**Available Settings**{a.join(options)}\nuse `{prefix}settings [setting name] [option]` to set-up the bot\nExample: `{prefix}settings colour #ffffff`", colour=self.bot.colour)
        emb.set_author(name=f"{ctx.guild.name} settings",icon_url=str(ctx.guild.icon_url_as(static_format="png")))

        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Settings(bot))