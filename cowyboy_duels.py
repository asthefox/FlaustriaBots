import random
import database
from math import floor
from numpy.random import choice as nchoice

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