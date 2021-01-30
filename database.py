from firebase import Firebase
import os
from dotenv import load_dotenv
import token_loader

def get(path):
  if db == None:
    print("Firebase Wrapper Error: The Firebase has not been initialized.")
  return db.child(path).get(user['idToken']).val()
  # Continue migrating 

def set(path, value):
  if db == None:
    print("Firebase Wrapper Error: The Firebase has not been initialized.")
  db.child(path).set(value, user['idToken'])


def update(path, value):
  if db == None:
    print("Firebase Wrapper Error: The Firebase has not been initialized.")
  db.child(path).update(value, user['idToken'])





def _init_database():

  global user
  global db

  print("Initializing database...")

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
  user = auth.sign_in_with_email_and_password(username, password)

  # Get a reference to the database service
  db = firebase.database()

_init_database()

