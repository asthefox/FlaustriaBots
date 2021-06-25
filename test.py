#import modules and setup
import discord
from discord.ext import commands
import token_loader
#import asyncio
#from threading import Thread

intents = discord.Intents().all()

glaucon_bot = commands.Bot(command_prefix='!', intents=intents)
glaucon_bot.load_extension("cog_loader")
glaucon_bot.start(token_loader.GLAUCON_TOKEN)

#loop = asyncio.get_event_loop()
#loop.create_task(glaucon_bot.start(token_loader.GLAUCON_TOKEN))
#Thread(target=loop.run_forever())