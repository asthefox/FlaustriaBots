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
BET_OPEN_TIME = '20:00'
DUEL_CHANNEL_NAME = "cowyboy-duels"
BET_CHANNEL_NAME = "cowyboy-bets"
DISCUSSION_CHANNEL_NAME = "cowyboy-discussion"
DEBUG_CHANNEL_NAME = "test-stuff"
OPEN_DAYS = [1, 4]
DUEL_DAYS = [2, 5]#[0, 1, 2, 3, 4, 5, 6]

class Cowyboys(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      self.odds_post = ""
      self.time_update.add_exception_type(asyncpg.PostgresConnectionError)
      self.time_update.start()

  @tasks.loop(minutes=1.0)
  async def time_update(self):
    try:
      day=datetime.datetime.today().weekday()
      now=datetime.datetime.now().strftime('%H:%M')
      if day in DUEL_DAYS and now == DUEL_TIME:
        await self._run_duel()
      if day in OPEN_DAYS and now == BET_OPEN_TIME:
        await self._open_bets()
    except Exception as e:
      error_message = f"Cowyboys timed update encountered error: {e}\nTraceback: {traceback.format_exc()}"
      guild = self._find_guild()
      error_channel = self._find_channel(DEBUG_CHANNEL_NAME, guild)
      if error_channel == None:
        print("Cowyboys debug channel not found, outputting error here...")
        print(error_message)
      else:
        await error_channel.send(error_message)


  @commands.Cog.listener()
  async def on_ready(self):
      print('Cowyboy Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)

      #self._init_database()

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
      await ctx.send("Sorry, only admins can reload cowyboy libraries.")

  @commands.command(name="debug_open_bets")
  async def debug_open_bets(self, ctx):

    if ctx.author.guild_permissions.administrator:
      #self._reset_odds()
      #self._clear_bets()
      await ctx.send("Opening bets...")
      try:
        await self._open_bets()
      except Exception as e:
        await ctx.send(f"Encountered error: {e}")
      await ctx.send("Bets are now open!")
    else:
      await ctx.send("Sorry, only admins can open bets.")

  async def _open_bets(self):
    ## -- Cleary any old bets -- ##
    self._clear_bets_from_db()

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
      cowyboy_line = (f"{i+1}. {cowyboys[i]['name']} ({cowyboys[i]['color']}) - {odds[i]:g}:1\n")
      opening_post += cowyboy_line
      self.odds_post += cowyboy_line

    opening_post += f"{utilities.hr()}\nPlace your bets in this channel using the command **!bet <amount> on <cowyboy number>**"
    await bet_channel.send(opening_post)

  @commands.command(name="debug_close_bets")
  async def debug_close_bets(self, ctx):
    if ctx.author.guild_permissions.administrator:
      await ctx.send("Closing bets")
      try:
        await self._close_bets()
      except Exception as e:
        await ctx.send(f"Encountered error: {e}")
      await ctx.send("Bets are now closed.")
    else:
      await ctx.send("Sorry, only admins can close bets.")


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


  @commands.command(name="debug_run_duel_instant")
  async def debug_run_duel_instant(self, ctx):
    if ctx.author.guild_permissions.administrator:
      await ctx.send("Running duel...")
      try:
        await self._run_duel(instant=True)
      except Exception as e:
        await ctx.send(f"Encountered error: {e}\nTraceback: {traceback.format_exc()}")
      await ctx.send("The duel is complete.")
    else:
      await ctx.send("Sorry, only admins can close bets.")

  @commands.command(name="debug_run_duel")
  async def debug_run_duel(self, ctx):
    if ctx.author.guild_permissions.administrator:
      await ctx.send("Running duel...")
      try:
        await self._run_duel(instant=False)
      except Exception as e:
        await ctx.send(f"Encountered error: {e}\nTraceback: {traceback.format_exc()}")
      await ctx.send("The duel is complete.")
    else:
      await ctx.send("Sorry, only admins can close bets.")


  async def _run_duel(self, instant=False, delay=15):

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

    # Create thread
    results_thread = await create_thread(f"{datetime.date.today().strftime('%B %d')} Cowyboy Duel")

    # Post duel
    if not instant:
      for line in output:
        await results_thread.send(line)
        #await duel_channel.send(line)
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

    # Update cowyboys
    new_cowyboy = duels.update_cowyboys_after_duel(results)
    outcome_string += "\nThey will be replaced by " + drama.format_name(new_cowyboy) + "."
    await results_thread.send(outcome_string)
    #await discussion_channel.send(outcome_string)

    # Resolve bets
    await self._resolve_bets(results[0], winner_odds)

  async def _resolve_bets(self, winner, odds):
    # Here we will respond to each of the individual bet tickets
    winner_name = winner['name']
    winner_id = winner['id']
    #await ctx.send(f"winner_name:{winner_name} winner_id:{winner_id} odds:{odds}")
    winner_bets = self._get_matching_bets(winner_id)

    if winner_bets != None:
      for wb in winner_bets:
        bet_user_id = wb['user_id']
        #print(f"User with ID {bet_user_id} won.")
        bet_user_id = int(bet_user_id)
        bet_amount = wb['bet_amount']
        winnings = int(float(bet_amount) * float(odds))
        await self._deposit_winnings(winnings, bet_user_id, winner_name)

    await self._send_pity_refunds()

    self._clear_bets_from_db()

  async def _deposit_winnings(self, winnings, bet_user_id, winner_name):
    guild = self._find_guild()
    #print(f"   Guild: {guild}, with {len(guild.members)} members")
    #for member in guild.members:
    #  print(f"      Member ID: {member.id}")
    member = find(lambda m: m.id == bet_user_id, guild.members)
    #print(f"   Member ID: {bet_user_id}.")
    #print(f"   Member: {member}")
    economy = self.bot.get_cog('Economy')
    economy.deposit_money(guild, member, winnings)
    try:
      dm = await member.create_dm()
      await dm.send(f"Congratulations! You have won {winnings}k by betting on {winner_name}.")
    except:
      pass
    #print("   DM sent.")

  def _get_matching_bets(self, cowyboy_id):
    all_bets = database.get(f"discord/cowyboy_bets")
    if all_bets == None:
      return None
    return [bet for bet in all_bets.values() if bet['cowyboy_id'] == cowyboy_id]

  async def _send_pity_refunds(self):
    pity_value = 50
    economy = self.bot.get_cog('Economy')
    guild = self._find_guild()
    all_bets = database.get(f"discord/cowyboy_bets")

    if all_bets == None:
      return

    all_bettors = list(set([bet['user_id'] for bet in all_bets.values()]))
    for bettor_id in all_bettors:
      bettor_id = int(bettor_id)
      member = find(lambda m: m.id == bettor_id, self._find_guild().members)
      if economy.get_balance(guild, member) <= 0:
        economy.deposit_money(self._find_guild(), member, pity_value)
        try:
          dm = await member.create_dm()
          await dm.send(f"The Market has taken pity on you after you piously bet all your money.  You have been wired {pity_value}k.")
        except:
          pass

  def _clear_bets_from_db(self):
    database.set(f"discord/cowyboy_bets", None)

  @commands.command(name="odds")
  async def reprint_odds(self, ctx):
    bet_channel = self._find_channel(BET_CHANNEL_NAME, ctx.guild)
    if bet_channel == None:
      return

    if ctx.channel != bet_channel:
      return

    if not hasattr(self, "odds_post") or self.odds_post == None:
      return

    await bet_channel.send(self.odds_post)

  @commands.command(name="bet")
  async def bet(self, ctx, bet_amount, on_word, cowyboy_number=None):
    #!bet <cowyboy (by name or color or number)> <money>

    bet_channel = self._find_channel(BET_CHANNEL_NAME, ctx.guild)
    if bet_channel == None:
      return

    if ctx.channel != bet_channel:
      return

    if not cowyboy_number or not bet_amount:
      await bet_channel.send('Please enter the number of the cowyboy you want to bet on, then the amount of k you want to bet (example - !bet 230 on 3)')
      return

    bet_amount = bet_amount.strip("k")

    if not utilities.is_only_numbers(bet_amount):
      await bet_channel.send(f"{bet_amount} is not a valid bet amount")
      return

    if not utilities.is_only_numbers(cowyboy_number):
      await bet_channel.send(f"{cowyboy_number} not a positive number")
      return

    cowyboy_index = int(cowyboy_number) - 1
    try:
      if not cowyboy_index in range(len(self.cowyboys)):
        await bet_channel.send(f"{cowyboy_number} not a number of one of the cowyboys you can bet on")
        return
    except:
      await bet_channel.send(f"Hold it up, pardoner!  Those there cowyboys have to be reinitialized due to a sytem reset, just like in the olden days.  I'll try to fix 'er up automatically, so you can try your bet again.")
      self.cowyboys = duels.get_active_cowyboys()
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
      "user_id" : str(user_id),
      "cowyboy_id" : cowyboy_id,
      "bet_amount" : bet_amount
    }
    database.push(f"discord/cowyboy_bets", bet_info)

def setup(bot):
    bot.add_cog(Cowyboys(bot))