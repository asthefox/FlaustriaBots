import random
import string

_names = {}

def get_full_name():
  return get_full_name_specific(random.random() < 0.5, False, False)

def get_full_name_specific(isFemale, isVladagar, isForeign):
  first = get_first_name(isFemale, isVladagar, isForeign)
  last = get_last_name(isVladagar, isForeign)

  modifications = [
    #hyphenate_first_name
    lambda first, last: (first + "-" + get_first_name(isFemale, isVladagar, isForeign), last),
    #of_place
    lambda first, last: (first, random.choice(["O\'", "Mc", "von ", "of ", "de ", "Mac", "de la ", "l\'", "ter", "St. "]) + last),
    #generational
    lambda first, last: (first, last + " " + ("Jr." if random.random() < 0.6 else ("III" if random.random() < 0.6 else random.choice(["IV", "V", "VI", "VII", "VIII", "IX", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"])))),
    #first_as_last
    lambda first, last: (first, get_first_name(isFemale, isVladagar, isForeign)),
    #last_as_first
    lambda first, last: (get_last_name(isVladagar, isForeign), last),
    #cross-gendered first
    lambda first, last: (get_first_name(not isFemale, isVladagar, isForeign), last),
    #middle initial
    lambda first, last: (first + " " + random.choice(string.ascii_letters).upper() + ".", last),
    #nickname
    lambda first, last: (random.choice(["Old", "Little", "Tiny", "Slick", "Fast", "Big", "Good Time", "Sweet"]) + " " + first, last)
  ]

  # modify
  if random.random() < 0.25:
    first, last = random.choice(modifications)(first, last)
  return first + " " + last

def get_first_name(isFemale, isVladagar, isForeign):
  key1 = "male"
  if isFemale: key1 = "female"

  key2 = "flaustrian"
  if isForeign or random.random() < 0.15: key2 = "foreign"
  if isVladagar: key2 = "vladagar"

  return random.choice(_names[(key1, key2)])

def get_last_name(isVladagar, isForeign):
  prefix_key = suffix_key = "flaustrian"
  if isForeign or random.random() < 0.15: prefix_key = "foreign"
  if isForeign or random.random() < 0.15: suffix_key = "foreign"
  if isVladagar:
    prefix_key = suffix_key = "vladagar"

  prefix = random.choice(_names[("prefix", prefix_key)])
  suffix = random.choice(_names[("suffix", prefix_key)])

  if (is_vowel(prefix[-1]) and is_vowel(suffix[0])) or (len(prefix) > 1 and prefix[-2] == prefix[-1] and prefix[-1] == suffix[0]):
    suffix = suffix[1:]

  return prefix + suffix

def is_vowel(char):
  return char in "aeiouAEIOU"

def _initialize():
  _load_file_set("male", "male_names")
  _load_file_set("female", "female_names")
  _load_file_set("prefix", "last_name_prefixes")
  _load_file_set("suffix", "last_name_suffixes")

def _load_file_set(key, file_prefix):
  _load_file(key, "flaustrian", file_prefix + "_flaustrian")
  _load_file(key, "vladagar", file_prefix + "_vladagar")
  _load_file(key, "foreign", file_prefix + "_foreign")

def _load_file(key1, key2, filename):
  filename = "character_names/" + filename + ".txt"
  with open(filename,'r') as f:
    lines = f.readlines()
    lines = map(lambda line: line.strip(), lines)
    _names[(key1, key2)] = list(filter(lambda line: line != "", lines))

def _test():
  print("There was a diplomatic conference.")
  print("\nThe Flaustrian representatives were:")
  for i in range(10):
    print(get_full_name())
  print("\nThe Vladagar representatives were:")
  for i in range(10):
    print(get_full_name_specific(random.random() < 0.5, True, False))
  print("\nThe Zanzerlander representatives were:")
  for i in range(10):
    print(get_full_name_specific(random.random() < 0.5, False, True))

_initialize()
#_test()
