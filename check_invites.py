
import discord
from discord.ext import commands
import token_loader
import database
from discord.utils import get, find
import re

class CheckInvitesCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.guild_name = token_loader.FLAUSTRIA_GUILD
    print('check invites loading')

  @commands.Cog.listener()
  async def on_ready(self):
      guild = self.get_guild()
      self.bot_id = self.bot.user.id

      if guild:
        await self.get_invites()
        print(f"{self.bot.user} is connected to the following guild:\n{guild.name} (id: {guild.id})")
      else:
        print(f"Can't connect to guild:{self.guild_name}")

  @commands.command(name='invite')
  async def invite(self, ctx, number_of_invites=None):
    if not ctx.author.guild_permissions.administrator:
      await ctx.send("Sorry, only admins can create invites.")
      return
    elif number_of_invites == None:
      await ctx.send(f'Please enter the number of invites. [example - !invite 10]')
      return
    elif not self.is_only_numbers(number_of_invites):
      await ctx.send(f'{number_of_invites} is not a number. Please enter a number of invites you want to generate. [example - !invite 10]')
      return

    welcome_channel = self.get_channel('welcome')
    for i in range(int(number_of_invites)):
      new_invite = await welcome_channel.create_invite(max_age=0, max_uses=2)
      new_invite_code = new_invite.code
      database.set(f"discord/alpha_invites/{new_invite_code}", True)

    await self.get_invites()
    await ctx.send(f"successfully created {number_of_invites} invites.")
  
  def is_only_numbers(self, text):
      #returns true if text is only numbers with no letters or other characters
      pattern = re.compile(r"\D")
      matches = pattern.findall(text)
      return len(matches) < 1

  @commands.command(name='inv_check')
  async def inv_check(self, ctx):
    if not ctx.author.guild_permissions.administrator:
      await ctx.send("Sorry, only admins can check invites.")
    else:
      await self.get_invites()
      invites_count = len(self.invites)
      await ctx.send(f"invites_count: {invites_count}")

  def get_channel(self, channel_name):
    guild = self.get_guild()
    return discord.utils.get(guild.text_channels, name=channel_name)

  async def get_invites(self):
    guild = self.get_guild()
    self.invites = await guild.invites()
    #print(f"self.invites: {self.invites}")

  @commands.Cog.listener()
  async def on_member_join(self, member):
    is_golden_eagle = await self.is_golden_eagle_invite(member)
    if is_golden_eagle:
      await self.add_role_to_member(member, 'Eagle-Type People')
    await self.add_role_to_member(member, 'Tourist')
    
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    was_new_user = 'Tourist' in [role.name for role in before.roles]
    is_new_user = 'Tourist' in [role.name for role in after.roles]
    if (not was_new_user) and is_new_user:
      await self.bot.get_cog('PersonalityTestCog').begin_test(after)
  
  async def is_golden_eagle_invite(self, member):
    invite = await self.find_matching_invite(member)
    if invite:
      invite_code = invite.code
      alpha_available = database.get(f"discord/alpha_invites/{invite_code}")
      if alpha_available:
        database.set(f"discord/alpha_invites/{invite_code}", False)
        await invite.delete()
        return True
    return False

  async def find_matching_invite(self, member):
    invites_before_join = self.invites
    invites_after_join = await member.guild.invites()
    for ibj in invites_before_join:
      after_join_invite = self.find_invite_by_code(invites_after_join, ibj.code)
      if self.invites_match(ibj, after_join_invite):
        self.invites = invites_after_join
        return ibj
    return None

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