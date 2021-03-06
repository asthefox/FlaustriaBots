#import modules and setup
import discord
from discord.ext import commands
from keep_alive import keep_alive
import token_loader
import asyncio
from threading import Thread

inside_track_bot = commands.Bot(command_prefix='!')
inside_track_bot.load_extension("inside_track_bot")
inside_track_bot.load_extension("economy")
inside_track_bot.load_extension("cowyboys")

glaucon_bot = commands.Bot(command_prefix='!')
glaucon_bot.load_extension("glaucon_bot")

#start the flask server
keep_alive()

#start several bots asynchronously so they can all run off this repl
loop = asyncio.get_event_loop()
loop.create_task(inside_track_bot.start(token_loader.INSIDE_TRACK_TOKEN))
loop.create_task(glaucon_bot.start(token_loader.TOKEN))
Thread(target=loop.run_forever())