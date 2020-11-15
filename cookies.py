# ⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆ 
# ⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠁⠸⣼⡿ 
# ⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀ 
# ⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
# ⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉

import discord, os, functools
from discord.ext import commands
from datetime import datetime

def betterEmbed(**para):
    EMBED_ATTRIBUTES = ('title', 'description', 'url', 'color', 'timestamp')
    EMBED_SETS = ('image', 'thumbnail', 'footer_text', 'footer_icon_url', 'author_name', 'author_icon_url')

    ATTRIBUTES_DICT = {argv: para[argv] for argv in para if argv in EMBED_ATTRIBUTES}
    SETS_DICT = {argv: para[argv] for argv in para if argv in EMBED_SETS}
    embed = discord.Embed(**ATTRIBUTES_DICT)   
    if SETS_DICT:
        for item, value in SETS_DICT.items():
              if item == EMBED_SETS[0]:
                    embed.set_image(url=value)
              elif item == EMBED_SETS[1]:
                    embed.set_thumbnail(url=value)
              elif item == EMBED_SETS[2]:
                    embed.set_footer(text=value)
              elif item == EMBED_SETS[3]:
                  if embed.footer.text:
                      embed.footer.icon_url=value
                  else:
                      pass
              elif item == EMBED_SETS[4]:
                    embed.set_author(name=value)
              elif item == EMBED_SETS[5]:
                  if embed.author.name:
                      embed.author.icon_url=value
                  else:
                      pass

    return embed

async def quickembed(ctx, text):
    "Make a quick embed (automatically sends it)"
    emb = discord.Embed(description = text, colour = 0xd8ad6a)
    await ctx.channel.send(embed = emb)

class Git:
    def __init__(self, loop):
        self.loop = loop

    def sync_pull(self):
        os.system("git pull origin master")

    def sync_push(self, commit):
        os.system("git add .")
        os.system(f'git commit -m "{commit}"')
        os.system("git push origin master")

    async def pull(self):
        sync_process = functools.partial(self.sync_pull)
        await self.loop.run_in_executor(None, sync_process)

    async def push(self, commit="auto push"):
        sync_process = functools.partial(self.sync_push, commit)
        await self.loop.run_in_executor(None, sync_process)

    
