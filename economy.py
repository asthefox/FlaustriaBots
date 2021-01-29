from firebase import Firebase
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import token_loader

project_id = "fir-test-for-atb-default-rtdb"
config = {
  "apiKey": token_loader.FIREBASE,
  "authDomain": f"{project_id}.firebaseapp.com",
  "databaseURL": f"https://{project_id}.firebaseio.com",
  "storageBucket": f"pro{project_id}jectId.appspot.com"
}


# data to save
test_balance_updates = {
    "Tranandez": "5000",
    "Wongowitz" : "2500"
}


class Economy(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
      print('Economy Cog Ready!')
      print('Logged in as ---->', self.bot.user)
      print('ID:', self.bot.user.id)
      await self._init_database()

  def _init_database(self):
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
    self.balances = db.child("discord").child("bank_accounts")

    @commands.command(name="atm")
    async def check_balance(self, ctx):
        bal = await _balance(ctx.author)
        ctx.send("Your balance is: " + str(bal) + "k")
        


  @commands.Cog.listener()
  async def on_message(self, message):
      print(message)



  async def _balance(self, member):
    guild = guild.id
    guild_balances = self.balances.get_child(guild.id)
    my_balance = guild_balances.order_by_child("id").equal_to(member.id).get().val()

    if len(my_balance) == 0:
      my_balance = {"id": member.id, "balance": 100}
      guild_balances.push(new_entry)
      # Balance not found, make a new one
    else:
      my_balance = my_balance[0]

    return my_balance["balance"]


  async def withdraw_money(self, member, money):
    
      # Pass the user's idToken to the push method
      results = self.db.child("discord").child("bank_accounts").set(test_balance_updates, user['idToken'])


  async def deposit_money(self, member, money):
      # implementation here
      ...
