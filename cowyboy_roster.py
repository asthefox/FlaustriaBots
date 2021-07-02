import database
import flaustrian_names
import random

prefixes = []
colors = ["Red", "Orange", "Yellow", "Purple", "Blue"]

def _initialize():
  global prefixes
  filename = "character_names/cowyboy_names.txt"
  with open(filename,'r') as f:
    lines = f.readlines()
    prefixes = list(map(lambda line: line.strip(), lines))

def _get_prefix(id):
  return prefixes[id%len(prefixes)]

def _get_first_name():
  isFemale = random.randint(1, 2) == 1
  isVladagar = random.randint(1, 5) == 1
  isForeign = random.randint(1, 5) == 1
  return flaustrian_names.get_first_name(isFemale, isVladagar, isForeign)

def generate_cowyboy(color, id):
  prefix = _get_prefix(id)
  first_name = _get_first_name()
  power = random.randint(50, 200)
  cowyboy = {
    "id": id,
    "prefix": prefix,
    "first_name": first_name,
    "name": prefix + " " + first_name,
    "color": color,
    "power": power,
    "duels": 0,
    "wins": 0
    }
  return cowyboy

def generate_cowyboy_batch(start_id=1):
  batch = []
  for i in range(5):
    c = generate_cowyboy(colors[i], i + start_id)
    batch.append(c)
  return batch

def get_next_id():
  roster_root = "flaustria/cowyboys/roster/"
  full_roster = database.get(roster_root)
  return len(full_roster)

def write_cowyboy_data(cowyboy):
  root = "flaustria/cowyboys/roster/" + str(cowyboy["id"])
  database.set(root, cowyboy)
  """
  database.set(root + "/id", cowyboy["id"])
  database.set(root + "/prefix", cowyboy["prefix"])
  database.set(root + "/first_name", cowyboy["first_name"])
  database.set(root + "/name", cowyboy["name"])
  database.set(root + "/color", cowyboy["color"])
  database.set(root + "/power", cowyboy["power"])
  database.set(root + "/wins", cowyboy["wins"])
  database.set(root + "/duels", cowyboy["duels"])
  """

def _read_cowyboy_data(id):
  root = "flaustria/cowyboys/roster/" + str(id)
  cowyboy = database.get(root)
  """
  cowyboy = {"id": id}
  cowyboy["prefix"] = database.get(root + "/prefix")
  cowyboy["first_name"] = database.get(root + "/first_name")
  cowyboy["name"] = database.get(root + "/name")
  cowyboy["color"] = database.get(root + "/color")
  cowyboy["power"] = database.get(root + "/power")
  cowyboy["wins"] = database.get(root + "/wins")
  cowyboy["duels"] = database.get(root + "/duels")
  """
  return cowyboy

def write_current_ids(id_list):
  database.set("flaustria/cowyboys/current", id_list)

def seed_initial_cowyboys():
  batch = generate_cowyboy_batch(0)
  for cowyboy in batch:
    write_cowyboy_data(cowyboy)
  ids = list(map(lambda c: c["id"], batch))
  write_current_ids(ids)

_initialize()