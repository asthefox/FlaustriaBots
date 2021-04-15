import random
import re
import datetime
import flaustrian_names
import string

keywords = {}
special_headlines = {}

# TODO: {number_min_max (positional)}
# TODO: {name_(f|m|first|last) (keyword)}

def initialize():
  load_keywords("keywords_general.txt")
  load_keywords("keywords_entertainment.txt")
  load_keywords("keywords_events.txt")
  load_special_headlines("special_headlines.txt")

def load_keywords(filename):
  with open(filename,'r') as f:
    templates = f.readlines()
    for line in templates:
      data = line.split(";")
      if len(data) != 2:
        continue
      key, value = data
      key = "[" + key + "]"
      value = value.strip()
      if key in keywords:
        keywords[key].append(value)
      else:
        keywords[key] = [value]

def load_special_headlines(filename):
  with open(filename, 'r') as f:
    lines = f.readlines()
    for line in lines:
      data = line.split(";")
      if len(data) != 3:
        continue
      date_str, category, headline = data
      
      category = category.strip()
      headline = headline.strip()

      special_headlines[(date_str, category)] = headline

def validate():

  # Keyword requirements
  sentences = sum(keywords.values(), [])
  for sentence in sentences:
    #print("Looking at sentence: " + sentence)
    key_reqs = re.findall("\[\w*\]", sentence)
    for key_req in key_reqs:
      #print("    looking at key req: " + key_req)
      if key_req not in keywords:
        print("Headline Validation Error: Keyword " + key_req + " needed.")

    special_reqs = re.findall("\{\w*\}", sentence)
    for special_req in special_reqs:
      valid = False
      for prefix in ["name", "number", "cowyboy", "cap", "plural"]:
        if special_req[1:].startswith(prefix): 
          valid = True
      if not valid:
        print("Headline Validation Error: Special command " + special_req + " not found.")

      if special_req[1:].startswith("capplural"):
        key = "[" + special_req[11:-1] + "]"
        if key not in keywords:
          print("Headline Validation Error: Capitalized Plural Keyword " + key + " needed.")
      elif special_req[1:].startswith("cap"):
        key = "[" + special_req[5:-1] + "]"
        if key not in keywords:
          print("Headline Validation Error: Capitalized Keyword " + key + " needed.")

  for key in keywords:
    cap_form = "{cap_" + key[1:-1] + "}"
    capplural_form = "{capplural_" + key[1:-1] + "}"
    for sentence in sentences:
      if key in sentence or cap_form in sentence or capplural_form in sentence:
        break
    else:
      print("Headline Validation Warning: Keyword " + key + " not used.")

def grammar_generate_recursive(str):
  recur = False
  for key in keywords:
    while key in str:
      str = str.replace(key, random.choice(keywords[key]), 1)
      recur = True

  special_sequences = re.findall("\{\w*\}", str)
  for sequence in special_sequences:
      str = str.replace(sequence, _special_keyword(sequence), 1)
      recur = True

  if recur:
    return grammar_generate_recursive(str)
  else:
    return _cleanup(str)

def _cleanup(str):
  
  # Replace "a vowelword" with "an vowelword"
  bad_as = re.findall(" [aA] [aeiouAEIOU]", str)
  for bad_a in bad_as:
    good_a = bad_a[:2] + "n" + bad_a[2:]
    str = str.replace(bad_a, good_a)

  # Replace "Person'S with "Person's" (artifact of .title())
  str = str.replace("'S", "'s")

  # Replace doubled punctuation
  str = str.replace("  ", " ")
  str = str.replace("!!", "!")
  str = str.replace("!.", ".")
  str = str.replace("!?", "?")
  str = str.replace("?!", "?")
  str = str.replace("?.", "?")
  str = str.replace("??", "?")

  return str

def _safe_capitalize(str):
  #words = re.split(' |-', str)
  #print("Capitalizing phrase: " + str)
  #for word in words:
  #  print("    Capitalizing word: " + word)
  #  if word[:1].isalpha():
  #    word = word[:1].upper() + word[1:]
  #return " ".join(words).strip()
  return str.title()

def _special_keyword(key_string):
  parts = key_string[1:-1].lower().strip().split("_")

  if parts[0] == "cap":
    key_str = "[" + key_string[5:-1] + "]"
    for key in keywords:
      while key in key_str:
        key_str = key_str.replace(key, random.choice(keywords[key]), 1)

    return _safe_capitalize(key_str)

  if parts[0] == "plural":
    key_str = key_string[8:-1]
    for key in keywords:
      while key in key_str:
        key_str = key_str.replace(key, random.choice(keywords[key]), 1)

    if key_str.endswith("s"):
      return key_str
    return key_str + "s"

  if parts[0] == "capplural":
    key_str = "[" + key_string[11:-1] + "]"
    for key in keywords:
      while key in key_str:
        key_str = key_str.replace(key, random.choice(keywords[key]), 1)

    key_str = _safe_capitalize(key_str)
    if key_str.endswith("s"):
      return key_str
    return key_str + "s"

  if parts[0] == "cowyboy":
    return "Horse Legs Wongowitz"
  if parts[0] == "name":
    is_female = ("f" in parts )
    specify_gender = "m" in parts or "f" in parts
    is_female = "f" in parts
    is_first = "first" in parts
    is_last = "last" in parts

    if specify_gender:
      name = flaustrian_names.get_full_name_specific(is_female, False, False)
    else:
      name = flaustrian_names.get_full_name()

    if is_first:
      return name.split(" ")[0]
    if is_last:
      return "".join(name.split(" ")[1:])
    
    return name

  if parts[0] == "number":
    min = 1
    max = 100
    try:
      if len(parts) > 1:
        max = int(parts[-1])
      if len(parts) > 2:
        min = int(parts[1])
    except ValueError:
      pass
    return str(random.randint(min, max))

  return ""

def get_daily_entertainment_headline():
  date_str = datetime.datetime.today().strftime("%Y-%m-%d")

  headline_profile = (date_str, "entertainment")

  if headline_profile in special_headlines:
    return special_headlines[headline_profile]

  weekday = datetime.date.today().weekday()
  if weekday == 0:
    return "Past TV Event"
  if weekday == 1:
    return "Movie Chart"
  if weekday == 2:
    return "Music News"
  if weekday == 3:
    return "Celebrity Gossip"
  if weekday == 4:
    return "Upcoming TV Event"
  if weekday == 5:
    return "Movie News"  
  return "Music Chart"


def test():
  #validate()
  #print("FLAUSTRIAN POP CHARTS, FEBRUARY 2 1965:\n")
  print()
  print(grammar_generate_recursive("[tv_news]"))  
  print()
  #for i in range(1, 5):
  #  print(grammar_generate_recursive("[tv_news]\n"))
  #  print(str(i) + ".\t" + grammar_generate_recursive("[recent_tv_headline]"))
  #  print(str(i) + ".\t" + #grammar_generate_recursive("[song_line]"))
  #print(grammar_generate_recursive("[business_headline]"))
  #print(grammar_generate_recursive("[sports_headline]"))

initialize()
test()
