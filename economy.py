#from firebase import Firebase
#import os
#from dotenv import load_dotenv
import discord
from discord.ext import commands
#import token_loader
import database

class Economy(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
      print('Economy Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)
      #self._init_database()


  """
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
  """

  @commands.command(name="atm")
  async def check_balance(self, ctx):
      await ctx.send("You have money!")
      bal = self._balance(ctx.guild, ctx.author)
      await ctx.send("Your balance is: " + str(bal) + "k")

  @commands.Cog.listener()
  async def on_message(self, message):
      print(message)

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
      return my_balance["balance"]

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
    

  def deposit_money(self, guild, member, money):
    balance = self._balance(guild, member)
    balance += money
    balance_path = self._get_balance_path(guild.id, member.id)
    database.update(balance_path, {"balance": balance})
    #self.db.child(balance_path).update({"balance": balance}, self.user['idToken'])

def setup(bot):
    bot.add_cog(Economy(bot))