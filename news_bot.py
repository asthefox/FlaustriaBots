import discord
from discord.ext import tasks, commands
import asyncpg
from datetime import datetime, time
from importlib import reload

import token_loader
import flaustrian_headlines
import database

import tweepy

class DailyNewsCog(commands.Cog):

  #### ---- PSEUDOCONSTANTS ---- ####

  #refresh_time='08:05' #time is in 24hr format
  news_post_time='17:00'
  entertainment_post_time='20:30'
  test_post_time = '23:15'

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

  def _date_db_format(self, day):
    return day.strftime("%Y-%m-%d")

  def _get_article_path(self, category, lookup_date):
    return "flaustria/news/" + category + "/" + lookup_date

  def _get_todays_article_path(self, category):
    todays_date = self._date_db_format(datetime.today())
    return self._get_article_path(category, todays_date)

  def _isTimeFormat(self, input):
    try:
        datetime.strptime(input, '%H:%M')
        return True
    except ValueError:
        return False

  def _connect_channels(self):
    if not hasattr(self, "guild") or not self.guild:
      self.guild = discord.utils.get(self.bot.guilds, name=self.guild_token)

    if not self.guild:
      raise Exception("Could not connect to guild with ID: " + self.guild_token)

    if not hasattr(self, "entertainment_channel") or not self.entertainment_channel:
      self.entertainment_channel = self._find_channel("flaustrian_entertainment")

    if not self.entertainment_channel:
      raise Exception("Could not find a channel with name flaustrian_entertainment")

    if not hasattr(self, "news_channel") or not self.news_channel:
      self.news_channel = self._find_channel("flaustrian_news")

    if not self.news_channel:
      raise Exception("Could not find a channel with name flaustrian_news")
      
    """"
    try:
      if not self.guild:
        raise AttributeError
    except AttributeError:
      self.guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
      if not self.guild:
        raise AttributeError
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
    """

  #### ---- SETUP METHODS ---- ####

  def __init__(self, bot):
      self.bot = bot
      self.guild_token = token_loader.FLAUSTRIA_GUILD
      self.data = []
      self.time_update.add_exception_type(asyncpg.PostgresConnectionError)
      self.time_update.start()
      #try:
      #self._connect_channels()
      #print("News bot loaded as extension and connected to guild.")
      #except AttributeError:
      #  print("News bot waiting for setup to connect to guild.")

  @commands.Cog.listener()
  async def on_ready(self):
      self._connect_channels()
      if self.guild:
          print(f"{self.bot.user} is connected to the following guild:\n{self.guild.name} (id: {self.guild.id})")
      else:
          print(f"Can't connect to guild:{self.guild_token}")


  #### ---- TWITTER AND SUCH ---- ####

  def twitter_crosspost(self, headline):

    try:
      auth = tweepy.OAuthHandler(
              token_loader.TWITTER_CONSUMER_KEY,
              token_loader.TWITTER_CONSUMER_SECRET
              )
      auth.set_access_token(
              token_loader.TWITTER_ACCESS_TOKEN,
              token_loader.TWITTER_ACCESS_TOKEN_SECRET
              )
      api = tweepy.API(auth)

      status = api.update_status(status=headline)

    except tweepy.TweepError:
      print('Error! Failed to access API and post.')


  #### ---- SETTING / GETTING HEADLINES FROM DATABASE ---- ####

  def _retrieve_daily_headline_info(self, category):
    data_path = self._get_todays_article_path(category)
    headline_query = database.get(data_path+"/headline")
    headline_type = database.get(data_path+"/category")
    if headline_query == None:
      return ("There is no news today.", None)
    return (headline_query, headline_type)

  def _format_headline_for_discord(self, headline, full_category):
    hr = "~~\u200B                                  \u200B~~\n"
    cat_words = {
      "music_review" : "MUSIC REVIEW",
      "movie_review" : "MOVIE REVIEW",
      "recent_tv_headline" : "TV NEWS",
      "movie_chart" : "MOVIE NEWS",
      "music_chart" : "MUSIC NEWS",
      "upcoming_tv_headline" : "TV PREVIEW",
      "movie_synopsis" : "MOVIE RECAP",

      "business_news" : "BREAKING BUSINESS UPDATE",
      "sports_news" : "BREAKING SPORTS NEWS",
      "gossip_news" : "THIS WEEK'S HOTTEST GOSSIP",
      "crime_news" : "BREAKING CRIME BULLETIN",
      "politics_news" : "BREAKING POLITICAL NEWS",
      "fad_news" : "THIS WEEK'S CULTURE REPORT",
      "listicle_news" : "THIS WEEK'S FUN FACTS"
  	}
    header = "\n" + hr + "**" + cat_words[full_category] + ":**\n" + headline + "\n" + hr + "\n"
    return header

  def _format_headline_for_twitter(self, headline, full_category):
    addendum = " Read and discuss the full article in our Discord: https://discord.gg/zbDusCRmHw"
    limit = 280 - len(addendum)
    headline_cropped = headline
    if len(headline_cropped) > limit:
      headline_cropped = headline_cropped[:limit-2] + ".."
    
    return headline_cropped + addendum

  def _retrieve_daily_article_post(self, category):
    data_path = self._get_todays_article_path(category)
    article_query = database.get(data_path+"/article")
    byline_query = database.get(data_path+"/byline")

    if article_query == None or byline_query == None:
      return "While it is unusual for there not to be any news, the All-Seeing Eye encourages our readers not to be alarmed."

    return "_" + byline_query + "_" + "\n\n>>> " + article_query


  #def _generate_daily_headline(self, category):
  #  headline = flaustrian_headlines.get_headline(category, datetime.today())
  #  headline_path = self._get_todays_headline_path(self.guild.id, category)
  #  database.set(headline_path, headline)


  #### ---- DEBUG COMMANDS ---- ####

  """"
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
"""

  @commands.command(name="news_current_time")
  async def debug_print_time(self, ctx):
    if ctx.author.guild_permissions.administrator:
      now=datetime.strftime(datetime.now(),'%H:%M')
      await ctx.send("The time is: " + now)
    else:
      await ctx.send("Sorry, only admins can tell the internal news timer.")
    
  @commands.command(name="news_debug_reload_libraries")
  async def debug_reload_library(self, ctx):
    if ctx.author.guild_permissions.administrator:
      global database
      global flaustrian_headlines
      global token_loader

      database = reload(database)
      flaustrian_headlines = reload(flaustrian_headlines)
      token_loader = reload(token_loader)
      await ctx.send("Newsbot libraries reloaded: database, flaustrian_headlines, token_loader.")

    else:
      await ctx.send("Sorry, only admins can change the news.")


  #@commands.command(name="news_debug_refresh_headlines")
  #async def debug_refresh_headlines(self, ctx):
  #  if ctx.author.guild_permissions.administrator:
  #    await self.refresh_headlines()
  #    await ctx.send("Headlines refreshed.")
  #  else:
  #    await ctx.send("Sorry, only admins can change the news.")

  @commands.command(name="news_debug_post_articles")
  async def debug_post_headlines(self, ctx):
    if ctx.author.guild_permissions.administrator:
      #headline = self._retrieve_daily_headline("news")
      await self.post_headline("news")
      #await self.post_article("news")
      await self.post_headline("entertainment")
      #await self.post_article("entertainment")
    else:
      await ctx.send("Sorry, only admins can advance the news.")


  @commands.command(name="news_debug_print_articles")
  async def debug_print_headlines(self, ctx):
    if ctx.author.guild_permissions.administrator:
      headline, category = self._retrieve_daily_headline_info("news")
      article = self._retrieve_daily_article_post("news")
      await ctx.send("NEWS: " + headline)
      await ctx.send(article)
      headline, category = self._retrieve_daily_headline_info("entertainment")
      article = self._retrieve_daily_article_post("entertainment")
      await ctx.send("ENTERTAINMENT: " + headline)
      await ctx.send(article)
    else:
      await ctx.send("Sorry, only admins can foresee the news.")

  @commands.command(name="news_debug_change_time")
  async def debug_change_news_time(self, ctx, event_arg, value_arg):
    if ctx.author.guild_permissions.administrator:
      if not self._isTimeFormat(value_arg):
        await ctx.send("Sorry, could not convert " + value_arg + " to a valid time.")
      #elif event_arg == "refresh":
      #  self.refresh_time = value_arg
      #  await ctx.send("The daily headlines will now refresh every day at " #+ value_arg + ".")
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
    #if now == self.refresh_time:
    #  await self.refresh_headlines()
    if now == self.news_post_time:
      await self.post_headline("news")
    if now == self.entertainment_post_time:
      await self.post_headline("entertainment")
    #if now == self.test_post_time:
    #  await self.test_post()

  #async def refresh_headlines(self):
    #database.refresh_token()
    #self._generate_daily_headline("news")
    #self._generate_daily_headline("entertainment")

  async def post_headline(self, category):
    headline, full_category = self._retrieve_daily_headline_info(category)
    article = self._retrieve_daily_article_post(category)
    if category == "news":
      channel = self.news_channel
    elif category == "entertainment":
      channel = self.entertainment_channel
    headline_post = self._format_headline_for_discord(headline, full_category)
    tweet = self._format_headline_for_twitter(headline, full_category)
    await channel.send(headline_post)
    await channel.send(article)
    self.twitter_crosspost(tweet)

  async def test_post(self):
    message_channel=self.news_channel
    await message_channel.send("This is a test of the Flaustrian Broadcasting System.")


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