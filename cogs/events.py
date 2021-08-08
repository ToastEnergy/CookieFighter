import discord, utils, config
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        errors = list()
        if isinstance(error, commands.ConversionError):
            errors.append("Something went wrong converting an item")
        elif isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.PrivateMessageOnly):
                errors.append("This commands works only in DMs")
            elif isinstance(error, commands.NoPrivateMessage):
                errors.append("This commands works only in servers")
            elif isinstance(error, commands.CheckAnyFailure):
                errors.append("This commands doesn't work with the current context")
            elif isinstance(error, commands.NotOwner):
                errors.append("This command is for the developers")
            elif isinstance(error, commands.MissingPermissions):
                if len(error.missing_perms) == 1:
                    errors.append(f"You are missing the `{error.missing_perms[0]}` permission")
                else:
                    errors.append(f"You are missing {' '.join([f'`{perm}`' for perm in error.missing_perms])} permissions")
            elif isinstance(error, commands.BotMissingPermissions):
                if len(error.missing_perms) == 1:
                    errors.append(f"I'm missing the `{error.missing_perms[0]}` permission")
                else:
                    errors.append(f"I'm missing {' '.join([f'`{perm}`' for perm in error.missing_perms])} permissions")
            elif isinstance(error, commands.MissingRole):
                errors.append(f"You're missing the `{error.missing_role}` role")
            elif isinstance(error, commands.BotMissingRole):
                errors.append(f"I'm missing the `{error.missing_role}` role")
            elif isinstance(error, commands.MissingAnyRole):
                if len(error.missing_roles) == 1:
                    errors.append(f"You're missing the `{error.missing_roles[0]}` role")
                else:
                    errors.append(f"You're missing {' '.join([f'`{perm}`' for perm in error.missing_roles])} roles")
            elif isinstance(error, commands.BotMissingAnyRole):
                if len(error.missing_roles) == 1:
                    errors.append(f"I'm missing the `{error.missing_roles[0]}` role")
                else:
                    errors.append(f"I'm missing {' '.join([f'`{perm}`' for perm in error.missing_roles])} roles")
            elif isinstance(error, commands.NSFWChannelRequired):
                errors.append("This command works only on NSFW channels")
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.DisabledCommand):
            erros.append("This command is currently disabled")
        elif isinstance(error, commands.CommandInvokeError):
            pass
        elif isinstance(error, commands.UserInputError):
            if isinstance(error, commands.MissingRequiredArgument):
                errors.append(f"Please specify `{error.param.name}`")
            elif isinstance(error, commands.ArgumentParsingError):
                if isinstance(error, commands.UnexpectedQuoteError):
                    errors.append(error)
                elif isinstance(error, commands.InvalidEndOfQuotedStringError):
                    errors.append(error)
                elif isinstance(error, commands.ExpectedClosingQuoteError):
                    errors.append(error)
            elif isinstance(error, commands.BadArgument):
                if isinstance(error, commands.MessageNotFound):
                    errors.append("Couldn't find that message")
                elif isinstance(error, commands.MemberNotFound):
                    errors.append(f"Couldn't find member `{error.argument}`")
                elif isinstance(error, commands.GuildNotFound):
                    errors.append(f"Couldn't find guild `{error.argument}`")
                elif isinstance(error, commands.UserNotFound):
                    errors.append(f"Couldn't find user `{error.argument}`")
                elif isinstance(error, commands.ChannelNotFound):
                    errors.append(f"Couldn't find channel `{error.argument}`")
                elif isinstance(error, commands.ChannelNotReadable):
                    errors.append(f"I don't have enough permissions to read {error.argument.mention}")
                elif isinstance(error, commands.BadColourArgument):
                    errors.append(f"{error.argument} isn't a invalid colour")
                elif isinstance(error, commands.RoleNotFound):
                    errors.append(f"Couldn't find role `{error.argument}`")
                elif isinstance(error, commands.BadInviteArgument):
                    errors.append("Invalid invite")
                elif isinstance(error, commands.EmojiNotFound):
                    errors.append(f"Couldn't find emoji **{error.argument}**")
                elif isinstance(error, commands.PartialEmojiConversionFailure):
                    errors.append(f"{error.argument} is an invalid emoji")
                elif isinstance(error, commands.BadBoolArgument):
                    errors.append(f"Couldn't convert `{error.argument}` to `True` or `False`")
            elif isinstance(error, commands.TooManyArguments):
                errors.append("You passed too many arguments")
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after = utils.get_time(round(error.retry_after))
            errors.append(f"You can use this command in {retry_after}")
        elif isinstance(error, commands.MaxConcurrencyReached):
            errors.append("This command is being used too many times")
        elif isinstance(error, commands.ExtensionError):
            if isinstance(error, commands.ExtensionAlreadyLoaded):
                errors.append("Extension is already loaded")
            elif isinstance(error, commands.ExtensionNotLoaded):
                errors.append("Extension not loaded")
            elif isinstance(error, commands.NoEntryPointError):
                errors.append("Missing `setup` function")
            elif isinstance(error, commands.ExtensionFailed):
                errors.append("Extension has loaded")
            elif isinstance(error, commands.ExtensionNotFound):
                errors.append("Extension not found")
        elif isinstance(error, commands.CommandRegistrationError):
            errors.append(f"There are 2 commands with the same name (`{error.name}`)!")

        if len(errors) == 0:
            errors.append(str(error))

        await utils.error(ctx, "\n".join(errors))

def setup(bot):
    bot.add_cog(Events(bot))
