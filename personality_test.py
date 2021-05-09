
import discord
from discord.ext import commands
import token_loader
from collections import namedtuple
import database

Question = namedtuple('Question', 'id text answers')

class Test():
  def __init__(self):
    self.questions = [
      Question('1', "Welcome to Flaustria! To post here, you'll need to become a Flaustrian citizen. (click ▶ to continue)\n", [ '▶' ]),
      Question('2', "Sign this thing saying that you'll post about Flaustrian news, entertainment, and Astronaut: The Best and leave behind your baggage from the old crappy world.\nYou're welcome to make up stuff about Flaustria, and it might become canon. (click ✅ to sign loyalty oath)\n", [ '✅' ]),
      Question('3', "In Flaustria, all citizens are expected to pay devotion to The Five Gods. So you'll need to join one of the five ministries, overseen by one of the High Priests. Which would you like to join?\n -The Ministry of Defense Against Serpents, run by Starnat, High Priest of The Mongoose (click 🐍)\n -The Ministry of Limited-Time Offers, run by Inside-Track, High Priest of The Market (click 💰)\n -The Ministry of Righteous Shaming, run by Correblanch, High Priest of The Sun (click ☀)\n -The Ministry of Forbidden Knowledge, run by Rulu, High Priest of The Book (click 📕)\n -The Ministry of Love and Death, run by Morningdew, High Priest of The Moon (click ☠)\n\n", [ '🐍', '💰', '☀', '📕', '☠' ])
    ]

class TestRecord():
  def __init__(self, test):
    self.test = test

  def get_question_index(self, user_id):
      test_record = self.get_test_record(user_id)
      return self.get_question_index_from_test_record(test_record)

  def get_test_record(self, user_id):
    database.refresh_token()
    record_path = f"discord/personality_tests/{user_id}"
    result = database.get(record_path)
    if not result:  
      print(f"adding new test record for user_id: {user_id}")
      database.set(record_path, ["" for question in self.test.questions])

    return result if result else self.get_test_record(user_id)
  
  def get_question_index_from_test_record(self, test_record):
    index = 0
    for answer in test_record:
      if answer == '':
        return index
      index += 1
    return index

  def set_question_answer(self, user_id, index, answer):
    database.refresh_token()
    database.set(f"discord/personality_tests/{user_id}/{index}", answer)


class PersonalityTestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_token = token_loader.GUILD
        self.test = Test()
        self.tr = TestRecord(self.test)
        self.bot_id = bot.user.id
        print('personality test loaded')

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
        if guild:
            print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
            self.print_guild_members(guild)
        else:
            print(f"Can't connect to guild:{self.guild_token}")

    @commands.command(name="test")
    async def test(self, ctx):
      dm = await ctx.author.create_dm()
      await self.ask_question_or_end_test(dm, ctx.author.id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
      if payload.user_id == self.bot_id:
        return

      channel = self.bot.get_channel(payload.channel_id)
      message = await channel.fetch_message(payload.message_id)
      msg_split = message.content.split('.')
      response_qi = int(msg_split[0]) - 1
      qi = self.tr.get_question_index(payload.user_id)
      if response_qi != qi or message.author.id != self.bot_id:
        return

      self.tr.set_question_answer(payload.user_id, qi, payload.emoji.name)
      await self.ask_question_or_end_test(message.channel, payload.user_id)

    async def ask_question_or_end_test(self, channel, user_id):
      qi = self.tr.get_question_index(user_id)
      if qi >= len(self.test.questions):
          await self.end_test(channel)
      else:
        await self.ask_question(channel, user_id)

    async def ask_question(self, channel, user_id):
      qi = self.tr.get_question_index(user_id)
      question = self.test.questions[qi]
      msg = await channel.send(f"{question.id}. {question.text}")

      for answer in question.answers:
        await msg.add_reaction(emoji=answer)
    
    async def end_test(self, channel):
      msg = "Congratulations! You are now a Flaustrian citizen and can enjoy all Flaustria has to offer. Let me recommend some channels:\n -Discuss Flaustrian news and entertainment!\n -Better yourself morally by betting on daily Cowyboy duels!\n -Petition to join the exclusive alpha of Astronaut: The Best!"
      await channel.send(msg)
    


def setup(bot):
    bot.add_cog(PersonalityTestCog(bot))