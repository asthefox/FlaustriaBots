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

# data to save
test_balance_updates = {
    "Tranandez": "5000",
    "Wongowitz" : "2500"
}

# Pass the user's idToken to the push method
results = db.child("discord").child("bank_accounts").set(test_balance_updates, user['idToken'])