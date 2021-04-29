
import discord
from discord.ext import commands
import token_loader
from collections import namedtuple
import database

Answer = namedtuple('Answer', 'emoji text')
Question = namedtuple('Question', 'id text answers')

class Test():
  def __init__(self):
    self.questions = [
      Question('1', 'What is your name?', [ Answer('🐍', 'Snake'), Answer('🐔', 'Chicken') ]),
      Question('2', 'Where were you born?', [ Answer('🐍', 'Snake'), Answer('🐔', 'Chicken') ]),
      Question('3', 'What is your favorite color??', [ Answer('🐍', 'Snake'), Answer('🐔', 'Chicken') ])
    ]

class PersonalityTestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_token = token_loader.GUILD
        self.test = Test()
        print(self.test.questions)

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
      await self.ask_question_or_end_test(ctx.channel, ctx.author)

    @commands.command(name="find_record")
    async def find_record(self, ctx):
      user_id = ctx.author.id
      test_record = self.get_test_record(user_id)
      await ctx.send(f"found test_record: {test_record}")
      qi = self.get_question_index_from_test_record(test_record)
      await ctx.send(f"current_index: {qi}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
      if reaction.count > 1:
        response = f'answer: {reaction.emoji}'
        await reaction.message.channel.send(response)

        qi = self.get_question_index(user.id)
        self.set_question_answer(user.id, qi, response)
        await self.ask_question_or_end_test(reaction.message.channel, user)

    async def ask_question_or_end_test(self, channel, user):
      qi = self.get_question_index(user.id)
      if qi >= len(self.test.questions):
          await self.end_test(channel)
      else:
        await self.ask_question(channel, user)

    async def ask_question(self, channel, user):
      qi = self.get_question_index(user.id)
      question = self.test.questions[qi]
      msg_text = question.text
      for answer in question.answers:
        msg_text += f"\n{answer.emoji} - {answer.text}"
      msg = await channel.send(msg_text)
      for answer in question.answers:
        await msg.add_reaction(emoji=answer.emoji)
    
    async def end_test(self, channel):
      await channel.send('The test is over, you have a personality!')

    def set_question_answer(self, user_id, index, answer):
      database.set(f"discord/personality_tests/{user_id}/{index}", answer)

    def get_question_index(self, user_id):
      test_record = self.get_test_record(user_id)
      return self.get_question_index_from_test_record(test_record)

    def get_test_record(self, user_id):
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


def setup(bot):
    bot.add_cog(PersonalityTestCog(bot))