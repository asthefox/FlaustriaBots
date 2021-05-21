
import discord
from discord.ext import commands
import token_loader
from collections import namedtuple
import database
from discord.utils import get, find

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
    record_path = f"discord/personality_tests/{user_id}/answers"
    result = database.get(record_path)
    if not result:  
      print(f"adding new test record for user_id: {user_id}")
      database.set(record_path, ["" for question in self.test.questions])
    return result if result else self.get_test_record(user_id)

  def set_role_record(self, user_id, role):
    database.set(f"discord/personality_tests/{user_id}/role", role)

  def get_role_record(self, user_id):
    return database.get(f"discord/personality_tests/{user_id}/role")
  
  def get_question_index_from_test_record(self, test_record):
    index = 0
    for answer in test_record:
      if answer == '':
        return index
      index += 1
    return index

  def set_question_answer(self, user_id, index, answer):
    database.set(f"discord/personality_tests/{user_id}/answers/{index}", answer)


class PersonalityTestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_name= token_loader.FLAUSTRIA_GUILD
        self.test = Test()
        self.tr = TestRecord(self.test)
        self.bot_id = bot.user.id
        print('personality test loaded')

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.get_guild()

        if guild:
            print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
            print(f"self.guild.name: {self.guild.name}")
        else:
            print(f"Can't connect to guild:{self.guild_name}")

    def get_guild(self):
      return discord.utils.get(self.bot.guilds, name=self.guild_name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
      await self.add_role_to_member(member, 'NewUser')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
      was_new_user = 'NewUser' in [role.name for role in before.roles]
      is_new_user = 'NewUser' in [role.name for role in after.roles]
      if (not was_new_user) and is_new_user:
        await self.begin_test(after)

    async def begin_test(self, member):
      dm = await member.create_dm()
      await self.ask_question_or_end_test(dm, member.id)

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
          await self.end_test(channel, user_id)
      else:
        await self.ask_question(channel, user_id)

    async def ask_question(self, channel, user_id):
      qi = self.tr.get_question_index(user_id)
      question = self.test.questions[qi]
      msg = await channel.send(f"{question.id}. {question.text}")

      for answer in question.answers:
        await msg.add_reaction(emoji=answer)
    
    async def end_test(self, channel, user_id):
      test_record = self.tr.get_test_record(user_id)
      last_answer = test_record[len(self.test.questions) - 1]
      roles = { 
        '🐍' : 'MongooseMinistry', 
        '💰' : 'MarketMinistry',
        '☀' : 'SunMinistry',
        '📕' : 'BookMinistry',
        '☠' : 'MoonMinistry' 
      }
      role_name = roles[last_answer]
      self.tr.set_role_record(user_id, role_name)
      await self.add_role_to_user(channel, user_id, role_name)
      await self.add_role_to_user(channel, user_id, 'FlaustrianCitizen')
      await self.remove_role_from_user(channel, user_id, 'NewUser')
      ministry_name = self.get_ministry(role_name)

      msg = f"Congratulations! You are now a Flaustrian citizen and you can now enjoy all Flaustria has to offer. Let me recommend some channels:\n -Discuss Flaustrian news and entertainment!\n -Better yourself morally by betting on daily Cowyboy duels!\n -Petition to join the exclusive alpha of Astronaut: The Best!\n -Join your coworkers at the {ministry_name}"
      
      embed = self.get_link_to_atb_discord()
      await channel.send(msg, embed=embed)

    def get_link_to_atb_discord(self):
      embed = discord.Embed()
      link = "https://discord.com/channels/801299215983837246/801299217083269151"
      embed.description = f"[Click to return to AtB Discord]({link})."
      return embed

    def get_ministry(self, role_name):
      ministries = { 
        'MongooseMinistry' : 'The Ministry of Defense Against Serpents', 
        'MarketMinistry' : 'The Ministry of Limited-Time Offers',
        'SunMinistry' : 'The Ministry of Righteous Shaming',
        'BookMinistry' : 'The Ministry of Forbidden Knowledge',
        'MoonMinistry' : 'The Ministry of Love and Death' 
      }
      return ministries[role_name]

    async def add_role_to_member(self, member, role_name):
      role = get(self.get_guild().roles, name=role_name)
      await member.add_roles(role)

    async def add_role_to_user(self, channel, user_id, role_name):
      member = find(lambda m: m.id == user_id, self.get_guild().members)
      await self.add_role_to_member(member, role_name)

    async def remove_role_from_user(self, channel, user_id, role_name):
      member = find(lambda m: m.id == user_id, self.get_guild().members)
      await self.remove_role_from_member(member, role_name)

    async def remove_role_from_member(self, member, role_name):
      role = get(self.get_guild().roles, name=role_name)
      await member.remove_roles(role)
      


def setup(bot):
    bot.add_cog(PersonalityTestCog(bot))