import random
import database
from math import floor
from numpy.random import choice as nchoice
import cowyboy_roster as roster

def get_active_cowyboys():
  ids = database.get("flaustria/cowyboys/current")
  cowyboys = list(map(lambda id: database.get("flaustria/cowyboys/roster/" + str(id)), ids))
  return cowyboys

def determine_placement(cowyboys):
  # Find odds of each being eliminated
  total_power = sum(int(cowyboy["power"]) for cowyboy in cowyboys)
  weights = list(map(lambda cowyboy: cowyboy["power"]/total_power, cowyboys))

  # Debug print
  #print("Odds of success:")
  #for i in range(len(cowyboys)):
  #  print(cowyboys[i]["name"] + str(weights[i]))

  # Select the index of the winner 5 times
  ordered_indexes = nchoice(len(cowyboys), len(cowyboys), p=weights, replace=False)

  # Return the ordered list of winners
  return list(map(lambda i: cowyboys[i], ordered_indexes))

def determine_payoffs(cowyboys):

  VIG = 0.1

  # Determine odds
  total_power = sum(int(cowyboy["power"]) for cowyboy in cowyboys)
  odds = list(map(lambda cowyboy: float(cowyboy["power"] / total_power), cowyboys))

  # Debug print
  #print("Odds of success:")
  #for i in range(len(cowyboys)):
  #  print(cowyboys[i]["name"] + str(odds[i]))

  # Invert odds to get payoffs
  # (Plus take vig and round to nearest 0.25)
  payoffs = list(map(lambda odd: round((1 - VIG) * 4 / odd) / 4, odds))

  return payoffs

def update_cowyboys_after_duel(results):

  winner = results[0]
  loser = results[-1]

  # Write changed data to cowyboys
  winner["wins"] += 1
  winner["power"] += 10
  for cowyboy in results:
    cowyboy["duels"] += 1
    roster.write_cowyboy_data(cowyboy)

  # Make new cowyboy
  new_cowyboy_id = roster.get_next_id()
  new_cowyboy_color = loser["color"]
  new_cowyboy = roster.generate_cowyboy(new_cowyboy_color, new_cowyboy_id)
  roster.write_cowyboy_data(new_cowyboy)

  # Update current cowyboy IDs
  updated_current_ids = list(map(lambda c: c["id"], results))
  updated_current_ids.remove(loser["id"])
  updated_current_ids.append(new_cowyboy_id)
  roster.write_current_ids(updated_current_ids)

