import discord
from discord.ext import commands, tasks
import token_loader
import database
import asyncpg
import traceback
from importlib import reload

class Leaderboards(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      self.time_update.add_exception_type(asyncpg.PostgresConnectionError)
      self.time_update.start()

  def cog_unload(self):
    self.batch_update.cancel()

  @commands.Cog.listener()
  async def on_ready(self):
    for guild in self.bot.guilds:
      if guild:
          print(f"{self.bot.user} is ready with the Leaderboard cog in the following guild:\n{guild.name} (id: {guild.id})")

  # Update leaderboard every 10 minutes
  @tasks.loop(minutes=10.0)
  async def time_update(self):
    try:
      await self.update_leaderboards()
    except Exception as e:
      error_message = f"Leaderboards timed update encountered error: {e}\nTraceback: {traceback.format_exc()}"
      channel_name = "test-stuff"
      debug_channels = []
      for guild in self.bot.guilds:
        if guild:
            debug_channels = list(filter(lambda chan: channel_name in chan.name.lower(), guild.channels))
      if len(debug_channels) != 1:
        print("Leaderboards debug channel not found, outputting error here...")
        print(error_message)
      else:
        debug_channel = debug_channels[0]
        await debug_channel.send(error_message)

  @commands.command(name="debug_update_leaderboards")
  async def debug_update_leaderboards(self, ctx):
    if ctx.author.guild_permissions.administrator:
      await ctx.send("Updating leaderboards..")
      await self.update_leaderboards()
    else:
      await ctx.send("Sorry, only admins can force a leaderboard update.")


  async def update_leaderboards(self):

    board_channel = None
    for guild in self.bot.guilds:
        if guild:
            guild_id = guild.id
            channel_name = "leaderboards"
            channels = list(filter(lambda chan: channel_name in chan.name.lower(), guild.channels))

            if len(channels) == 0:
              print("Leaderboards: Could not find channel; no channel \"" + channel_name + "\"found.")
              return
            elif len(channels) > 1:
              print("Leaderboards: Could not find channel; multiple channels \"" + channel_name + "\"found.")
              return
            else:
              board_channel = channels[0]
              break
        else:
            print(f"Leaderboards can't connect to guild:{guild}")
            return
    if board_channel == None:
      print("Leaderboards bot not connected to any guild channels.")
      return

    # Build money leaderboard
    hr = "~~\u200B                                  \u200B~~\n"
    money_leaders = hr+"**The Market's Board of Honor**\n"+hr+"\n"
    all_accounts = database.get("discord/bank_accounts/" + str(guild_id))
    account_keys = list(all_accounts.keys())
    account_keys.sort(reverse=True, key=lambda account: all_accounts[account]["balance"])
    top_accounts = account_keys[:10]
    for i in range(len(top_accounts)):
      member_id = top_accounts[i]
      #print(f"ID: {member_id}")
      account = all_accounts[member_id]
      #print(f"Account: {account}")
      name = account['name']
      member = guild.get_member(int(member_id))
      if member != None:
        name = member.nick
      money_leaders += f"{i+1}. **{name}**: {account['balance']}k\n\n"
    money_leaders += "\n\n\n"

    # Build cowyboy leaderboard
    best_cowyboys = hr+"**Cowyboys Hall of Fame**\n"+hr+"\n"
    all_cowyboys = database.get("flaustria/cowyboys/roster")
    #print(all_cowyboys[0]["name"])
    all_cowyboys.sort(reverse=True, key=lambda cowyboy: cowyboy["wins"])
    top_cowyboys = all_cowyboys[:10]
    for i in range(len(top_cowyboys)):
      cowyboy = top_cowyboys[i]
      best_cowyboys += str(i+1) + ". **" + cowyboy["name"] + "**\n\tWins: " + str(cowyboy["wins"]) + "\n\tDuels: " + str(cowyboy["duels"])+"\n\n"
    best_cowyboys += "\n\n\n"

    # Edit or post leaderboards
    messages = await board_channel.history().flatten()

    try:
      await messages[0].edit(content=best_cowyboys)
    except:
      await board_channel.send(best_cowyboys)

    try:
      await messages[1].edit(content=money_leaders)
    except:
      await board_channel.send(money_leaders)

    try:
      for message in messages[2:]:
        await message.delete()
    except:
      pass


def setup(bot):
  bot.add_cog(Leaderboards(bot))
