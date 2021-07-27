import discord
from discord.ext import commands
import token_loader
import random
import database
from utilities import is_only_numbers

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

    @commands.command(name="bit-k-ticker")
    async def ticker(self, ctx):
      bitk_value = self.get_bitk_value()
      await ctx.send(f'1 bit-k is now trading at {bitk_value}k.')

    @commands.command(name="mine")
    async def mine(self, ctx, number_to_mine=None):
      if number_to_mine == None:
        await ctx.send(f'Please enter a number to mine. [example - !mine 2527]')
        return
      elif not is_only_numbers(number_to_mine):
        await ctx.send(f'{number_to_mine} is not a number. Please enter a number to mine. (Example: !mine 2527)')
        return
      elif "6" in number_to_mine:
        await ctx.send(f'||{number_to_mine}|| is a forbidden number. Please enter a non-forbidden number to mine. (Example: !mine 2527])')
        return

      await self.try_mine_number(ctx, number_to_mine)

    async def try_mine_number(self, ctx, number_to_mine):
      is_bitk_record = self.get_mined_bitk(number_to_mine)
      if is_bitk_record == True:
        await ctx.send(f'{number_to_mine} has already been mined.')
        return
      elif is_bitk_record == False:
        await ctx.send(f'{number_to_mine} is not a bit-k.')
        return

      is_bitk = self.check_is_bitk()
      self.set_mined_bitk(ctx, number_to_mine, is_bitk)

      if is_bitk:
        await ctx.send(f'**{number_to_mine} is a bit-k!**')
        bitk_value = self.get_bitk_value()
        self.set_bitk_value(bitk_value + 1)
        economy = self.bot.get_cog('Economy')
        economy.deposit_money(ctx.guild, ctx.author, bitk_value)
        await ctx.send(f"{ctx.author.name } earned {bitk_value}k for discovering the bit-k {number_to_mine}.")
        return

      await ctx.send(f'{number_to_mine} is not a bit-k.')

    def check_is_bitk(self):
      return random.randint(0, 10) == 0;

    def set_mined_bitk(self, ctx, bitk_number, is_bitk):
      database.set(f"discord/mined_bitk/{bitk_number}", is_bitk)

    def get_mined_bitk(self, bitk_number):
      return database.get(f"discord/mined_bitk/{bitk_number}")

    def set_bitk_value(self, new_value):
      database.set(f"discord/bitk_value", new_value)

    def get_bitk_value(self):
      result = database.get(f"discord/bitk_value")
      if result == None:
        self.set_bitk_value(100)
        return self.get_bitk_value()
      else:
        return int(result)

def setup(bot):
    bot.add_cog(KMines(bot))