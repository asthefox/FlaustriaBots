#import modules and setup
import discord
from discord.ext import commands
import token_loader
import asyncio
from threading import Thread

# This is all required to be awaited now, so it's in a function
async def setup_bots():

	await inside_track_bot.load_extension("economy")
	await inside_track_bot.load_extension("kmines")
	#inside_track_bot.load_extension("inside_track_bot")
	await inside_track_bot.load_extension("cowyboys")
	await inside_track_bot.load_extension("leaderboards")

	await ase_bot.load_extension("news_bot")
	#ase_bot.load_extension("cog_loader")

	#glaucon_bot = commands.Bot(command_prefix='!', intents=intents)
	#glaucon_bot.load_extension("cog_loader")

	await inquisitor_bot.load_extension("personality_test")
	await inquisitor_bot.load_extension("check_invites")
	await inquisitor_bot.load_extension("key_sender")

intents = discord.Intents().all()
inside_track_bot = commands.Bot(command_prefix='!', intents=intents)
ase_bot = commands.Bot(command_prefix='ASE!', intents=intents)
inquisitor_bot = commands.Bot(command_prefix='IQ!', intents=intents)
asyncio.run(setup_bots())

#start several bots asynchronously so they can all run off this repl


try:
	loop = asyncio.get_event_loop()
except:
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

loop.create_task(inside_track_bot.start(token_loader.INSIDE_TRACK_TOKEN))
loop.create_task(ase_bot.start(token_loader.ASE_TOKEN))
#loop.create_task(glaucon_bot.start(token_loader.GLAUCON_TOKEN))
loop.create_task(inquisitor_bot.start(token_loader.INQUISITOR_TOKEN))
Thread(target=loop.run_forever())
