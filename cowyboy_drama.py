# Handles cowyboy duel text generation.
import random

def _init():
  global elim_lines
  global filler_lines
  elim_filename = "cowyboy_eliminations.txt"
  filler_filename = "cowyboy_filler.txt"
  with open(elim_filename,'r') as f:
    lines = f.readlines()
    elim_lines = list(map(lambda line: line.strip(), lines))
  with open(filler_filename,'r') as f:
    lines = f.readlines()
    filler_lines = list(map(lambda line: line.strip(), lines))


def format_name(cowyboy):
	return "**" + cowyboy["name"] + "**"

def get_intro(ordered_contestants):
  return """
  Please gather for the opening convocation:
  Before the five, the land was lawless.
  Man turned to saloons for solace.
  Behold the cowyboys before you.
  Observe their hubris, I implore you.
  Their buckles wide and guns ablaze,
  Take heed of their wicked ways.
  By Mongoose, Market, Moon, Book, Sun:
  The Cowyboy Show has begun.

  Now, let the duel begin!
  """

def get_finale(winner):
	return "The winner is: " + winner["name"]

def get_filler_output(remaining_contestants):
  c1 = random.choice(remaining_contestants)
  include_doubles = len(remaining_contestants) > 1
  if include_doubles:
    c2 = random.choice(list(filter(lambda c:c!=c1, remaining_contestants)))
    filler_choices = filler_lines
  else:
    filler_choices = list(filter(lambda line: "{c2}" not in line, filler_lines))
  
  line = random.choice(filler_choices)
  line = line.replace("{c1}", format_name(c1))
  line = line.replace("{c1_color}", c1["color"])
  if include_doubles:
    line = line.replace("{c2}", format_name(c2))
    line = line.replace("{c2_color}", c2["color"])

  return line

def get_elimination_output(eliminated, other_contestants):
  killerman = random.choice(other_contestants)
  line = random.choice(elim_lines)
  line = line.replace("{e}", format_name(eliminated))
  line = line.replace("{e_color}", eliminated["color"])
  line = line.replace("{c1}", format_name(killerman))
  line = line.replace("{c1_color}", killerman["color"])
  return line

def get_contest_output(ordered_contestants):
  outputs = []
  remaining_contestants = ordered_contestants.copy()

  # Opening convocation
  outputs.append(get_intro(remaining_contestants))

  # Each round/elimination
  while len(remaining_contestants) > 1:

    # Random number of filler events
    filler_events = random.choice([0, 1, 1, 2])
    for i in range(filler_events):
      outputs.append(get_filler_output(remaining_contestants))

    # Actual elimination
    eliminated = remaining_contestants[-1]
    remaining_contestants.remove(eliminated)
    outputs.append(get_elimination_output(eliminated, remaining_contestants))
    
  # Output winner
  outputs.append(get_finale(remaining_contestants[0]))
  return outputs

_init()