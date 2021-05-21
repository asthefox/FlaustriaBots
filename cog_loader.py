import discord
from discord.ext import commands
import token_loader

class CogLoader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.guild_token = token_loader.GUILD

    @commands.Cog.listener()
    async def on_ready(self):
        #guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
        for guild in self.bot.guilds:
          if guild:
              print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
          else:
              print(f"Can't connect to guild:{guild}")

    @commands.command(name="reload")
    async def reload_extension(self, ctx, arg):
      self.bot.reload_extension(arg)  
      await ctx.send(f'reloading  {arg}')

    @commands.command(name="load")
    async def load_extension(self, ctx, arg):
      self.bot.load_extension(arg)  
      await ctx.send(f'loading  {arg}')

    @commands.command(name="unload")
    async def unload_extension(self, ctx, arg):
      self.bot.unload_extension(arg)  
      await ctx.send(f'unloading  {arg}')
    

def setup(bot):
    bot.add_cog(CogLoader(bot))