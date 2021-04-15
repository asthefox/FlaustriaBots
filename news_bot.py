import discord
from discord.ext import tasks, commands
from datetime import datetime

import token_loader
import flaustrian_headlines
import database

class DailyNewsCog(commands.Cog):

  #### ---- PSEUDOCONSTANTS ---- ####

  refresh_time='0:00' #time is in 24hr format
  news_post_time='10:00'
  entertainment_post_time='13:30'


  #### ---- HELP METHODS ---- ####

  async def _find_channel(self, name):
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


  #### ---- SETUP METHODS ---- ####

  def __init__(self, bot):
      self.bot = bot
      self.guild_token = token_loader.GUILD

  @commands.Cog.listener()
  async def on_ready(self):
      self.guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
      if self.guild:
          print(f"{self.bot.user} is connected to the following guild:\n{self.guild.name} (id: {self.guild.id})")

          self.entertainment_channel = await self._find_channel("flaustrian_entertainment")
          self.news_channel = await self._find_channel("flaustrian_news")
      else:
          print(f"Can't connect to guild:{self.guild_token}")


  #### ---- SETTING / GETTING HEADLINES FROM DATABASE ---- ####

  def _retrieve_daily_headline(self, category):
    headline_path = self._get_headline_path(self.guild.id, category)
    headline_query = database.get(headline_path)

    if headline_query == None:
      self._generate_daily_headline(category)
      headline_query = database.get(headline_path)

    return headline_query

  def _generate_daily_headline(self, category):
    pass
    # TODO: Implement adding new headline to Firebase


  #### ---- DEBUG COMMANDS ---- ####
  
  # TODO: Refresh daily headlines
  # TODO: Print daily headlines
  # TODO: Change time for refresh/news/entertainment


  #### ---- TIMED TASKS ---- ####

  @tasks.loop(minutes=1.0)
  async def batch_update(self):
      async with self.bot.pool.acquire() as con:
        now=datetime.strftime(datetime.now(),'%H:%M')
        if now == self.refresh_time:
          self.refresh_headlines()
        if now == self.news_post_time:
          self.post_headline("news")
        if now == self.entertainment_post_time:
          self.post_headline("entertainment")
        if now == '15:20':
          self.test_post()

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