import discord
from discord.ext import commands
import token_loader
import random

class GlauconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_token = token_loader.GUILD

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.find(lambda g: g.name == self.guild_token, self.bot.guilds)
        if guild:
            print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
            self.print_guild_members(guild)
        else:
            print(f"Can't connect to guild:{self.guild_token}")

    @commands.Cog.listener()
    async def on_message(self,message):
      if message.author == self.bot.user: 
            return

      glaucon_command = '!glaucon' in message.content.lower()
      reload_command = '!reload' in message.content.lower()
      
      if glaucon_command:
        await self.repond_to_glaucon_command(message)
      elif reload_command:
        await self.reload_extension(message)

    async def repond_to_glaucon_command(self, message):
      examined = 'philosophy' in message.content.lower()
      response = 'The unexamined life is not worth living.' if examined else self.get_random_response(message.author)
      await message.channel.send(response)

    def print_guild_members(self,guild):
        members_len = len(guild.members)
        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members ({members_len}):\n - {members}')

    def get_random_response(self,interlocutor):
        responses = [
            'Surely!', 'Certainly!', 'Of course!',
            'How could it be any other way?', f'Yes, {interlocutor}.',
            f'Your mind is a marvel, {interlocutor}!'
        ]
        return random.choice(responses)
    
    async def reload_extension(self, message):
      message_split = message.content.lower().split(' ')
      extension_name = message_split[1]
      self.bot.reload_extension(extension_name)
      response = f'reloading  {extension_name}'
      await message.channel.send(response)
    

def setup(bot):
    bot.add_cog(GlauconCog(bot))