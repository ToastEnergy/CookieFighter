import discord, utils, config
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.ConversionError):
            pass
        elif isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.PrivateMessageOnly):
                pass
            elif isinstance(error, commands.NoPrivateMessage):
                pass
            elif isinstance(error, commands.CheckAnyFailure):
                pass
            elif isinstance(error, commands.NotOwner):
                pass
            elif isinstance(error, commands.MissingPermissions):
                pass
            elif isinstance(error, commands.BotMissingPermissions):
                pass
            elif isinstance(error, commands.MissingRole):
                pass
            elif isinstance(error, commands.BotMissingRole):
                pass
            elif isinstance(error, commands.MissingAnyRole):
                pass
            elif isinstance(error, commands.BotMissingAnyRole):
                pass
            elif isinstance(error, commands.NSFWChannelRequired):
                pass
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.DisabledCommand):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            pass
        elif isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                pass
            elif isinstance(error, commands.ArgumentParsingError):
                if isinstance(error, commands.UnexpectedQuoteError):
                    pass
                elif isinstance(error, commands.InvalidEndOfQuotedStringError):
                    pass
                elif isinstance(error, commands.ExpectedClosingQuoteError):
                    pass
            elif isinstance(error, commands.BadArgument):
                if isinstance(error, commands.MessageNotFound):
                    pass
                elif isinstance(error, commands.MemberNotFound):
                    await utils.error(ctx, f"Couldn't find member `{error.argument}`")
                elif isinstance(error, commands.GuildNotFound):
                    pass
                elif isinstance(error, commands.UserNotFound):
                    pass
                elif isinstance(error, commands.ChannelNotFound):
                    pass
                elif isinstance(error, commands.ChannelNotReadable):
                    pass
                elif isinstance(error, commands.BadColourArgument):
                    pass
                elif isinstance(error, commands.RoleNotFound):
                    pass
                elif isinstance(error, commands.BadInviteArgument):
                    pass
                elif isinstance(error, commands.EmojiNotFound):
                    pass
                elif isinstance(error, commands.PartialEmojiConversionFailure):
                    pass
                elif isinstance(error, commands.BadBoolArgument):
                    pass
            elif isinstance(error, commands.TooManyArguments):
                pass
        elif isinstance(error, commands.CommandOnCooldown):
            pass
        elif isinstance(error, commands.MaxConcurrencyReached):
            pass
        elif isinstance(error, commands.errors.CommandOnCooldown):
            pass
        elif isinstance(error, commands.MaxConcurrencyReached):
            pass
        elif isinstance(error, commands.errors.ChannelNotFound):
            pass
        elif isinstance(error, commands.ExtensionError):
            if isinstance(error, commands.ExtensionAlreadyLoaded):
                pass
            elif isinstance(error, commands.ExtensionNotLoaded):
                pass
            elif isinstance(error, commands.NoEntryPointError):
                pass
            elif isinstance(error, commands.ExtensionFailed):
                pass
            elif isinstance(error, commands.ExtensionNotFound):
                pass
        elif isinstance(error, commands.CommandRegistrationError):
            pass

def setup(bot):
    bot.add_cog(Events(bot))
