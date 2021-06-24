import re

def is_only_numbers(text):
  #returns true if text is only numbers with no letters or other characters
  pattern = re.compile(r"\D")
  matches = pattern.findall(text)
  return len(matches) < 1