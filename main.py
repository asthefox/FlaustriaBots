#import modules and setup
import discord
from discord.ext import commands
from keep_alive import keep_alive
import token_loader
import asyncio
from threading import Thread


intents = discord.Intents().all()

inside_track_bot = commands.Bot(command_prefix='IT!')
#inside_track_bot.load_extension("inside_track_bot")
#inside_track_bot.load_extension("economy")
#inside_track_bot.load_extension("cowyboys")

ase_bot = commands.Bot(command_prefix='ASE!')
#ase_bot.load_extension("news_bot")

glaucon_bot = commands.Bot(command_prefix='!', intents=intents)
glaucon_bot.load_extension("cog_loader")

inquisitor_bot = commands.Bot(command_prefix='!', intents=intents)
inquisitor_bot.load_extension("cog_loader")

#start the flask server
keep_alive()

#start several bots asynchronously so they can all run off this repl
loop = asyncio.get_event_loop()
loop.create_task(inside_track_bot.start(token_loader.INSIDE_TRACK_TOKEN))
loop.create_task(ase_bot.start(token_loader.ASE_TOKEN))
loop.create_task(glaucon_bot.start(token_loader.GLAUCON_TOKEN))
loop.create_task(inquisitor_bot.start(token_loader.INQUISITOR_TOKEN))
Thread(target=loop.run_forever())