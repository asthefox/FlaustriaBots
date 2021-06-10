
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
      Question('1', "Welcome to the **Flaustrian Command Center** server! If you want to participate in our community or access our famous **Alpha**, you'll need to become a Flaustrian citizen. All you have to do is complete a quick and tidy **loyalty oath**. \n(click ▶ to start the process)\n", [ '▶' ]),
      Question('2', "Wondrous! The first step towards citizens is agreeing to abide by the rules of Flaustria, set forth by the Five Gods in time immemorial. Simply sign this oath:\n\n:one:. I will not perpetrate harassment, racism, sexism, abuse, intimidation, threats, discrimination, or toxic behavior of any kind. I understand that any violations will result in my immediate expulsion into the cold, harsh void of the Internet.\n\n:two:. I will leave behind my baggage from neighboring universes, and not introduce any religious, political, salacious, gory, or otherwise controversial topics that could upset the local ecosystem.\n\n:three:. I will observe the mores of polite Flaustrian society. I will keep my conversations PG-13, and always remember that I am conversing with actual humans with different backgrounds, values, cultures, and personalities.\n\n:four:. Though I will not fear to share my ~~failures~~successes with the Flaustrian media, nor will I place myself above the Five Gods by self-promoting to an irritating extent.\n\n:five:. I will not blaspheme against the Five High Priests, nor promote any heretical Vladagar heterodoxy.\n\n(click ✅ to sign oath)\n", [ '✅' ]),
      Question('3', "Well done! I have no doubt you'll become a sterling member of our community.\n\nNow, our humble universe is still growing, and it's an effort we all share. You are invited to contribute to discussions about Flaustrian news and events by, er… making things up. I have heard that events and facts about Flaustria from this server might become \"canon,\" whatever that means.\n(click ▶ to continue)\n", [ '▶' ]),
      Question('4', "In Flaustria, all citizens are expected to pay devotion to The Five Gods. As such, you'll need to join one of the five ministries, overseen by one of the High Priests. Which is your choice?\n -The Ministry of Defense Against Serpents, run by Starnat, High Priest of The Mongoose (click 🐍)\n -The Ministry of Limited-Time Offers, run by Inside-Track, High Priest of The Market (click 💰)\n -The Ministry of Righteous Shaming, run by Correblanch, High Priest of The Sun (click ☀)\n -The Ministry of Forbidden Knowledge, run by Rulu, High Priest of The Book (click 📕)\n -The Ministry of Love and Death, run by Morningdew, High Priest of The Moon (click ☠)", [ '🐍', '💰', '☀', '📕', '☠' ])
    ]

    self.eagle_response = Question('1', "Ah, congratulations! You're somewhat of a VIP. Normally one would have to complete a test of valor before gaining the honor of accessing the **Astronaut: The Best alpha**, but I've been told you can skip all that.\n\nSo without further ado: <#807380325562449930>.\n\nOh, right! If you'd like to participate in the other activities our humble server has to offer, I can help you gain Flaustrian citizenship. Just click the arrow below to proceed. \n(click ▶ to start the process)\n", [ '▶' ]),

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
        print('personality test loaded')

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.get_guild()
        self.bot_id = self.bot.user.id

        if guild:
            print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
        else:
            print(f"Can't connect to guild:{self.guild_name}")

    def get_guild(self):
      return discord.utils.get(self.bot.guilds, name=self.guild_name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
      await self.add_role_to_member(member, 'Tourist')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
      was_new_user = 'Tourist' in [role.name for role in before.roles]
      is_new_user = 'Tourist' in [role.name for role in after.roles]
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
        '🐍' : 'Mongoose Ministry', 
        '💰' : 'Market Ministry',
        '☀' : 'Sun Ministry',
        '📕' : 'Book Ministry',
        '☠' : 'Moon Ministry' 
      }
      role_name = roles[last_answer]
      self.tr.set_role_record(user_id, role_name)
      await self.add_role_to_user(channel, user_id, role_name)
      await self.add_role_to_user(channel, user_id, 'Flaustrian Citizen')
      await self.remove_role_from_user(channel, user_id, 'Tourist')
      ministry_name = self.get_ministry(role_name)

      msg = "Congratulations! You are now a Flaustrian citizen, and you can now enjoy all Flaustria has to offer.\n\nAllow me to humbly recommend some activities:\n -Discuss the latest <#832427377967628288> and <#832378973161521192>!\n -Better yourself morally by betting on daily <#850534625319321601>!\n -Petition to join the exclusive **alpha of Astronaut: The Best** with <#850528747853709334>!"
      
      embed = self.get_link_to_atb_discord()
      await channel.send(msg, embed=embed)

    def get_link_to_atb_discord(self):
      embed = discord.Embed()
      link = "https://discord.com/channels/801299215983837246/801299217083269151"
      embed.description = f"[Click to return to the Flaustrian Command Center]({link})."
      return embed

    def get_ministry(self, role_name):
      ministries = { 
        'Mongoose Ministry' : 'The Ministry of Defense Against Serpents', 
        'Market Ministry' : 'The Ministry of Limited-Time Offers',
        'Sun Ministry' : 'The Ministry of Righteous Shaming',
        'Book Ministry' : 'The Ministry of Forbidden Knowledge',
        'Moon Ministry' : 'The Ministry of Love and Death' 
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