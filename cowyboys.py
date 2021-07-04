from firebase import Firebase
import discord
from discord.ext import tasks, commands
import token_loader
import database
import utilities
import traceback
import cowyboy_duels as duels
import cowyboy_drama as drama
import datetime
import asyncio, asyncpg
from discord.utils import find
from importlib import reload

DUEL_TIME='19:00'
BET_OPEN_TIME = '18:00'
DUEL_CHANNEL_NAME = "test_duels"
BET_CHANNEL_NAME = "test_bets"
DISCUSSION_CHANNEL_NAME = "test_cowyboy_discussion"

#TODO: Replace guild.default_role with the Flaustrian Citizen role

class Cowyboys(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      self.odds_post = ""
      self.time_update.add_exception_type(asyncpg.PostgresConnectionError)
      self.time_update.start()

  @tasks.loop(minutes=1.0)
  async def time_update(self):
    now=datetime.datetime.now().strftime('%H:%M')
    #if now == self.refresh_time:
    #  await self.refresh_headlines()
    if now == DUEL_TIME:
      await self._run_duel()
    if now == BET_OPEN_TIME:
      await self._open_bets()

  @commands.Cog.listener()
  async def on_ready(self):
      print('Cowyboy Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)

      self._init_database()

  def _find_guild(self):
    guild = discord.utils.get(self.bot.guilds, name=token_loader.FLAUSTRIA_GUILD)
    if guild == None:
      guild = discord.utils.get(self.bot.guilds, name=token_loader.DMERSHON_TEST_GUILD)
    if guild == None:
      raise Exception("Could not connect to guilds with ID: " + token_loader.FLAUSTRIA_GUILD + " or " + token_loader.DMERSHON_TEST_GUILD)

    return guild

  def _find_channel(self, name, guild):
    channels = list(filter(lambda chan: name in chan.name.lower(), guild.channels))

    if len(channels) == 0:
      #await ctx.send("Could not open bets; no channel \"" + name + "\"found.")
      return None
    #if len(channels) > 1:
      #await ctx.send("Could not open bets; multiple channels \"" + name + "\"found.")
      #return None

    return channels[0]

  @commands.command(name="debug_reload_cowyboy_libraries")
  async def debug_reload_library(self, ctx):
    if ctx.author.guild_permissions.administrator:
      global database
      global duels
      global drama
      global token_loader

      database = reload(database)
      drama = reload(drama)
      duels = reload(duels)
      token_loader = reload(token_loader)
      await ctx.send("Cowyboy libraries reloaded: database, cowyboy_drama, cowyboy_duels, token_loader.")

    else:
      await ctx.send("Sorry, only admins can change the news.")

  @commands.command(name="debug_open_bets")
  async def debug_open_bets(self, ctx):

    #self._reset_odds()
    #self._clear_bets()
    await ctx.send("Opening bets...")
    try:
      await self._open_bets()
    except Exception as e:
      await ctx.send(f"Encountered error: {e}")
    await ctx.send("Bets are now open!")

  async def _open_bets(self):

    ## -- Open Channel -- ##
    guild = self._find_guild()
    bet_channel = self._find_channel(BET_CHANNEL_NAME, guild)
    if bet_channel == None:
      return

    # Uses Flaustrian Citizen role if available
    role = guild.get_role(845096006261407765)
    if role == None:
      role = guild.default_role
    await bet_channel.set_permissions(role, send_messages=True)

    ## -- Print Odds -- ##
    self.cowyboys = duels.get_active_cowyboys()
    await self.print_odds(self.cowyboys, bet_channel)

  async def print_odds(self, cowyboys, bet_channel):
    odds = duels.determine_payoffs(cowyboys)
    opening_post = f"{utilities.hr()}**COWYBOY BETS NOW OPEN FOR {datetime.date.today().strftime('%B %d').upper()}**!\n"
    self.odds_post = ""
    for i in range(len(cowyboys)):
      cowyboy_line = (f"{i+1}.{cowyboys[i]['name']} ({cowyboys[i]['color']}) - {odds[i]:g}:1\n")
      opening_post += cowyboy_line
      self.odds_post += cowyboy_line

    opening_post += f"{utilities.hr()}\nPlace your bets in this channel using the command **!bet <cowyboy number> <amount>**"
    await bet_channel.send(opening_post)
  
  @commands.command(name="debug_close_bets")
  async def debug_close_bets(self, ctx):
    await ctx.send("Closing bets")
    try:
      await self._close_bets()
    except Exception as e:
      await ctx.send(f"Encountered error: {e}")
    await ctx.send("Bets are now closed.")

  async def _close_bets(self):
    guild = self._find_guild()
    bet_channel = self._find_channel(BET_CHANNEL_NAME, guild)
    if bet_channel == None:
      return

    # Uses Flaustrian Citizen role if available
    role = guild.get_role(845096006261407765)
    if role == None:
      role = guild.default_role
    await bet_channel.set_permissions(role, send_messages=False)

    await bet_channel.send(f"Bets are now closed for {datetime.date.today().strftime('%B %d')}. Please gather around #{DUEL_CHANNEL_NAME}, for the opening convocation will begin shortly.")


  @commands.command(name="debug_run_duel")
  async def debug_run_duel(self, ctx):
    await ctx.send("Running duel...")
    try:
      await self._run_duel(ctx, instant=True)
    except Exception as e:
      await ctx.send(f"Encountered error: {e}\nTraceback: {traceback.format_exc()}")
    await ctx.send("Bets are now closed.")

  async def _run_duel(self, ctx, instant=False, delay=10):

    # Close bets
    await self._close_bets()

    if not instant:
      await asyncio.sleep(delay)

    # Determine duel outcome
    guild = self._find_guild()
    duel_channel = self._find_channel(DUEL_CHANNEL_NAME, guild)
    cowyboys = duels.get_active_cowyboys()
    odds = duels.determine_payoffs(cowyboys)
    results = duels.determine_placement(cowyboys)
    output = drama.get_contest_output(results)

    # Post duel
    if not instant:
      for line in output:
        await duel_channel.send(line)
        await asyncio.sleep(delay)

    # Post outcome
    discussion_channel = self._find_channel(DISCUSSION_CHANNEL_NAME, guild)
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
    await self._resolve_bets(ctx, results[0], winner_odds)

  async def _resolve_bets(self, ctx, winner, odds):
    # Here we will respond to each of the individual bet tickets
    winner_name = winner['name']
    winner_id = winner['id']
    await ctx.send(f"winner_name:{winner_name} winner_id:{winner_id} odds:{odds}")
    winner_bets = self._get_matching_bets(winner_id)
    for wb in winner_bets:
      bet_user_id = wb['user_id']
      bet_amount = wb['bet_amount']
      winnings = int(float(bet_amount) * float(odds))
      self._deposit_winnings(winnings, bet_user_id)
      await ctx.send(f"paid out bet to user:{bet_user_id} bet_amount:{bet_amount} winnings:{winnings}")

  def _deposit_winnings(self, winnings, user_id):
    member = find(lambda m: m.id == user_id, self._find_guild().members)
    economy = self.bot.get_cog('Economy')
    economy.deposit_money(self._find_guild(), member, winnings)

  def _get_matching_bets(self, cowyboy_id):
    all_bets = database.get(f"discord/cowyboy_bets")
    return [bet for bet in all_bets.values() if bet['cowyboy_id'] == cowyboy_id]

  @commands.command(name="bet")
  async def bet(self, ctx, cowyboy_number=None, bet_amount=None):
    #!bet <cowyboy (by name or color or number)> <money>

    bet_channel = self._find_channel(BET_CHANNEL_NAME, ctx.guild)
    if bet_channel == None:
      return

    if not cowyboy_number or not bet_amount:
      await bet_channel.send('please enter the name of the cowyboy you want to bet on, then the amount of k you want to bet (example - !bet horselegs 230)')
      return

    if not utilities.is_only_numbers(bet_amount):
      await bet_channel.send(f"{bet_amount} is not a valid bet amount")
      return
    
    if not utilities.is_only_numbers(cowyboy_number):
      await bet_channel.send(f"{cowyboy_number} not a positive number")
      return

    cowyboy_index = int(cowyboy_number) - 1
    if not cowyboy_index in range(len(self.cowyboys)):
      await bet_channel.send(f"{cowyboy_number} not a number of one of the cowyboys you can bet on")
      return

    economy = self.bot.get_cog('Economy')
    (has_money, balance) = economy.withdraw_money(ctx.guild, ctx.author, int(bet_amount))

    if not has_money:
      await bet_channel.send(f"Sorry, you dot not have {bet_amount}k in your bank account. Your current balance is {balance}k.")
      return

    cowyboy = self.cowyboys[cowyboy_index]
    cb_name = cowyboy['name']
    self._add_bet_to_db(ctx.author.id, cowyboy['id'], bet_amount)
    await bet_channel.send(f"Placing bet of {bet_amount}k on {cb_name}")

  def _add_bet_to_db(self, user_id, cowyboy_id, bet_amount):
    bet_info = {
      "user_id" : user_id,
      "cowyboy_id" : cowyboy_id,
      "bet_amount" : bet_amount
    }
    database.push(f"discord/cowyboy_bets", bet_info)

def setup(bot):
    bot.add_cog(Cowyboys(bot))