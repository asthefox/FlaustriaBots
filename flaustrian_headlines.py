import random
import re
import datetime
keywords = {}

def initialize():
  load_keywords("keywords_entertainment.txt")

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

def validate():

  # Keyword requirements
  sentences = sum(keywords.values(), [])
  for sentence in sentences:
    print("Looking at sentence: " + sentence)
    key_reqs = re.findall("\[\w*\]", sentence)
    for key_req in key_reqs:
      print("    looking at key req: " + key_req)
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
    if key in str:
      str = str.replace(key, random.choice(keywords[key]))
      recur = True

  if recur:
    return grammar_generate_recursive(str)
  else:
    return str

def get_daily_headline():
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
  initialize()
  validate()
  #print(mad_lib_recursive("[entertainment_headline]"))

#test()
initialize()