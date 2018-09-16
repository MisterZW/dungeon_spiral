from game_messages import Message
from colors import Colors
from random import randint

class BasicMonster:
	def take_turn(self, target, game_map):
		results = []
		monster = self.owner

		if game_map.fov[monster.x, monster.y]:
			if monster.distance_to(target) >= 2:
				monster.move_towards(target.x, target.y, game_map)

			elif target.fighter.hp > 0:
				attack_results = monster.fighter.attack(target)
				results.extend(attack_results)

		return results

class ConfusedMonster:
	def __init__(self, prev_ai, duration=10):
		self.prev_ai = prev_ai
		self.duration = duration

	def take_turn(self, target, game_map):
		results = []
		monster = self.owner

		if self.duration > 0:
			self.duration -= 1
			dest_x = monster.x + randint(-1, 1)
			dest_y = monster.y + randint(-1, 1)

			if dest_x != monster.x and dest_y != monster.y:
				monster.move_towards(dest_x, dest_y, game_map)
		else:
			monster.ai = self.prev_ai
			results.append({'message': Message('{0} is no longer confused'.format(monster.name), Colors.LIGHT_PINK)})

		return results

class StunnedMonster:
	def __init__(self, prev_ai, duration=10):
		self.prev_ai = prev_ai
		self.duration = duration

	def take_turn(self, target, game_map):
		results = []
		monster = self.owner

		if self.duration > 0:
			#do nothing
			self.duration -= 1
		else:
			monster.ai = self.prev_ai
			results.append({'message': Message('{0} is no longer stunned'.format(monster.name), Colors.LIGHT_RED)})

		return results


class SuicideMonster:
	def take_turn(self, target, game_map):
		results = []
		monster = self.owner

		if game_map.fov[monster.x, monster.y]:
			if monster.distance_to(target) >= 2:
				monster.move_towards(target.x, target.y, game_map)

			#Explode -- use scroll targeting self
			elif target.fighter.hp > 0:
				results.append({'message': Message('{0} cries "WITNESS ME!"'.format(monster.name), Colors.LIGHT_CYAN)})
				fireball = monster.inventory.items[0]
				suicide_results = monster.inventory.use(fireball, game_map=game_map, target_x=monster.x, target_y=monster.y)
				results.extend(suicide_results)

		return results

class ThiefMonster:

	def take_turn(self, target, game_map):
		results = []
		monster = self.owner

		if game_map.fov[monster.x, monster.y]:
			if monster.distance_to(target) >= 2:
				monster.move_towards(target.x, target.y, game_map)

			elif len(target.inventory.items) > 0 and len(monster.inventory.items) < monster.inventory.capacity:
				if monster.fighter.roll_to_hit(target):
					stolen_item = target.inventory.relinquish()
					monster.inventory.silent_add(stolen_item)
					monster.teleport(game_map)
					results.append({'message': Message('{0} teleports away with your {1}!'.format(monster.name, stolen_item.name), Colors.LIGHT_CYAN)})
				else:
					results.append({'message': Message('{0} swipes at your possessions, but misses'.format(monster.name), Colors.WHITE)})
			else:
				monster.teleport(game_map)
				results.append({'message': Message('You blink, and {0} is gone'.format(monster.name), Colors.WHITE)})

		return results

class SpyMonster:

	def take_turn(self, target, game_map):
		results = []
		monster = self.owner

		if monster.distance_to(target) >= 2:
			monster.move_towards(target.x, target.y, game_map)

		elif target.fighter.hp > 0:
			if monster.fighter.roll_to_hit(target):
				target.fighter.take_damage(2)
				target.fighter.base_max_hp -= 2
				results.append({'message': Message('{0} jabs you with poisoned blade! You feel weaker!'.format(monster.name), Colors.WHITE)})
			else:
				results.append({'message': Message('{0} lunges wildly but fails to connect'.format(monster.name), Colors.WHITE)})

			monster.teleport(game_map)
			results.append({'message': Message('{0} throws something at the ground, then disappears in a plume of smoke.'.format(monster.name), Colors.GRAY)})

		return results
