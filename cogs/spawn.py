import discord, asyncio, utils, config, datetime
from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashContext

class Spawn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spawn_loop.start()
        self.settings = dict()

    @tasks.loop(seconds=10)
    async def spawn_loop(self):
        now = datetime.datetime.utcnow()
        for msg in await utils.get_spawn_messages(self.bot.db):
            if now >= msg.date:
                settings = await utils.get_settings(self.bot.db, msg.guild)
                guild = self.bot.get_guild(msg.guild)
                channel = guild.get_channel(msg.channel)
                message = await channel.fetch_message(msg.message)

                await message.remove_reaction(msg.emoji, guild.me)
                await utils.remove_timer(self.bot.db, msg.message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.guild_id or payload.member.bot:
            return

        settings = await utils.get_settings(self.bot.db, payload.guild_id)

        if settings["emoji"] in config.emojis.default:
            if str(payload.emoji) not in config.emojis.default:
                return
        else:
            if str(payload.emoji) != settings["emoji"]:
                return

        if await utils.check_message_spawn(self.bot.db, payload.message_id):
            await utils.add_cookies(self.bot.db, payload.user_id, payload.guild_id, 1)
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            await msg.clear_reaction(payload.emoji)

    @commands.Cog.listener()
    async def on_message(self, message):
        for word in ["spongebob", "sponge bob", "sponj bob", "sponjbob"]:
            if word in message.content.lower():
                await message.reply("https://www.youtube.com/watch?v=68mb97t87y4")
                break

        if not message.guild or message.author.bot:
            return

        if await utils.get_spawn_status(self.bot.db, message.guild.id) == "enabled":
            if await utils.is_ignored(self.bot.db, message.channel.id):
                return
            if await utils.calc_spawn(self.bot.db, message.guild.id):
                settings = await utils.get_settings(self.bot.db, message.guild.id)
                await message.add_reaction(settings["emoji"])
                await utils.add_timer(self.bot.db, message.guild.id, message.channel.id, message.id, datetime.datetime.utcnow() + datetime.timedelta(seconds=settings["timeout"]), settings["emoji"])

    @commands.command(name="enable-spawn", aliases=["enablespawn"])
    @commands.has_permissions(manage_guild=True)
    async def enable_spawn(self, ctx):
        "Enable the spawn of cookies in your server"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        spawn_enabled = await utils.get_spawn_status(self.bot.db, ctx.guild.id) == "enabled"
        if spawn_enabled:
            return await utils.error(ctx, "Spawning cookies for this server are already enabled")

        await utils.enable_spawn(self.bot.db, ctx.guild.id)
        await utils.success(ctx, "Spawning cookies enabled for this server", settings["colour"])

    @commands.command(name="disable-spawn", aliases=["disablespawn"])
    @commands.has_permissions(manage_guild=True)
    async def disable_spawn(self, ctx):
        "Disable spawning cookies in your server"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        spawn_enabled = await utils.get_spawn_status(self.bot.db, ctx.guild.id)
        if spawn_enabled == "enabled":
            return await utils.error(ctx, "Spawning cookies for this server are already disabled")

        await utils.disable_spawn(self.bot.db, ctx.guild.id)
        await utils.success(ctx, "Spawning cookies disabled for this server", settings["colour"])

    @commands.command(name="spawn-rate", aliases=["spawnrate"])
    @commands.has_permissions(manage_guild=True)
    async def spawn_rate(self, ctx, perc):
        "Edit the spawn rate"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)
        if "%" in perc:
            if perc[:-1].isdigit():
                perc = int(perc[:-1])
        elif perc.isdigit():
            perc = int(perc)
            if perc not in range(1, 61):
                return await utils.error(ctx, "Please specify a percentage between `1%` and `60%`")
        else:
            return await utils.error(ctx, "Please specify a percentage between `1%` and `60%`")

        await utils.edit_spawn_rate(self.bot.db, ctx.guild.id, perc)
        await utils.success(ctx, f"Spawn rate updated to `{perc}%`")

    @commands.command(name="ignore-channel", aliases=["ignorechannel", "ignore-spawn", "ignorespawn"])
    @commands.has_permissions(manage_guild=True)
    async def ignore_channel(self, ctx, *, channel: discord.TextChannel):
        "Block cookies from spawning in a channel"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        if await utils.is_ignored(self.bot.db, channel.id):
            return await utils.error(ctx, f"{channel.mention} is already ignored!")

        await utils.add_ignored_channel(self.bot.db, channel.id)
        await utils.success(ctx, f"Cookies won't spawn in {channel.mention}")

    @commands.command(name="allow-channel", aliases=["allowchannel", "allow-spawn", "allowspawn"])
    @commands.has_permissions(manage_guild=True)
    async def allow_channel(self, ctx, *, channel: discord.TextChannel):
        "Allow cookies ot spawn in a channel"

        settings = await utils.get_settings(self.bot.db, ctx.guild.id)

        if not await utils.is_ignored(self.bot.db, channel.id):
            return await utils.error(ctx, f"{channel.mention} isn't ignored!")

        await utils.remove_ignored_channel(self.bot.db, channel.id)
        await utils.success(ctx, f"Cookies will now spawn in {channel.mention}")

def setup(bot):
    bot.add_cog(Spawn(bot))
