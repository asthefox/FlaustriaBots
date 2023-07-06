import discord
from discord.ext import commands
import database

class Economy(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
      print('Economy Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)


  @commands.command(name="atm")
  async def check_balance(self, ctx):
      #await ctx.send("You have money!")
      bal = self._balance(ctx.guild, ctx.author)
      await ctx.send("Your balance is: " + str(bal) + "k")

  @commands.command(name="award")
  async def admin_give_money(self, ctx, member_name, amount):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Sorry, only admins can give k awards.")
        return
    member = ctx.guild.get_member_named(member_name)
    if member == None:
      await ctx.send("A Flaustrian named " + member_name + " cannot be found.")
      return
    try:
      amount = int(amount)
    except:
      await ctx.send("That is not a valid integer amount.")
      return

    display_name = member.nick
    if display_name == None:
      display_name = member.name
    balance = self._balance(ctx.guild, member)
    balance += amount
    balance_path = self._get_balance_path(ctx.guild.id, member.id)
    database.update(balance_path, {"balance": balance})
    await ctx.send(display_name + " has been awarded " + str(amount) + "k, and now has a balance of " + str(balance) + "k.")

  @commands.command(name="charge")
  async def admin_charge_money(self, ctx, member_name, amount):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Sorry, only admins can give k awards.")
        return
    member = ctx.guild.get_member_named(member_name)
    if member == None:
      await ctx.send("A Flaustrian named " + member_name + " cannot be found.")
      return
    try:
      amount = int(amount)
    except:
      await ctx.send("That is not a valid integer amount.")
      return

    display_name = member.nick
    if display_name == None:
      display_name = member.name
    balance = self._balance(ctx.guild, member)
    if balance < amount:
      await ctx.send(display_name + " only has " + str(balance) + "k, and cannot be charged " + str(amount) + " k.")
      return
    balance -= amount
    balance_path = self._get_balance_path(ctx.guild.id, member.id)
    database.update(balance_path, {"balance": balance})
    await ctx.send(display_name + " has been charged " + str(amount) + "k, and now has a balance of " + str(balance) + "k.")

  #@commands.Cog.listener()
  #async def on_message(self, message):
  #    print(message)

  def _get_balance_path(self, guild_id, member_id):
    return "discord/bank_accounts/" + str(guild_id) + "/" + str(member_id)


  def _balance(self, guild, member):
    balance_path = self._get_balance_path(guild.id, member.id)
    balance_query = database.get(balance_path)
    #balance_query = self.db.child(balance_path).get(self.user['idToken']).val()

    #print(balance_query)

    if balance_query == None:
      # Balance not found, make a new one
      #print("Debug: Creating balance entry for user " + str(member) + " in guild " + str(guild))
      my_balance = {"name": member.name, "balance": 100}
      database.set(balance_path, my_balance)
      #self.db.child(balance_path).set(my_balance, self.user['idToken'])
      return int(my_balance["balance"])

    return int(balance_query["balance"])


  def withdraw_money(self, guild, member, money):
    balance = self._balance(guild, member)
    if balance < money:
      return (False, balance)

    balance -= money
    balance_path = self._get_balance_path(guild.id, member.id)
    database.update(balance_path, {"balance": balance})
    #self.db.child(balance_path).update({"balance": balance}, self.user['idToken'])

    return (True, balance)


  def get_balance(self, guild, member):
    return self._balance(guild, member)

  def deposit_money(self, guild, member, money):
    balance = self._balance(guild, member)
    balance += money
    balance_path = self._get_balance_path(guild.id, member.id)
    database.update(balance_path, {"balance": balance})
    #self.db.child(balance_path).update({"balance": balance}, self.user['idToken'])

async def setup(bot):
    await bot.add_cog(Economy(bot))