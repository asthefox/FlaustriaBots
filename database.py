from firebase import Firebase
import os
from dotenv import load_dotenv
import token_loader
from time import time

def get(path):
  refresh_token()
  if db == None:
    print("Firebase Wrapper Error: The Firebase has not been initialized.")
  return db.child(path).get(user['idToken']).val()

def set(path, value):
  refresh_token()
  if db == None:
    print("Firebase Wrapper Error: The Firebase has not been initialized.")
  db.child(path).set(value, user['idToken'])

def push(path, value):
  refresh_token()
  if db == None:
    print("Firebase Wrapper Error: The Firebase has not been initialized.")
  db.child(path).push(value, user['idToken'])

def update(path, value):
  refresh_token()
  if db == None:
    print("Firebase Wrapper Error: The Firebase has not been initialized.")
  db.child(path).update(value, user['idToken'])

def refresh_token():
  time_left = get_token_expiration()
  #refresh token if there's less than 1 minute left
  if time_left > 60:
    return

  global user
  global firebase
  auth = firebase.auth()
  user = auth.refresh(user['refreshToken'])
  set_next_token_refresh_time()

def get_token_expiration():
  global next_refresh_time
  return next_refresh_time - time()

def set_next_token_refresh_time():
  global next_refresh_time
  #tokens expire after 1 hour so I'm setting a refresh time at 3600
  token_length_seconds = 3600
  next_refresh_time = time() + token_length_seconds

def _init_database():
  global user
  global db
  global firebase

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
  set_next_token_refresh_time()

  # Get a reference to the database service
  db = firebase.database()

_init_database()

