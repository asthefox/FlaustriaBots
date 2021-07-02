import cowyboy_roster
import cowyboy_duels as duels
import cowyboy_drama as drama

def reseed():
  cowyboy_roster.seed_initial_cowyboys()

def test_full_duel():
  cowyboys = duels.get_active_cowyboys()
  odds = duels.determine_payoffs(cowyboys)

  print("PLACE YER BETS NOW!\nODDS:")
  for i in range(len(cowyboys)):
    print(f"{cowyboys[i]['name']} - {odds[i]:g}:1")

  results = duels.determine_placement(cowyboys)
  output = drama.get_contest_output(results)

  for line in output:
    print(line)
    input("..")

  print("\nTHE RESULTS:")
  for i in range(len(cowyboys)):
    print(f"{i+1}. {drama.format_name(results[i])}")

  winner_odds_index = cowyboys.index(results[0])
  winner_odds = odds[winner_odds_index]
  print(f"{drama.format_name(results[0])} pays {winner_odds} to 1")

test_full_duel()