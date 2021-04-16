import discord
from discord.ext import tasks, commands
import asyncpg
from datetime import datetime, time

import token_loader
import flaustrian_headlines
import database

class DailyNewsCog(commands.Cog):

  #### ---- PSEUDOCONSTANTS ---- ####

  refresh_time='0:00' #time is in 24hr format
  news_post_time='10:00'
  entertainment_post_time='13:30'
  test_post_time = '15:05'

  #### ---- HELP METHODS ---- ####

  def _find_channel(self, name):
    channels = list(filter(lambda chan: name in chan.name.lower(), self.guild.channels))

    if len(channels) == 0:
      print("NewsBot: Could not find channel; no channel \"" + name + "\"found.")
      return None
    if len(channels) > 1:
      print("NewsBot: Could not find channel; multiple channels \"" + name + "\"found.")
      return None

    return channels[0]

  def _get_headline_path(self, guild_id, category, lookup_date):
    return "discord/news/" + str(guild_id) + "/" + category + "/" + lookup_date

  def _get_todays_headline_path(self, guild_id, category):
    todays_date = datetime.now().strftime("%Y/%m/%d")
    return self._get_headline_path(guild_id, category, todays_date)

  def _isTimeFormat(self, input):
    try:
        time.strptime(input, '%H:%M')
        return True
    except ValueError:
        return False

  def _connect_channels(self):
    try:
      if not self.guild: 
        raise AttributeError
    except AttributeError:
      self.guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
    try:
      if not self.entertainment_channel: 
        raise AttributeError
    except AttributeError:
      self.entertainment_channel = self._find_channel("flaustrian_entertainment")
    try: 
      if not self.news_channel:
        raise AttributeError
    except AttributeError:
      self.news_channel = self._find_channel("flaustrian_news")

  #### ---- SETUP METHODS ---- ####

  def __init__(self, bot):
      self.bot = bot
      self.guild_token = token_loader.GUILD
      self.data = []
      self.time_update.add_exception_type(asyncpg.PostgresConnectionError)
      self.time_update.start()
      self._connect_channels()

  @commands.Cog.listener()
  async def on_ready(self):
      self._connect_channels()
      if self.guild:
          print(f"{self.bot.user} is connected to the following guild:\n{self.guild.name} (id: {self.guild.id})")
      else:
          print(f"Can't connect to guild:{self.guild_token}")
      


  #### ---- SETTING / GETTING HEADLINES FROM DATABASE ---- ####

  def _retrieve_daily_headline(self, category):
    headline_path = self._get_todays_headline_path(self.guild.id, category)
    headline_query = database.get(headline_path)

    if headline_query == None:
      self._generate_daily_headline(category)
      headline_query = database.get(headline_path)

    return headline_query

  def _generate_daily_headline(self, category):
    headline = flaustrian_headlines.get_headline(category, datetime.today())
    headline_path = self._get_todays_headline_path(self.guild.id, category)
    database.set(headline_path, headline)
    

  #### ---- DEBUG COMMANDS ---- ####
  
  @commands.command(name="news_hi")
  async def news_hi(self, ctx):
    await ctx.send("hi from the news")

  @commands.command(name="news_debug_connection")
  async def debug_connection(self, ctx):
    if self.guild:
      await ctx.send("Guild: " + str(self.guild.id))
      await ctx.send(self.news_channel)
      await ctx.send(self.entertainment_channel)
    else:
      await ctx.send("No guild.")

  @commands.command(name="news_debug_reauth")
  async def debug_reauthenticate_db(self, ctx):
    database.refresh_token()
    await ctx.send("Database token refreshed.")

  @commands.command(name="refresh_headlines")
  async def debug_refresh_headlines(self, ctx):
    if ctx.author.guild_permissions.administrator:
      await self.refresh_headlines()
      await ctx.send("Headlines refreshed.")
    else:
      await ctx.send("Sorry, only admins can change the news.")

  @commands.command(name="post_headlines")
  async def debug_post_headlines(self, ctx):
    if ctx.author.guild_permissions.administrator:
      #headline = self._retrieve_daily_headline("news")
      await self.post_headline("news")
      await self.post_headline("entertainment")
    else:
      await ctx.send("Sorry, only admins can advance the news.")

  @commands.command(name="print_headlines")
  async def debug_print_headlines(self, ctx):
    if ctx.author.guild_permissions.administrator:
      headline = self._retrieve_daily_headline("news")
      await ctx.send("NEWS: " + headline)
      headline = self._retrieve_daily_headline("entertainment")
      await ctx.send("ENTERTAINMENT: " + headline)
    else:
      await ctx.send("Sorry, only admins can foresee the news.")

  @commands.command(name="change_news_time")
  async def debug_change_news_time(self, ctx, event_arg, value_arg):
    if ctx.author.guild_permissions.administrator:
      if not self._isTimeFormat(value_arg):
        await ctx.send("Sorry, could not convert " + value_arg + " to a valid time.")
      elif event_arg == "refresh":
        self.refresh_time = value_arg
        await ctx.send("The daily headlines will now refresh every day at " + value_arg + ".")
      elif event_arg == "news":
        self.news_post_time = value_arg
        await ctx.send("The news headline will now post every day at " + value_arg + ".")
      elif event_arg == "entertainment":
        self.entertainment_post_time = value_arg
        await ctx.send("The entertainment headline will now post every day at " + value_arg + ".")
      elif event_arg == "test":
        self.test_post_time = value_arg
        await ctx.send("The test will now post every day at " + value_arg + ".")
      else:
        await ctx.send("Sorry, could not recognize news event " + event_arg + ". Must be news, entertainment, or refresh.")
    else:
      await ctx.send("Sorry, only admins can foresee the news.")


  #### ---- TIMED TASKS ---- ####

  @tasks.loop(minutes=1.0)
  async def time_update(self):
    now=datetime.strftime(datetime.now(),'%H:%M')
    if now == self.refresh_time:
      await self.refresh_headlines()
    if now == self.news_post_time:
      await self.post_headline("news")
    if now == self.entertainment_post_time:
      await self.post_headline("entertainment")
    if now == self.test_post_time:
      await self.test_post()

  async def refresh_headlines(self):
    self._generate_daily_headline("news")
    self._generate_daily_headline("entertainment")    

  async def post_headline(self, category):
    headline = self._retrieve_daily_headline(category)
    if category == "news":
      channel = self.news_channel
    elif category == "entertainment":
      channel = self.entertainment_channel
    await self.bot.send_message(channel, headline)
    
  async def test_post(self):
    message_channel=self.bot.get_channel(self.message_channel_id)
    await self.bot.send_message(message_channel,"This is a test of the Flaustrian Broadcasting System.")


  #### ---- TAKEDOWN METHODS ---- ####

  def cog_unload(self):
    self.batch_update.cancel()

def setup(bot):
    bot.add_cog(DailyNewsCog(bot))

""""
bot=commands.Bot(command_prefix='!')


file_name='some_file.txt' #replace with the name of your file with extension

if os.path.isfile(file_name):
		with open(file_name, "r") as f:
			message_list = f.read()
			message_list = message_list.strip().split("\n")

@bot.event
async def on_ready():
	print(bot.user.name)
	print(bot.user.id)

async def time_check():
	await bot.wait_until_ready()
	message_channel=bot.get_channel(message_channel_id)
	while not bot.is_closed:
		now=datetime.strftime(datetime.now(),'%H:%M')
		if now == send_time:
			message= random.choice(message_list)
			await bot.send_message(message_channel,message)
			time=90
		else:
			time=1
		await asyncio.sleep(time)

bot.loop.create_task(time_check())

bot.run('TOKEN')
"""