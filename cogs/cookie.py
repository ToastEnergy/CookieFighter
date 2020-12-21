import discord, cookies, os, traceback, asyncio, random, time, aiosqlite, dbl, datetime
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from typing import Union

class Cookie(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    self.dblpy = dbl.DBLClient(self.bot, str(os.environ.get("topgg")))
    self.database = cookies.Database()

  @commands.command(aliases = ["cookies", "c"])
  @commands.guild_only()
  @commands.max_concurrency(1, BucketType.channel)
  @commands.cooldown(1, 5, BucketType.user)
  @cookies.check_perms()
  async def cookie(self, ctx):
    "Spawn a cookie in the chat, first one to take it wins!"

    opt = await cookies.guild_settings(ctx.guild.id)

    timeout = opt["timeout"]
    emoji = opt["emoji"]
    if opt["emoji_default"] == False:
      emoji = self.bot.get_emoji(emoji)

      if not emoji:
        emoji = random.choice([self.bot.gocciola, self.bot.cookie, self.bot.oreo])

      else:
        emoji = str(emoji)

    colour = int(opt["colour"])

    count = discord.Embed(title = "**3**", colour = colour)
    count.set_footer(text = "First one to take the cookie wins 🍪!")

    msg = await ctx.send(embed = count)
    number = 2
    await asyncio.sleep(1)
    for a in range(2):
      count.title = f"**{number}**"
      await msg.edit(embed = count)
      number -= 1
      await asyncio.sleep(1)

    emb = discord.Embed(description = f"First one to take the cookie wins {emoji}!", colour = colour)
    await msg.edit(embed = emb)
    await msg.add_reaction(emoji)

    def check(reaction, user):
      return user.bot is False and str(reaction.emoji) == emoji and reaction.message.id == msg.id

    start = time.perf_counter()
    await asyncio.sleep(0.25)
    try:
      msg0 = await self.bot.wait_for("reaction_add", check = check, timeout = timeout)

    except asyncio.TimeoutError:
      emb.description = "Nobody ate the cookie!"
      try:
        await msg.edit(embed = emb)
        await msg.remove_reaction(emoji, ctx.guild.me)
      except:
        emb.description = "The original message got deleted, I can't end the game!"
        await ctx.send(embed = emb)

      return

    end = time.perf_counter()
    duration = (end - start) 
    emb.set_author(name = "We have a winner!", icon_url = str(msg0[1].avatar_url_as(static_format = "png")))
    
    emb.description = f"{msg0[1].mention} won and ate the cookie {emoji} in `{duration:.2f}` seconds!"
    await msg.edit(embed = emb)

    winner = str(msg0[1].id)

    await self.database.add_cookies(winner, 1, ctx.message.id, duration)
    
    await asyncio.sleep(1.5)
    try:
      msg = await msg.channel.fetch_message(msg.id)
      users = await msg.reactions[0].users().flatten()
      others = "\n".join([a.mention for a in users if a.id != int(winner) and a.bot is False])

      if len(others) >= 1:
        emb.description = f"{msg0[1].mention} won and ate the cookie {emoji} in `{duration:.2f}` seconds!\n\nOther players:\n{others}"
        await msg.edit(embed = emb)    
      
    except:
      print(traceback.print_exc())

  @commands.command(aliases = ["m"])
  @commands.guild_only()
  @commands.max_concurrency(1, BucketType.channel)
  @commands.cooldown(1, 5, BucketType.user) 
  @cookies.check_perms()
  async def milk(self, ctx):
    "Spawn a milk in the chat, first one to take it wins!"

    opt = await cookies.guild_settings(ctx.guild.id)

    timeout = opt["timeout"]
    colour = int(opt["colour"])

    count = discord.Embed(title = "**3**", colour = colour)
    count.set_footer(text = "First one to take the milk wins 🥛!")

    msg = await ctx.send(embed = count)
    number = 2
    await asyncio.sleep(1)
    for a in range(2):
      count.title = f"**{number}**"
      await msg.edit(embed = count)
      number -= 1
      await asyncio.sleep(1)

    emb = discord.Embed(description = f"First one to take the cookie wins {self.bot.milk}!", colour = colour)
    await msg.edit(embed = emb)
    await msg.add_reaction(self.bot.milk)

    def check(reaction, user):
      return user.bot is False and str(reaction.emoji) == self.bot.milk and reaction.message.id == msg.id

    start = time.perf_counter()
    await asyncio.sleep(0.25)
    try:
      msg0 = await self.bot.wait_for("reaction_add", check = check, timeout = timeout)

    except asyncio.TimeoutError:
      emb.description = "Nobody drunk the milk!"
      try:
        await msg.edit(embed = emb)
        await msg.remove_reaction(self.bot.milk, ctx.guild.me)
      except:
        emb.description = "The original message got deleted, I can't end the game!"
        await ctx.send(embed = emb)

      return
    end = time.perf_counter()
    duration = (end - start) 
    emb.set_author(name = "We have a winner!", icon_url = str(msg0[1].avatar_url_as(static_format = "png")))
    emb.description = f"{msg0[1].mention} won and drunk the milk {self.bot.milk} in `{duration:.2f}` seconds!!"
    await msg.edit(embed = emb)

    winner = str(msg0[1].id)

    async with aiosqlite.connect("data/db.db") as db:
      data = await db.execute(f"SELECT * from users where user = '{winner}'")
      data = await data.fetchall()

      if len(data) == 0:
        await db.execute(f"INSERT into users (user, cookies) VALUES ('{winner}', 1)")

      else:
        final_data = int(data[0][1]) + 1
        await db.execute(f"UPDATE users set cookies = {final_data} where user = {winner}")

      await db.execute(f"INSERT into results (user, message, time) VALUES ('{winner}', '{ctx.message.id}', '{duration:.4f}')")
      await db.commit()

    await asyncio.sleep(1.5)
    try:
      msg = await msg.channel.fetch_message(msg.id)
      users = await msg.reactions[0].users().flatten()
      others = "\n".join([a.mention for a in users if a.id != int(winner) and a.bot is False])

      if len(others) >= 1:
        emb.description = f"{msg0[1].mention} won and drunk the milk {self.bot.milk} in `{duration:.2f}` seconds!\n\nOther players:\n{others}"
        await msg.edit(embed = emb)    
      
    except:
      print(traceback.print_exc())

  @commands.group(aliases = ["lb", "top"], invoke_without_command = True)
  @cookies.check_perms()
  async def leaderboard(self, ctx, number: Union[int, float] = None):
    "Top Cookie users, if a number is specified it will return the closest results to that number."

    await ctx.trigger_typing()

    if not ctx.guild:
      colour = self.bot.colour
      emoji = self.bot.cookie

    else:
      opt = await cookies.guild_settings(ctx.guild.id)
      colour = int(opt["colour"])
      emoji = opt["emoji"]
      if opt["emoji_default"] == False:
        emoji = self.bot.get_emoji(emoji)

        if not emoji:
          emoji = self.bot.cookie

        else:
          emoji = str(emoji)


    if number is not None:
      async with aiosqlite.connect("data/db.db") as db:
        data = await db.execute("SELECT * from results")
        data = await data.fetchall()

      lb = {}
      
      for stat in sorted(data, key=lambda d: abs(number-d[2])):
        lb[stat[1]] = {"time": stat[2], "user": stat[0]}

      res = ""

      counter = 0

      for data in lb:

        if counter >= 10:
          break
        
        else:
            u = self.bot.get_user(int(lb[data]["user"])) 

            if not u:
              try:
                u = await self.bot.fetch_user(int(lb[data]["user"]))
              except:
                u = None

            if u:
              counter += 1
              user = str(u).replace("`", "")
              res += f"\n**{counter}.** `{user}` - **{lb[data]['time']}s {self.bot.clock}**"
        
    else:
      stats = {}
      async with aiosqlite.connect("data/db.db") as db:
        data = await db.execute("SELECT * from users")
        data = await data.fetchall()

        for value in data:
          stats[str(value[0])] = int(value[1])
    
        lb = sorted(stats, key=lambda x : stats[x], reverse=True)

        res = ""

        counter = 0

        for data in lb:

          if counter >= 10:
            break
          
          else:
            u = self.bot.get_user(int(data)) 

            if not u:
              try:
                u = await self.bot.fetch_user(int(data))
              except:
                u = None
                
            if u:
              counter += 1
              user = str(u).replace("`", "")
              res += f"\n**{counter}.** `{user}` - **{stats[str(data)]} {emoji}**"

    emb = discord.Embed(description = res, colour = colour)
    emb.set_author(name = "Global Leaderboard", icon_url = "https://cookiefighter.github.io/cdn/cookie_gif.gif")
    await ctx.send(embed = emb)

  @leaderboard.command(aliases = ["guild"])
  @cookies.check_perms()
  async def server(self, ctx):
    "Top Cookie users in the actual server"

    if not ctx.guild:
      colour = self.bot.colour
      emoji = self.bot.cookie

    else:
      opt = await cookies.guild_settings(ctx.guild.id)
      colour = int(opt["colour"])
      emoji = opt["emoji"]
      if opt["emoji_default"] == False:
        emoji = self.bot.get_emoji(emoji)

        if not emoji:
          emoji = self.bot.cookie

        else:
          emoji = str(emoji)

    async with ctx.typing():
      emb = discord.Embed(title=f"{self.bot.clock} | loading...",colour=colour)
      msg = await ctx.send("due to the new discord intents this will take a while", embed = emb) 

      stats = {}
      async with aiosqlite.connect("data/db.db") as db:
        data = await db.execute("SELECT * from users")
        data = await data.fetchall()

        for value in data:
          stats[str(value[0])] = int(value[1])
    
        lb = sorted(stats, key=lambda x : stats[x], reverse=True)

        res = ""

        counter = 0

        for data in lb:

          if counter >= 10:
            break
          
          else:
            u = ctx.guild.get_member(int(data)) 

            if not u:
              try:
                u = await ctx.guild.fetch_member(int(data))
              except:
                u = None
                
            if u:
              counter += 1
              user = str(u).replace("`", "")
              res += f"\n**{counter}.** `{user}` - **{stats[str(data)]} {emoji}**"

    emb = discord.Embed(description = res, colour = colour)
    emb.set_author(name = ctx.guild.name, icon_url = str(ctx.guild.icon_url_as(static_format="png")))
    await msg.edit(embed = emb, content = None)

  @commands.command(aliases = ["stat", "info", "bal", "balance"])
  @cookies.check_perms()
  async def stats(self, ctx, user = None):
    "Check User stats"

    if not ctx.guild:
      colour = self.bot.colour
      emoji = self.bot.cookie
    
    else:
      opt = await cookies.guild_settings(ctx.guild.id)
      colour = int(opt["colour"])
      emoji = opt["emoji"]
      if opt["emoji_default"] == False:
        emoji = self.bot.get_emoji(emoji)

        if not emoji:
          emoji = self.bot.cookie

        else:
          emoji = str(emoji)

    if not user:
      user = ctx.author
    
    else:
      try:
        user = await self.bot.fetch_user(int(user))

      except:
        if ctx.message.mentions:
          try:
            user = await self.bot.fetch_user(int(ctx.message.mentions[0].id))

          except:
            return await ctx.send("user not found")

        else:
          return await ctx.send("user not found")
          
    async with aiosqlite.connect("data/db.db") as db:
      data = await db.execute(f"SELECT * from users where user = {user.id}")
      data = await data.fetchall()

      if len(data) == 0:
        cookies_ = 0
      
      else:
        cookies_ = int(data[0][1])

    emb = discord.Embed(description = f"**{cookies_}** Cookies {emoji}!", colour = colour)
    emb.set_author(name = user.name, icon_url = user.avatar_url_as(static_format="png"))

    await ctx.send(embed = emb)

  @commands.command(name='type')
  @commands.guild_only()
  @commands.max_concurrency(1, BucketType.channel)
  @commands.cooldown(1, 5, BucketType.user) 
  @cookies.check_perms()
  async def _type(self, ctx):
    "First one to send the cookie emoji wins!"

    opt = await cookies.guild_settings(ctx.guild.id)

    timeout = opt["timeout"]
    colour = int(opt["colour"])

    count = discord.Embed(title = "**3**", colour = colour)
    count.set_footer(text = "First one to send a cookie wins🍪!")
    NotFound = discord.Embed(description = "<a:fail:727212831782731796> someone deleted my message and I can't continue the game!", colour = colour)

    msg = await ctx.send(embed = count)
    number = 2
    await asyncio.sleep(1)
    for a in range(2):
      count.title = f"**{number}**"

      try:
        await msg.edit(embed = count)
      except discord.NotFound:
        return await ctx.send(embed = NotFound)

      number -= 1
      await asyncio.sleep(1)

    emb = discord.Embed(description = f"First one to send a cookie in the chat wins {self.bot.cookie}!", colour = colour)
    try:
      await msg.edit(embed = emb)
    except discord.NotFound:
      return await ctx.send(embed = NotFound)

    def check(msg1):
      return not msg1.author.bot and msg1.channel.id == ctx.channel.id  and msg1.content == "🍪" or msg1.content == self.bot.cookie
    
    start = time.perf_counter()
    await asyncio.sleep(0.25)
    try:
      msg0 = await self.bot.wait_for("message", check = check, timeout = timeout)

    except asyncio.TimeoutError:
      emb.description = "Nobody ate the cookie!"
      try:
        await msg.edit(embed = emb)
        await msg.remove_reaction(self.bot.cookie, ctx.guild.me)
      except:
        emb.description = "The original message got deleted, I can't end the game!"
        await ctx.send(embed = emb)

      return

    end = time.perf_counter()
    duration = (end - start) 
    emb.set_author(name = "We have a winner!", icon_url = str(msg0.author.avatar_url_as(static_format = "png")))
    emb.description = f"{msg0.author.mention} won and ate the cookie {self.bot.cookie} in `{duration:.2f}` seconds!"

    try:
      await msg.edit(embed = emb)
    except discord.NotFound:
        return await ctx.send(embed = NotFound)

    try:
      await msg0.add_reaction("🎉")
    except:
      pass

    winner = int(msg0.author.id)

    async with aiosqlite.connect("data/db.db") as db:
      data = await db.execute(f"SELECT * from users where user = '{winner}'")
      data = await data.fetchall()

      if len(data) == 0:
        await db.execute(f"INSERT into users (user, cookies) VALUES ('{winner}', 1)")

      else:
        final_data = int(data[0][1]) + 1
        await db.execute(f"UPDATE users set cookies = {final_data} where user = {winner}")
        
      await db.execute(f"INSERT into results (user, message, time) VALUES ('{winner}', '{ctx.message.id}', '{duration:.4f}')")
      await db.commit()

  @commands.command(aliases = ["p"])
  @commands.guild_only()
  @commands.max_concurrency(1, BucketType.channel)
  @cookies.check_perms()
  async def party(self, ctx):
    "Make a Party with some friends and play a random game!"
  
    check = await self.dblpy.get_user_vote(ctx.author.id)
    opt = await cookies.guild_settings(ctx.guild.id)
    colour = int(opt["colour"])

    if not check:
      if ctx.author.id in self.bot.owner_ids:
        pass
      else:
        emb = discord.Embed(title = "Please Vote!", description = f"• This command is for voters only!\n• Vote [here](https://top.gg/bot/{self.bot.user.id}/vote) and wait 1-2 minutes to use it.", url = f"https://top.gg/bot/{self.bot.user.id}/vote", colour = colour)
        return await ctx.send(embed = emb)

    GREENTICK = self.bot.get_emoji(726040431539912744)
    REDTICK = self.bot.get_emoji(727212831782731796 )
    EMOJIS = [GREENTICK, REDTICK]
    # MISSIONS_AND_ANSWERS = {f"First one to eat the cookie wins{self.bot.cookie}!": ["REACTION", self.bot.cookie], f"First one to drink the milk wins{self.bot.milk}!": ["REACTION", self.bot.milk]}
    MISSIONS_AND_ANSWERS = {'Who first sends the cookie emoji, win!': ["🍪", "<:mc_cookie:726184620164382741>"], "What we are drinking with cookies?": ["🥛", "milk"], "Which food connects black and white?": ["oreo", self.bot.oreo], f"First one to take the cookie wins {self.bot.cookie}!": ["REACTION", self.bot.cookie], f"First one to eat the milk wins {self.bot.milk}!": ["REACTION", self.bot.milk]}
    SECONDS = 10.0
    NotFound = discord.Embed(description = "<a:fail:727212831782731796> someone deleted my message and I can't continue the game!", colour = colour)

    description=f"{GREENTICK} `:` JOIN THE PARTY \n{REDTICK} `:` ABORT AFTER JOINING"
    e = discord.Embed(title="**Cookies Party Missions 🎉**, are you ready?", description=description, timestamp=ctx.message.created_at, colour = colour)
    e.set_footer(text=f'You have {int(SECONDS)} seconds from')
    msg = await ctx.send(embed=e)
    [await msg.add_reaction(str(e)) for e in EMOJIS]

    PARTY_MEMBERS = []

    @tasks.loop(seconds=2)
    async def partymembers_loop(_msg):
        if not PARTY_MEMBERS:
            return 

        PARTY_MENTIONS = []

        for user in PARTY_MEMBERS:
          u = self.bot.get_user(user)
          
          if not u:
            u = await self.bot.fetch_user(user)

          PARTY_MENTIONS.append(f"• {u.mention}")

        PARTY_MENTIONS = "\n".join(PARTY_MENTIONS)

        e = _msg.embeds[0].copy()
        e.description = f"{description} \n\n__**PARTY PARTICIPANTS**__: \n{PARTY_MENTIONS}"
        await _msg.edit(embed=e)

    def check(reaction, user):

        if reaction.emoji not in EMOJIS or reaction.message.channel.id != ctx.channel.id or reaction.message.id != msg.id or user.bot:
            return False
        if reaction.emoji.id == GREENTICK.id:
            if user.id not in PARTY_MEMBERS:
                PARTY_MEMBERS.append(user.id)
        if reaction.emoji.id == REDTICK.id:
            if user.id in PARTY_MEMBERS:
                PARTY_MEMBERS.remove(user.id)
        return False

    try:
        partymembers_loop.start(msg)
        await self.bot.wait_for('reaction_add', timeout=SECONDS, check=check)

    except asyncio.TimeoutError:
        partymembers_loop.cancel()

        if len(PARTY_MEMBERS) <= 1:
          emb = discord.Embed(title = f"{REDTICK} **Too few players**", description = f"At least 2 players are required to start a party!", colour = colour)
          try:
            await msg.clear_reactions()
          except:
            pass
          return await msg.edit(embed = emb)

        mission, answer = random.choice(list(MISSIONS_AND_ANSWERS.items()))
        e = discord.Embed(title='Prepare to your mission! 5 seconds!', colour = colour)
        try:
          await msg.clear_reactions()
        except:
          pass
        await msg.edit(embed=e)
        await asyncio.sleep(5)
        e.title = None
        e.description = mission
        await msg.delete()
        msg = await ctx.send(embed=e)

        def _check(msg):
            return msg.author.id in PARTY_MEMBERS and msg.channel.id == ctx.channel.id and msg.content.lower() in answer

        if answer[0] == "REACTION":
          await msg.add_reaction(answer[1])

          def r_check(reaction, user):
            return user.bot is False and str(reaction.emoji) == answer[1] and reaction.message.id == msg.id and user.id in PARTY_MEMBERS
          
          try:
            start = time.perf_counter()
            await asyncio.sleep(0.25)
            reaction, user = await self.bot.wait_for("reaction_add", check = r_check)
            end = time.perf_counter()
            duration = (end - start)
          except asyncio.TimeoutError:
            emb = discord.Embed(description = f"I am sorry, but nobody won :/", colour = colour)
            return await ctx.send(embed = emb)

          try:
            await msg.delete()
          except discord.NotFound:
            return await ctx.send(embed = NotFound)
          # members = [ctx.guild.get_member(a) for a in PARTY_MEMBERS]
          members = []
          for id in PARTY_MEMBERS:
            u = self.bot.get_user(id)

            if not u:
              u = await self.bot.fetch_user(id)

            members.append(u)

          e = discord.Embed(title="**Cookies Party Missions 🎉**", description="{} Participants:\n{}".format(len(PARTY_MEMBERS), '\n'.join([a.mention for a in members])), timestamp=datetime.datetime.utcnow(), colour = colour)
          e.set_author(name=f"{user.name} Won in {duration:.2f} seconds!🎉", icon_url = str(user.avatar_url_as(static_format = "png")))
          e.set_footer(text='The party ends at')
          msg = await ctx.send(embed=e)
          await msg.add_reaction("🎉")
          winner = str(user.id)

        else:
          try:
            start = time.perf_counter()
            await asyncio.sleep(0.25)
            message = await self.bot.wait_for('message', timeout=SECONDS, check=_check)
            end = time.perf_counter()
            duration = (end - start)
          except asyncio.TimeoutError:
            emb = discord.Embed(description = f"I am sorry, but nobody knows the answer :/ \nThe answer was **||{answer[0]}||**", colour = colour)
            return await ctx.send(embed = emb)
          else:
              try:
                await msg.delete()
              except discord.NotFound:
                return await ctx.send(embed = NotFound)
              members = []
              for id in PARTY_MEMBERS:
                u = self.bot.get_user(id)

                if not u:
                  u = await self.bot.fetch_user(id)

                members.append(u)
              e = discord.Embed(title="**Cookies Party Missions 🎉**", description="{} Participants:\n{}".format(len(PARTY_MEMBERS), '\n'.join([a.mention for a in members])), timestamp=datetime.datetime.utcnow(), colour = colour)
              e.set_author(name=f"{message.author.display_name} Won in {duration:.2f} seconds!🎉", icon_url=message.author.avatar_url)
              e.set_footer(text='The party ends at')
              msg = await ctx.send(embed=e)
              try:
                await message.add_reaction("🎉")
              except:
                pass
              winner = str(message.author.id)

        async with aiosqlite.connect("data/db.db") as db:
          data = await db.execute(f"SELECT * from users where user = '{winner}'")
          data = await data.fetchall()

          if len(data) == 0:
            await db.execute(f"INSERT into users (user, cookies) VALUES ('{winner}', 1)")

          else:
            final_data = int(data[0][1]) + 1
            await db.execute(f"UPDATE users set cookies = {final_data} where user = {winner}")

          await db.execute(f"INSERT into results (user, message, time) VALUES ('{winner}', '{ctx.message.id}', '{duration:.4f}')")
          await db.commit()

  @commands.command(aliases = ["gift"], usage = "<user> <cookies>")
  @cookies.check_perms()
  async def send(self, ctx, user, cookies_: int):
    "Gift cookies to a user"

    if not ctx.guild:
      colour = self.bot.colour
      emoji = self.bot.cookie

    else:
      opt = await cookies.guild_settings(ctx.guild.id)
      colour = int(opt["colour"])
      emoji = opt["emoji"]
      if opt["emoji_default"] == False:
        emoji = self.bot.get_emoji(emoji)

        if not emoji:
          emoji = self.bot.cookie

        else:
          emoji = str(emoji)

    try:
      user = await self.bot.fetch_user(int(user))

    except:
      if ctx.message.mentions:
        try:
          user = await self.bot.fetch_user(int(ctx.message.mentions[0].id))

        except:
          return await ctx.send("user not found")

      else:
        return await ctx.send("user not found")

    if user.bot:
      emb = discord.Embed(description = "nah, robot don't eat cookies.", colour = colour)
      return await ctx.send(embed = emb)

    if user.id == ctx.author.id:
      emb = discord.Embed(description = "mh.. why would give yourself something you already have?", colour=colour)
      return await ctx.send(embed = emb)

    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel

    try:

      emb = discord.Embed(description = f"Are you sure you want to gift **{cookies_} {emoji}** to **{str(user)}**? Reply with `yes` if you agree.", colour = colour)
      await ctx.send(embed = emb)
      msg = await self.bot.wait_for("message", check = check, timeout = 30)

      if msg.content.lower() == "yes":
        pass 

      else:  
        emb = discord.Embed(description = "<a:fail:727212831782731796> | Aborted", colour = colour)
        return await ctx.send(embed = emb)

    except asyncio.TimeoutError:
      emb = discord.Embed(description = "<a:fail:727212831782731796> | Time out, aborted", colour = colour)
      return await ctx.send(embed = emb)

    winner = user.id
    emb = discord.Embed(description = f"Adding **{cookies_} {emoji}** to **{user.mention}**...", colour = colour)
    msg = await ctx.send(embed = emb)

    async with aiosqlite.connect("data/db.db") as db:
      data = await db.execute(f"SELECT * from users where user = {ctx.author.id}")
      data = await data.fetchall()

      if len(data) == 0:
        emb.description = "<a:fail:727212831782731796> | You don't have any cookie!"
        return await msg.edit(embed = emb)

      final_data = int(data[0][1]) - cookies_

      if final_data < 0:
        emb.description = "<a:fail:727212831782731796> | You don't have enough cookies!"
        return await msg.edit(embed = emb)

      await db.execute(f"UPDATE users set cookies = {final_data} where user = {ctx.author.id}")
      await db.commit()

      data = await db.execute(f"SELECT * from users where user = {winner}")
      data = await data.fetchall()

      if len(data) == 0:
        await db.execute(f"isnert into users (user, cookies) VALUES ({winner}, {cookies_})")
        await db.commit()
      
      else:
        final_data = int(data[0][1]) + cookies_
        await db.execute(f"UPDATE users set cookies = {final_data} where user = {winner}")
        await db.commit()

    emb.description = f"<a:check:726040431539912744> | Gifted **{cookies_} {emoji}** to **{str(user)}**!"
    await msg.edit(embed = emb)

  @commands.command()
  @cookies.check_perms()
  async def delete(self, ctx):
    "Delete all your cookies"

    if not ctx.guild:
      colour = self.bot.colour

    else:
      opt = await cookies.guild_settings(ctx.guild.id)
      colour = int(opt["colour"])

    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel

    try:

      emb = discord.Embed(description = "Are you sure you want to delete all your cookies? Reply with `yes` if you agree.", colour = colour)
      await ctx.send(embed = emb)
      msg = await self.bot.wait_for("message", check = check, timeout = 30)

      if msg.content.lower() == "yes":
        pass 

      else:  
        emb = discord.Embed(description = "<a:fail:727212831782731796> | Aborted", colour = colour)
        return await ctx.send(embed = emb)

    except asyncio.TimeoutError:
      emb = discord.Embed(description = "<a:fail:727212831782731796> | Time out, aborted", colour = colour)
      return await ctx.send(embed = emb)

    winner = str(ctx.author.id)
  
    async with aiosqlite.connect("data/db.db") as db:
          await db.execute(f"UPDATE users set cookies = 0 where user = {winner}")
          await db.commit()

    emb = discord.Embed(description = f"<a:check:726040431539912744> | Removed all your cookies.", colour = colour)
    await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Cookie(bot))
