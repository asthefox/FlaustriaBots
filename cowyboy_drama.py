# Handles cowyboy duel text generation.
import random
import flaustrian_headlines

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
  celebrity = flaustrian_headlines.grammar_generate_recursive("[celebrity]")
  output = f"Gather one and all, the Cowyboy Duels are about to begin!\n\nToday the opening convocation will be performed by {celebrity}."

  output += """
    *"Before the five, the land was lawless.
    Man turned to saloons for solace.
    Behold the cowyboys before you.
    Observe their hubris, I implore you.
    Their buckles wide and guns ablaze,
    Take heed of their wicked ways.
    By Mongoose, Market, Moon, Book, Sun:
    The Cowyboy Show has begun."*
  """
  output += "\nThe crowd applauds in an onrush of politeness and anticipation.  The duel is beginning!\n"
  return output

def get_first_step(ordered_contestants):
  output = "The five cowyboys line up backs-to-backs in the dusty street outside the ol' saloon.\n"
  output += "Today, they are: "
  for c in ordered_contestants:
    suffix = ", "
    if c == ordered_contestants[-1]:
      suffix = ".\n"
    if c == ordered_contestants[-2]:
      suffix += ", and "
    output += format_name(c) + suffix

  output += "The saloon bell tolls high noon.  The cowyboys take ten paces, then disperse around the stage.\nWho will outlast their foes in today's Duel?\n"
  return output

def get_finale(winner):
  # TODO
	return f"Only one cowyboy remains!\nToday's winner is: {format_name(winner)}.\nThey take a bow as the crowd applauds their display of moral fortitude.  Who among them has won along with {winner['name']} today?"


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
  line += f"\n{format_name(eliminated)} has been eliminated."
  return line

def get_contest_output(ordered_contestants):
  outputs = []
  remaining_contestants = ordered_contestants.copy()

  # Opening convocation
  outputs.append(get_intro(remaining_contestants))
  outputs.append(get_first_step(remaining_contestants))

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