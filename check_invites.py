
import discord
from discord.ext import commands
import token_loader
from collections import namedtuple
import database
from discord.utils import get, find


class CheckInvitesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.guild_name= token_loader.FLAUSTRIA_GUILD
        print('CheckInvitesCog')

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.get_guild()
        self.bot_id = self.bot.user.id

        if guild:
            print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
        else:
            print(f"Can't connect to guild:{self.guild_name}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
      await self.add_role_to_member(member, 'NewUser')
      dm = await member.create_dm()
      await self.test_message(dm)

    async def test_message(self, channel):
      await channel.send(f"test message")

    async def add_role_to_member(self, member, role_name):
      role = get(self.get_guild().roles, name=role_name)
      await member.add_roles(role)
    
    def get_guild(self):
      return discord.utils.get(self.bot.guilds, name=self.guild_name)

def setup(bot):
    bot.add_cog(CheckInvitesCog(bot))