from firebase import Firebase
import discord
from discord.ext import commands
import token_loader
import database
import utilities
import traceback
import cowyboy_duels as duels
import cowyboy_drama as drama
import datetime
import asyncio

DUEL_CHANNEL_NAME = "test_duels"
BET_CHANNEL_NAME = "test_bets"
DISCUSSION_CHANNEL_NAME = "test_cowyboy_discussion"

#TODO: Replace guild.default_role with the Flaustrian Citizen role

class Cowyboys(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      self.odds_post = ""

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

  @commands.command(name="debug_open_bets")
  async def debug_open_bets(self, ctx):

      #self._reset_odds()
      #self._clear_bets()
      await ctx.send("Opening bets...")
      try:
        await self._open_bets(ctx)
      except Exception as e:
        await ctx.send(f"Encountered error: {e}")
      await ctx.send("Bets are now open!")

  async def _open_bets(self, ctx):

      ## -- Open Channel -- ##

      bet_channel = await self._find_channel(BET_CHANNEL_NAME, ctx)
      if bet_channel == None:
        return

      await bet_channel.set_permissions(ctx.guild.default_role, send_messages=True)

      ## -- Print Odds -- ##
      cowyboys = duels.get_active_cowyboys()
      odds = duels.determine_payoffs(cowyboys)

      opening_post = f"{utilities.hr()}**COWYBOY BETS NOW OPEN FOR {datetime.date.today().strftime('%B %d').upper()}**!\n"
      self.odds_post = ""
      for i in range(len(cowyboys)):
        cowyboy_line = (f"{i+1}.{cowyboys[i]['name']} ({cowyboys[i]['color']}) - {odds[i]:g}:1\n")
        opening_post += cowyboy_line
        self.odds_post += cowyboy_line

      opening_post += f"{utilities.hr()}\nPlace your bets in this channel using the command **!bet <cowyboy name or color> <amount>**"

      await bet_channel.send(opening_post)


  @commands.command(name="debug_close_bets")
  async def debug_close_bets(self, ctx):
      await ctx.send("Closing bets")
      try:
        await self._close_bets(ctx)
      except Exception as e:
        await ctx.send(f"Encountered error: {e}")
      await ctx.send("Bets are now closed.")

  async def _close_bets(self, ctx):
      bet_channel = await self._find_channel(BET_CHANNEL_NAME, ctx)
      if bet_channel == None:
        return

      await bet_channel.set_permissions(ctx.guild.default_role, send_messages=False)

      await bet_channel.send(f"Bets are now closed for {datetime.date.today().strftime('%B %d')}. Please gather around #{DUEL_CHANNEL_NAME}, for the opening convocation will begin shortly.")


  @commands.command(name="debug_run_duel")
  async def debug_run_duel(self, ctx):
    await ctx.send("Running duel...")
    try:
      await self._run_duel(ctx)
    except Exception as e:
      await ctx.send(f"Encountered error: {e}\nTraceback: {traceback.format_exc()}")
    await ctx.send("Bets are now closed.")

  async def _run_duel(self, ctx, instant=False):

    # Close bets
    await self._close_bets(ctx)
    if not instant:
      await asyncio.sleep(10)

    # Determine duel outcome
    duel_channel = await self._find_channel(DUEL_CHANNEL_NAME, ctx)
    cowyboys = duels.get_active_cowyboys()
    odds = duels.determine_payoffs(cowyboys)
    results = duels.determine_placement(cowyboys)
    output = drama.get_contest_output(results)

    # Post duel
    if not instant:
      for line in output:
        await duel_channel.send(line)
        await asyncio.sleep(1)

    # Post outcome
    discussion_channel = await self._find_channel(DISCUSSION_CHANNEL_NAME, ctx)
    outcome_string = (f"COWYBOY DUEL RESULTS FOR {datetime.date.today().strftime('%B %d')}:\n")
    for i in range(len(cowyboys)):
      outcome_string += (f"{i+1}. {drama.format_name(results[i])}\n")
    winner_odds_index = cowyboys.index(results[0])
    winner_odds = odds[winner_odds_index]
    outcome_string += (f"\n{drama.format_name(results[0])} pays {winner_odds} to 1.\n")
    outcome_string += f"{drama.format_name(results[-1])} has been eliminated, and will retire from competition."

    await discussion_channel.send(outcome_string)

    # Update cowyboys
    duels.update_cowyboys_after_duel(results)

    # Resolve bets
    self._resolve_bets(ctx, results[0], winner_odds)

  async def _resolve_bets(self, ctx, winner, odds):

    # Here we will respond to each of the individual bet tickets
    pass


  @commands.command(name="bet")
  async def bet(self, ctx, cowyboy=None, bet_amount=None):
    #!bet <cowyboy (by name or color or number)> <money>

    bet_channel = await self._find_channel(BET_CHANNEL_NAME, ctx)
    if bet_channel == None:
      return

    if not cowyboy or not bet_amount:
      await bet_channel.send('please enter the name of the cowyboy you want to bet on, then the amount of k you want to bet (example - !bet horselegs 230)')
      return

    if not utilities.is_only_numbers(bet_amount):
      await bet_channel.send(f"{bet_amount} is not a valid bet amount")
      return

    economy = self.bot.get_cog('Economy')
    (has_money, balance) = economy.withdraw_money(ctx.guild, ctx.author, int(bet_amount))

    if not has_money:
      await bet_channel.send(f"Sorry, you dot not have {bet_amount}k in your bank account. Your current balance is {balance}k.")
      return

    self.add_bet_to_db(ctx.author.id, cowyboy, bet_amount)
    await bet_channel.send(f"Placing bet of {bet_amount}k on {cowyboy}")

  def add_bet_to_db(self, user_id, cowyboy, bet_amount):
    bet_info = {
      "user_id" : user_id,
      "cowyboy" : cowyboy,
      "bet_amount" : bet_amount
    }
    database.push(f"discord/cowyboy_bets", bet_info)

def setup(bot):
    bot.add_cog(Cowyboys(bot))