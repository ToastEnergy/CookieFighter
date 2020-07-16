import discord
from discord.ext import commands, tasks
import asyncio
from discord.ext.commands.cooldowns import BucketType
import os
import traceback
import random
import time
from datetime import datetime
import aiosqlite

class Cookie(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot

  @commands.command(aliases = ["cookies", "c"])
  @commands.guild_only()
  @commands.max_concurrency(1, BucketType.channel)
  @commands.cooldown(1, 5, BucketType.user)
  async def cookie(self, ctx):

    "Spawn a cookie in the chat, first one to take it wins!"

    count = discord.Embed(title = "**3**", colour = self.bot.colour)
    count.set_footer(text = "First one to take the cookie wins🍪!")

    msg = await ctx.send(embed = count)
    number = 2
    await asyncio.sleep(1)
    for a in range(2):
      count.title = f"**{number}**"
      await msg.edit(embed = count)
      number -= 1
      await asyncio.sleep(1)

    emb = discord.Embed(description = f"First one to take the cookie wins{self.bot.cookie}!", colour = self.bot.colour)
    await msg.edit(embed = emb)
    await msg.add_reaction(self.bot.cookie)

    def check(reaction, user):
      return user.bot is False and str(reaction.emoji) == self.bot.cookie and reaction.message.id == msg.id

    start = time.perf_counter()
    await asyncio.sleep(0.25)
    msg0 = await self.bot.wait_for("reaction_add", check = check)
    end = time.perf_counter()
    duration = (end - start) 
    emb.set_author(name = "We have a winner!", icon_url = str(msg0[1].avatar_url_as(static_format = "png")))
    emb.description = f"{msg0[1].mention} won and ate the cookie {self.bot.cookie} in `{duration:.2f}` seconds!"
    await msg.edit(embed = emb)

    winner = str(msg0[1].id)
      
    async with aiosqlite.connect("data/db.db") as db:
      try:
        data = await db.execute(f"SELECT * from '{winner}'")
        data = await data.fetchall()
        final_data = int(data[0][0]) + 1
        await db.execute(f"UPDATE '{winner}' set cookies = '{final_data}'")
        await db.commit()
      except aiosqlite.OperationalError:
        await db.execute(f"CREATE table '{winner}' (cookies id)")
        await db.execute(f"INSERT into '{winner}' (cookies) values ('1')")
        await db.execute(f"INSERT into ids (ids) values ('{winner}')")
        await db.commit()

    await asyncio.sleep(1.5)
    try:
      msg = await msg.channel.fetch_message(msg.id)
      users = await msg.reactions[0].users().flatten()
      others = "\n".join([a.mention for a in users if a.id != int(winner) and a.bot is False])

      if len(others) >= 1:
        emb.description = f"{msg0[1].mention} won and ate the cookie {self.bot.cookie} in `{duration:.2f}` seconds!\n\nOther players:\n{others}"
        await msg.edit(embed = emb)    
      
    except:
      print(traceback.print_exc())

  @commands.command()
  @commands.guild_only()
  @commands.max_concurrency(1, BucketType.channel)
  @commands.cooldown(1, 5, BucketType.user) 
  async def milk(self, ctx):

    "Spawn a milk in the chat, first one to take it wins!"

    count = discord.Embed(title = "**3**", colour = self.bot.colour)
    count.set_footer(text = "First one to take the milk wins🥛!")

    msg = await ctx.send(embed = count)
    number = 2
    await asyncio.sleep(1)
    for a in range(2):
      count.title = f"**{number}**"
      await msg.edit(embed = count)
      number -= 1
      await asyncio.sleep(1)

    emb = discord.Embed(description = f"First one to take the cookie wins{self.bot.milk}!", colour = self.bot.colour)
    await msg.edit(embed = emb)
    await msg.add_reaction(self.bot.milk)

    def check(reaction, user):
      return user.bot is False and str(reaction.emoji) == self.bot.milk and reaction.message.id == msg.id

    start = time.perf_counter()
    await asyncio.sleep(0.25)
    msg0 = await self.bot.wait_for("reaction_add", check = check)
    end = time.perf_counter()
    duration = (end - start) 
    emb.set_author(name = "We have a winner!", icon_url = str(msg0[1].avatar_url_as(static_format = "png")))
    emb.description = f"{msg0[1].mention} won and drunk the milk {self.bot.milk} in `{duration:.2f}` seconds!!"
    await msg.edit(embed = emb)

    winner = str(msg0[1].id)
      
    async with aiosqlite.connect("data/db.db") as db:
      try:
        data = await db.execute(f"SELECT * from '{winner}'")
        data = await data.fetchall()
        final_data = int(data[0][0]) + 1
        await db.execute(f"UPDATE '{winner}' set cookies = '{final_data}'")
        await db.commit()
      except aiosqlite.OperationalError as e:
        await db.execute(f"CREATE table '{winner}' (cookies id)")
        await db.execute(f"INSERT into '{winner}' (cookies) values ('1')")
        await db.execute(f"INSERT into ids (ids) values ('{winner}')")
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
  async def leaderboard(self, ctx):
    "Top Cookie users"

    stats = {}

    async with aiosqlite.connect("data/db.db") as db:
      data = await db.execute("SELECT * from ids")
      data = await data.fetchall()

      for a in data:
        data = await db.execute(f"SELECT * from '{a[0]}'")
        data = await data.fetchall()
        stats[str(a[0])] = int(data[0][0])
    
    lb = sorted(stats, key=lambda x : stats[x], reverse=True)

    res = ""

    counter = 0

    for a in lb:

      if counter >= 10:
        pass
      
      else:
        u = self.bot.get_user(int(a))
        if u:
          counter += 1
          res += f"\n**{counter}.** `{str(u)}` - **{stats[str(a)]} {self.bot.cookie}**"

    emb = discord.Embed(description = res, colour = self.bot.colour)
    emb.set_author(name = "Global Leaderboard", icon_url = "https://cookiefighter.github.io/cdn/cookie_gif.gif")
    await ctx.send(embed = emb)

  @leaderboard.command(aliases = ["guild"], invoke_without_command = True)
  async def server(self, ctx):
    "Top Cookie users in the actual server"

    stats = {}

    async with aiosqlite.connect("data/db.db") as db:
      data = await db.execute("SELECT * from ids")
      data = await data.fetchall()

      for a in data:
        data = await db.execute(f"SELECT * from '{a[0]}'")
        data = await data.fetchall()
        stats[str(a[0])] = int(data[0][0])
    
    lb = sorted(stats, key=lambda x : stats[x], reverse=True)

    res = ""

    counter = 0

    for a in lb:

      if counter >= 10:
        pass
      
      else:
        u = self.bot.get_user(int(a))
        if u:
          if u.id in [a.id for a in ctx.guild.members]:
            counter += 1
            res += f"\n**{counter}.** `{str(u)}` - **{stats[str(a)]} {self.bot.cookie}**"

    emb = discord.Embed(description = res, colour = self.bot.colour)
    emb.set_author(name = f"{ctx.guild.name} Leaderboard", icon_url = str(ctx.guild.icon_url_as(static_format = "png")))
    await ctx.send(embed = emb)

  @commands.command(aliases = ["stat", "info", "bal", "balance"])
  async def stats(self, ctx, *, user: discord.User = None):
    "Check User stats"
    
    user = user or ctx.author

    async with aiosqlite.connect("data/db.db") as db:
      try:
        data = await db.execute(f"SELECT * from '{user.id}'")
        data = await data.fetchall()
        cookies = int(data[0][0])
      except aiosqlite.OperationalError:
        cookies = 0
      await db.commit()
      await db.close()

    emb = discord.Embed(description = f"**{cookies}** Cookies {self.bot.cookie}!", colour = self.bot.colour)
    emb.set_author(name = user.name, icon_url = user.avatar_url_as(static_format="png"))

    await ctx.send(embed = emb)

  @commands.command(name='type')
  @commands.guild_only()
  @commands.max_concurrency(1, BucketType.channel)
  @commands.cooldown(1, 5, BucketType.user) 
  async def _type(self, ctx):
    "First one to send the cookie emoji wins!"

    count = discord.Embed(title = "**3**", colour = self.bot.colour)
    count.set_footer(text = "First one to send a cookie wins🍪!")
    NotFound = discord.Embed(description = "<a:fail:727212831782731796> someone deleted my message and I can't continue the game!", colour = self.bot.colour)

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

    emb = discord.Embed(description = f"First one to send a cookie in the chat wins{self.bot.cookie}!", colour = self.bot.colour)
    try:
      await msg.edit(embed = emb)
    except discord.NotFound:
      return await ctx.send(embed = NotFound)

    def check(msg1):
      return not msg1.author.bot and msg1.channel.id == ctx.channel.id  and msg1.content == "🍪" or msg1.content == self.bot.cookie
    
    start = time.perf_counter()
    await asyncio.sleep(0.25)
    msg0 = await self.bot.wait_for("message", check = check)
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

    winner = str(msg0.author.id)

    async with aiosqlite.connect("data/db.db") as db:
      try:
        data = await db.execute(f"SELECT * from '{winner}'")
        data = await data.fetchall()
        final_data = int(data[0][0]) + 1
        await db.execute(f"UPDATE '{winner}' set cookies = '{final_data}'")
        await db.commit()
      except aiosqlite.OperationalError:
        await db.execute(f"CREATE table '{winner}' (cookies id)")
        await db.execute(f"INSERT into '{winner}' (cookies) values ('1')")
        await db.execute(f"INSERT into ids (ids) values ('{winner}')")
        await db.commit()
    
  @commands.command()
  @commands.max_concurrency(1, BucketType.channel)
  async def party(self, ctx):
    "Make a Party with some friends and play a random game!"

    GREENTICK = self.bot.get_emoji(726040431539912744)
    REDTICK = self.bot.get_emoji(727212831782731796 )
    EMOJIS = [GREENTICK, REDTICK]
    # MISSIONS_AND_ANSWERS = {f"First one to eat the cookie wins{self.bot.cookie}!": ["REACTION", self.bot.cookie], f"First one to drink the milk wins{self.bot.milk}!": ["REACTION", self.bot.milk]}
    MISSIONS_AND_ANSWERS = {'Who first sends the cookie emoji, win!': ["🍪", "<:mc_cookie:726184620164382741>"], "What we are drinking with cookies?": ["🥛", "milk"], f"First one to take the cookie wins{self.bot.cookie}!": ["REACTION", self.bot.cookie], f"First one to eat the milk wins{self.bot.milk}!": ["REACTION", self.bot.milk]}
    SECONDS = 10.0
    NotFound = discord.Embed(description = "<a:fail:727212831782731796> someone deleted my message and I can't continue the game!", colour = self.bot.colour)

    description=f"{GREENTICK} `:` JOIN THE PARTY \n{REDTICK} `:` ABORT AFTER JOINING"
    e = discord.Embed(title="**Cookies Party Missions 🎉**, are you ready?", description=description, timestamp=ctx.message.created_at, colour = self.bot.colour)
    e.set_footer(text=f'You have {int(SECONDS)} seconds from')
    msg = await ctx.send(embed=e)
    [await msg.add_reaction(str(e)) for e in EMOJIS]

    PARTY_MEMBERS = list()

    @tasks.loop(seconds=2)
    async def partymembers_loop(_msg):
        if not PARTY_MEMBERS:
            return 

        PARTY_MENTINOS = '\n'.join(list((msg.guild.get_member(member_id)).mention for member_id in PARTY_MEMBERS))
        e = msg.embeds[0].copy()
        e.description = f"{description} \n\n__**PARTY PARTICIPANTS**__: \n{PARTY_MENTINOS}"
        await msg.edit(embed=e)

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
          emb = discord.Embed(title = f"{REDTICK} **Too few players**", description = f"At least 2 players are required to start a party!", colour = self.bot.colour)
          try:
            await msg.clear_reactions()
          except:
            pass
          return await msg.edit(embed = emb)

        mission, answer = random.choice(list(MISSIONS_AND_ANSWERS.items()))
        e = discord.Embed(title='Prepare to your mission! 5 seconds!', colour = self.bot.colour)
        try:
          await msg.clear_reactions()
        except:
          pass
        await msg.edit(embed=e)
        await asyncio.sleep(5)
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
            emb = discord.Embed(description = f"I am sorry, but nobody won :/", colour = self.bot.colour)
            return await ctx.send(embed = emb)

          try:
            await msg.delete()
          except discord.NotFound:
            return await ctx.send(embed = NotFound)
          members = [ctx.guild.get_member(a) for a in PARTY_MEMBERS]
          e = discord.Embed(title="**Cookies Party Missions 🎉**", description="{} Participants:\n{}".format(len(PARTY_MEMBERS), '\n'.join([a.mention for a in members])), timestamp=datetime.utcnow(), colour = self.bot.colour)
          e.set_author(name=f"{user.display_name} Won in {duration:.2f} seconds!🎉", icon_url = str(user.avatar_url_as(static_format = "png")))
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
            emb = discord.Embed(description = f"I am sorry, but nobody knows the answer :/ \nThe answer was **||{answer[0]}||**", colour = self.bot.colour)
            return await ctx.send(embed = emb)
          else:
              try:
                await msg.delete()
              except discord.NotFound:
                return await ctx.send(embed = NotFound)
              members = [ctx.guild.get_member(a) for a in PARTY_MEMBERS]
              e = discord.Embed(title="**Cookies Party Missions 🎉**", description="{} Participants:\n{}".format(len(PARTY_MEMBERS), '\n'.join([a.mention for a in members])), timestamp=datetime.utcnow(), colour = self.bot.colour)
              e.set_author(name=f"{message.author.display_name} Won in {duration:.2f} seconds!🎉", icon_url=message.author.avatar_url)
              e.set_footer(text='The party ends at')
              msg = await ctx.send(embed=e)
              try:
                await message.add_reaction("🎉")
              except:
                pass
              winner = str(message.author.id)
      
        async with aiosqlite.connect("data/db.db") as db:
          try:
            data = await db.execute(f"SELECT * from '{winner}'")
            data = await data.fetchall()
            final_data = int(data[0][0]) + 1
            await db.execute(f"UPDATE '{winner}' set cookies = '{final_data}'")
            await db.commit()
          except aiosqlite.OperationalError:
            await db.execute(f"CREATE table '{winner}' (cookies id)")
            await db.execute(f"INSERT into '{winner}' (cookies) values ('1')")
            await db.execute(f"INSERT into ids (ids) values ('{winner}')")
            await db.commit()
def setup(bot):
    bot.add_cog(Cookie(bot))