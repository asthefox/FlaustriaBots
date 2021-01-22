import random

keywords = {}
with open("word_lists.txt",'r') as f:
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
  
def mad_lib_recursive(str):
  recur = False
  for key in keywords:
    if key in str:
      str = str.replace(key, random.choice(keywords[key]))
      recur = True

  if recur:
    return mad_lib_recursive(str)
  else:
    return str

def test():
  print(mad_lib_recursive("[entertainment_headline]"))

test()