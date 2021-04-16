import discord
from discord.ext import commands
import token_loader

class PersonalityTestCog(commands.Cog):
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

      valid_command = '!personality' in message.content.lower()
      
      if valid_command:
        response = 'T T T Testing personality test bot...'
        await message.channel.send(response)


def setup(bot):
    bot.add_cog(PersonalityTestCog(bot))