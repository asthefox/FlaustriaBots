import random
import re
import datetime
keywords = {}
special_headlines = {}

# TODO: {number_min_max (positional)}
# TODO: {name_(f|m|first|last) (keyword)}

def initialize():
  load_keywords("keywords_entertainment.txt")
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

  for key in keywords:
    for sentence in sentences:
      if key in sentence:
        break
    else:
      print("Headline Validation Warning: Keyword " + key + " not used.")

def grammar_generate_recursive(str):
  recur = False
  for key in keywords:
    while key in str:
      str = str.replace(key, random.choice(keywords[key]), 1)
      recur = True

  if recur:
    return grammar_generate_recursive(str)
  else:
    return str

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
  validate()
  print(grammar_generate_recursive("[sports_headline]"))

initialize()
test()
