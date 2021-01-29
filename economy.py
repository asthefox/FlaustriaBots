from firebase import Firebase
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import token_loader


class Economy(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
      print('Economy Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)
      self._init_database()

  def _init_database(self):
    project_id = "fir-test-for-atb-default-rtdb"
    config = {
      "apiKey": token_loader.FIREBASE,
      "authDomain": f"{project_id}.firebaseapp.com",
      "databaseURL": f"https://{project_id}.firebaseio.com",
      "storageBucket": f"pro{project_id}jectId.appspot.com"
    }

    firebase = Firebase(config)

    # Get a reference to the auth service
    auth = firebase.auth()

    # Log the user in
    load_dotenv()
    username = os.getenv('FIREBASE_USERNAME')
    password = os.getenv('FIREBASE_PASSWORD')
    self.user = auth.sign_in_with_email_and_password(username, password)

    # Get a reference to the database service
    self.db = firebase.database()
    self.balances = self.db.child("discord").child("bank_accounts")

  @commands.command(name="atm")
  async def check_balance(self, ctx):
      await ctx.send("You have money!")
      bal = await self._balance(ctx)
      await ctx.send("Your balance is: " + str(bal) + "k")

  @commands.Cog.listener()
  async def on_message(self, message):
      print(message)

  async def _balance(self, ctx):
    member = ctx.author.id
    guild = ctx.guild.id

    # Check if guild exists in database
    guild_query = self.balances.order_by_child("guild_id").equal_to(guild).get().val()

    if len(guild_query) == 0:
      # Guild not found, make a new one
      print("Debug: Creating new guild entry " + str(guild))
      my_guild = {"guild_id": guild, "balances": []}
      #self.balances.set(my_guild)
      self.balances.child(guild)



    guild_balances = self.balances.child(guild)
    my_balance_query = guild_balances.order_by_child("id").equal_to(member).get().val()

    print(*my_balance_query)

    if len(my_balance_query) == 0:
      # Balance not found, make a new one
      await ctx.send("Debug: Creating balance entry for user " + str(member) + " in guild " + str(guild))
      my_balance = {"id": member, "balance": 100}
      guild_balances.push(my_balance)

    else:
      my_balance = my_balance[0]

    return my_balance["balance"]


  async def withdraw_money(self, guild_id, member_id, money):
    pass
    # Pass the user's idToken to the push method
    # results = self.db.child("discord").child("bank_accounts").set$(test_balance_updates, user['idToken'])


  async def deposit_money(self, guild_id, member_id, money):
    # implementation here
    pass

def setup(bot):
    bot.add_cog(Economy(bot))