from firebase import Firebase
import os
from dotenv import load_dotenv

project_id = "fir-test-for-atb-default-rtdb"
config = {
  "apiKey": " AIzaSyCl0QkTls5X2q8wZarfdq1bW9kBPryhrsA ",
  "authDomain": f"{project_id}.firebaseapp.com",
  "databaseURL": f"https://{project_id}.firebaseio.com",
  "storageBucket": f"pro{project_id}jectId.appspot.com"
}

def test_print_config():
    for key in config.keys():
        value = config[key]
        print(f"{ key }:{ value }")

firebase = Firebase(config)

# Get a reference to the auth service
auth = firebase.auth()

# Log the user in
load_dotenv()
username = os.getenv('FIREBASE_USERNAME')
password = os.getenv('FIREBASE_PASSWORD')
user = auth.sign_in_with_email_and_password(username, password)

# Get a reference to the database service
db = firebase.database()

def test1():

  # data to save
  test_balance_updates = {
      "Tranandez": "5000",
      "Wongowitz" : "2500"
  }

  # Pass the user's idToken to the push method
  results = db.child("discord").child("bank_accounts").set(test_balance_updates, user['idToken'])

def test2():
  accounts = db.child("discord").child("bank_accounts")
  spoof_guild_id = 982658975236
  spoof_user_id = 32895912531
  spoof_user_nickname = "jonny moneyhaver"

  user_info = { "balance": 100, "name": spoof_user_nickname}
  accounts.child(spoof_guild_id).child(spoof_user_id).set(user_info, user['idToken'])

def test3():
  accounts = db.child("discord").child("bank_accounts")
  spoof_guild_id = 982658975236
  spoof_user_id = 32895912531
  bad_user_id = 59382
  bad_guild_id = 386955
  balance = accounts.child(bad_guild_id).child(spoof_user_id).get(user['idToken'])
  print(balance.val())

test3()