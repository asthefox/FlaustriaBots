#import modules and setup
import discord
from discord.ext import commands
from keep_alive import keep_alive
import token_loader


bot = commands.Bot(command_prefix='!')

#keep_alive()
bot.load_extension("glaucon_bot")
bot.run(token_loader.TOKEN)

