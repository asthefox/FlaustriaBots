import discord
from discord.ext import commands

class AdminTools(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      self.guild_name = 'dmershon test server'

  @commands.Cog.listener()
  async def on_ready(self):
      print('AdminTools Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)

  @commands.command(name="print_users")
  async def print_users(self, ctx):
    if not ctx.author.guild_permissions.administrator:
      await ctx.send("Sorry, only admins can create invites.")
      return

    message = 'printing guild members...'
    guild = self.get_guild()
    for member in guild.members:
      message += f"\nname: {member.name} id: {member.id}"
    await ctx.send(message)

  def get_guild(self):
    return discord.utils.get(self.bot.guilds, name=self.guild_name)

def setup(bot):
    bot.add_cog(AdminTools(bot))