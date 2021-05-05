import discord, utils
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="settings", description="Check server settings")
    async def settings_slash(self, ctx: SlashContext):
        settings = utils.get_settings(ctx, self.bot.db_cache)
        emb = discord.Embed(description=f"• **Emoji:** {settings['emoji']}\n• **Colour:** `{str(discord.Colour(settings['colour']))}`\n• **Timeout:** `{settings['timeout']}`", colour=settings["colour"])
        await ctx.send(embed=emb)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def settings(self, ctx):
        "Check server settings"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        emb = discord.Embed(description=f"• **Emoji:** {settings['emoji']}\n• **Colour:** `{str(discord.Colour(settings['colour']))}`\n• **Timeout:** `{settings['timeout']}`", colour=settings["colour"])
        await ctx.reply(embed=emb, mention_author=False)

    @settings.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def emoji(self, ctx, emoji: discord.Emoji):
        "Change the server emoji"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        self.bot.db_cache["guilds"][ctx.guild.id]["settings"]["emoji"] = str(emoji)
        self.bot.db_cache["guilds"][ctx.guild.id]["settings"]["emoji_default"] = False

        await utils.update_data(self.bot.db, self.bot.db_cache)

        emb = discord.Embed(description = f"Emoji changed to {str(emoji)}", colour=settings["colour"])
        await ctx.reply(embed=emb, mention_author=False)

    @settings.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def colour(self, ctx, colour):
        "Change the server colour"

        init_colour = colour
        colour = f"0x{colour[1:]}"
        colour = int(colour, 16)

        settings = utils.get_settings(ctx, self.bot.db_cache)
        self.bot.db_cache["guilds"][ctx.guild.id]["settings"]["colour"] = colour

        await utils.update_data(self.bot.db, self.bot.db_cache)

        emb = discord.Embed(description = f"Colour changed to `{init_colour}`", colour=colour)
        await ctx.reply(embed=emb, mention_author=False)

    @settings.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def timeout(self, ctx, timeout: int):
        "Change the server timeout"

        settings = utils.get_settings(ctx, self.bot.db_cache)
        self.bot.db_cache["guilds"][ctx.guild.id]["settings"]["timeout"] = timeout

        await utils.update_data(self.bot.db, self.bot.db_cache)

        emb = discord.Embed(description = f"Timeout changed to `{timeout}` seconds", colour=settings["colour"])
        await ctx.reply(embed=emb, mention_author=False)

def setup(bot):
    bot.add_cog(Settings(bot))
