from firebase import Firebase
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import token_loader
from utilities import is_only_numbers

DUEL_CHANNEL_NAME = "test_duels"
BET_CHANNEL_NAME = "test_bets"

#TODO: Replace guild.default_role with the Flaustrian Citizen role

class Cowyboys(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
      print('Cowyboy Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)

      self._init_database()

  async def _find_channel(self, name, ctx):
    channels = list(filter(lambda chan: name in chan.name.lower(), ctx.guild.channels))

    if len(channels) == 0:
      await ctx.send("Could not open bets; no channel \"" + name + "\"found.")
      return None
    if len(channels) > 1:
      await ctx.send("Could not open bets; multiple channels \"" + name + "\"found.")
      return None

    return channels[0]

  @commands.command(name="open_bets")
  async def open_bets(self, ctx):

      #self._reset_odds()
      #self._clear_bets()

      bet_channel = await self._find_channel(BET_CHANNEL_NAME, ctx)
      if bet_channel == None:
        return

      await bet_channel.set_permissions(ctx.guild.default_role, send_messages=True)

      await ctx.send("Bets are now open!")
      await bet_channel.send("Bets are now open!")
      await bet_channel.send("Here are the odds.")

  @commands.command(name="close_bets")
  async def close_bets(self, ctx):
      bet_channel = await self._find_channel(BET_CHANNEL_NAME, ctx)
      if bet_channel == None:
        return

      await bet_channel.set_permissions(ctx.guild.default_role, send_messages=False)

      await ctx.send("Bets are now closed.")
      await bet_channel.send("Bets are now closed.")

  @commands.command(name="bet")
  async def bet(self, ctx, cowyboy=None, bet_amount=None):
    #!bet <cowyboy (by name or color or number)> <money>

    bet_channel = await self._find_channel(BET_CHANNEL_NAME, ctx)
    if bet_channel == None:
      return

    if not cowyboy or not bet_amount:
      await bet_channel.send('please enter the name of the cowyboy you want to bet on, then the amount of k you want to bet (example - !bet horselegs 230)')
      return
    
    if not is_only_numbers(bet_amount):
      await bet_channel.send(f"{bet_amount} is not a valid bet amount")
      return

    await bet_channel.send(f"Placing bet of {bet_amount}k on {cowyboy}")


def setup(bot):
    bot.add_cog(Cowyboys(bot))