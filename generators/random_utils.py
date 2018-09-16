from numpy.random import choice
from random import randint

#gets a random dictionary choice and returns its key -- weights options by the value
def get_random_key(choice_dict):
	choices = list(choice_dict.keys())
	chances = list(choice_dict.values())

	decimal_chances = [chance / sum(chances) for chance in chances]

	return choice(choices, p=decimal_chances)

#used to select different weights for items/monsters by dungeon level
def from_dlvl(table, dungeon_level):
	for(value, level) in reversed(table):
		if dungeon_level >= level:
			return value
	return 0

#simulate n rolls of an s-sided die, then return the sum
def roll_dice(n, s):
	result = 0
	for i in range(n):
		result += randint(1, s)
	return result
