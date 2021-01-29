import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
INSIDE_TRACK_TOKEN = os.getenv('INSIDE_TRACK_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
FIREBASE = os.getenv('FIREBASE_TOKEN')