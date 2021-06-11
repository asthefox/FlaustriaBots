
import discord
from discord.ext import commands
import token_loader
from collections import namedtuple
import database
from discord.utils import get, find


class CheckInvitesCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.guild_name= 'dmershon test server'
    print('check invites loading')

  @commands.Cog.listener()
  async def on_ready(self):
      guild = self.get_guild()
      self.bot_id = self.bot.user.id
      
      if guild:
          print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
      else:
          print(f"Can't connect to guild:{self.guild_name}")

  @commands.command(name="invites")
  async def invites(self, ctx):
    await self.get_invites()
    invites_count = len(self.invites)
    await ctx.send(f"invites_count: {invites_count}")

  async def get_invites(self):
    guild = self.get_guild()
    self.invites = await guild.invites()

  @commands.Cog.listener()
  async def on_member_join(self, member):
    await self.add_role_to_member(member, 'NewUser')
    await self.check_member_invites(member)
    
  async def check_member_invites(self, member):
    invites_before_join = self.invites
    invites_after_join = await member.guild.invites()
    for ibj in invites_before_join:
      after_join_invite = self.find_invite_by_code(invites_after_join, ibj.code)
      if self.invites_match(ibj, after_join_invite):
        self.print_matching_invite(member, ibj)      
        self.invites = invites_after_join

  def print_matching_invite(self, member, invite):
    print(f"Member {member.name} Joined")
    print(f"Invite Code: {invite.code}")
    print(f"Inviter: {invite.inviter}")

  def invites_match(self, before_join_invite, after_join_invite):
    return after_join_invite and before_join_invite.uses < after_join_invite.uses

  def find_invite_by_code(self, invite_list, code):
    for inv in invite_list:
        if inv.code == code:
            return inv

  @commands.Cog.listener()
  async def on_member_remove(self, member):
    self.invites = await member.guild.invites()

  async def add_role_to_member(self, member, role_name):
    role = get(self.get_guild().roles, name=role_name)
    await member.add_roles(role)
  
  def get_guild(self):
    return discord.utils.get(self.bot.guilds, name=self.guild_name)

def setup(bot):
    bot.add_cog(CheckInvitesCog(bot))