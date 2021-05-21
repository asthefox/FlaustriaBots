import discord
from discord.ext import commands
import token_loader

class KMines(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
          if guild:
              print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
          else:
              print(f"Can't connect to guild:{guild}")

    @commands.command(name="mine")
    async def mine(self, ctx, arg):
      if not arg:
        await ctx.send(f'Please enter a number to mine. (example - !mine 2527)')
      await ctx.send(f'mining {arg}')
    

def setup(bot):
    bot.add_cog(KMines(bot))