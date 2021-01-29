from firebase import Firebase
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

project_id = "fir-test-for-atb-default-rtdb"
config = {
  "apiKey": " AIzaSyCl0QkTls5X2q8wZarfdq1bW9kBPryhrsA ",
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
      await init_database()

  def init_database():
    firebase = Firebase(config)

    # Get a reference to the auth service
    auth = firebase.auth()

    # Log the user in
    load_dotenv()
    username = os.getenv('FIREBASE_USERNAME')
    password = os.getenv('FIREBASE_PASSWORD')
    user = auth.sign_in_with_email_and_password(username, password)

    # Get a reference to the database service
    self.db = firebase.database()

  @commands.Cog.listener()
  async def on_message(self, message):
      print(message)


  async def withdraw_money(self, member, money):
      # implementation here
      # Pass the user's idToken to the push method
      results = db.child("discord").child("bank_accounts").set(test_balance_updates, user['idToken'])


  async def deposit_money(self, member, money):
      # implementation here
      ...
