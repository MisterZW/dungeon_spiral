from game_messages import Message
from colors import Colors
from components.ai import ConfusedMonster, StunnedMonster
from random import randint
from generators.random_utils import roll_dice

import inspect

from entity import get_impassable_entities_at

def heal(*args, **kwargs):
	entity = args[0]
	amount = roll_dice(5, 4)

	results = []

	if entity.fighter.hp == entity.fighter.max_hp:
		results.append({'consumed': False, 'message': Message('You are already at full HP.', Colors.YELLOW)})

	else:
		if (entity.fighter.max_hp - entity.fighter.hp) < amount:
			amount = (entity.fighter.max_hp - entity.fighter.hp)
		entity.fighter.heal(amount)
		results.append({'consumed': True, 'message': Message('You recover {0} HP!'.format(amount), Colors.GREEN)})
		
	return results

def gain_level(*args, **kwargs):
	source = kwargs.get('source')

	results = []

	if source.level:
		xp_short = source.level.exp_to_next_level
		results.append({'consumed': True, 'xp': xp_short, 'message': Message('You feel more experienced!')})

	return results


def cast_lightning(*args, **kwargs):
	caster = args[0]
	game_map = kwargs.get('game_map')
	entities = game_map.entities
	damage = kwargs.get('damage')
	max_range = kwargs.get('max_range')

	results = []

	target = None
	nearest = max_range + 1

	for entity in entities:
		if entity.fighter and entity != caster and game_map.fov[entity.x, entity.y]:
			distance = caster.distance_to(entity)

			if distance < nearest:
				target = entity
				nearest = distance

	if target:
		results.append({'consumed': True, 'target': target, 'message': Message(
			'A lightning bolt strikes the {0} for {1} damage'.format(target.name, damage))})
		results.extend(target.fighter.take_damage(damage))
	else:
		results.append({'consumed': False, 'target': None, 'message': Message(
			'You hear a rumble of thunder, but nothing happens.', Colors.RED)})

	return results

def cast_fireball(*args, **kwargs):
	game_map = kwargs.get('game_map')
	entities = game_map.entities
	damage = kwargs.get('damage')
	radius = kwargs.get('radius')
	target_x = kwargs.get('target_x')
	target_y = kwargs.get('target_y')

	results = []

	if not game_map.fov[target_x, target_y]:
		results.append({'consumed': False, 'message': Message(
			'You can\'t target a tile you can\'t see', Colors.YELLOW)})

	else:
		results.append({'consumed': True, 'message': Message('BOOM!', Colors.RED )})

		for entity in entities:
			if entity.fighter and entity.distance(target_x, target_y) <= radius:
				adjusted_damage = round( damage - (3 * entity.distance(target_x, target_y)) )
				results.append({'message': Message(
					'{0} is engulfed! {0} burns for {1} damage'.format(entity.name, adjusted_damage), Colors.ORANGE)})
				results.extend(entity.fighter.take_damage(adjusted_damage))

	return results

def cast_confuse(*args, **kwargs):
	game_map = kwargs.get('game_map')
	entities = game_map.entities
	target_x = kwargs.get('target_x')
	target_y = kwargs.get('target_y')
	radius = kwargs.get('radius')

	results = []

	if not game_map.fov[target_x, target_y]:
		results.append({'consumed': False, 'message': Message(
			'You can\'t target a tile you can\'t see', Colors.YELLOW)})

	else:
		results.append({'consumed': True, 'message': Message('A shimmering haze falls.', Colors.LIGHT_PINK)})
		for entity in entities:
			if entity.ai and entity.distance(target_x, target_y) <= radius:
				confused_ai = ConfusedMonster(prev_ai=entity.ai, duration=10)
				confused_ai.owner = entity
				entity.ai = confused_ai

				results.append({'message': Message('{0} begins to wander aimlessly'.format(entity.name, Colors.LIGHT_CYAN))})

	return results

def cast_teleport(*args, **kwargs):
	target = kwargs.get('target')
	game_map = kwargs.get('game_map')
	entities = game_map.entities

	results = []

	target.teleport(game_map)

	results.append({'consumed': True, 'message': Message(' You blink, and {0} is gone'.format(target.name), Colors.LIGHT_CYAN)})

	return results

def cast_arcane_storm(*args, **kwargs):
	source = kwargs.get('source')
	game_map = kwargs.get('game_map')
	radius = kwargs.get('radius')

	target_x = source.x
	target_y = source.y

	entities = game_map.entities
	player = game_map.player

	results = []

	results.append({'consumed': True, 'message': Message('A tempestuous vortex discharges energy wildly!', Colors.LIGHT_PINK)})
	for entity in entities:
		if entity.fighter and entity.distance(target_x, target_y) <= radius:
			
			damage = randint(0, entity.fighter.hp - 1)
			if entity == source:
				damage = damage // 2 
			results.extend(entity.fighter.take_damage(damage))
			entity.teleport(game_map)
			results.append({'message': Message(
				'{0} takes {1} damage as its body twists into the ether'.format(entity.name, damage), Colors.VIOLET)})
			
	return results

#creates a cascading domino effect of displacement -- if one entity hits another, the momentum transfers through
#confuses enemies for a brief duration
def cast_gust_of_wind(*args, **kwargs):
	caster = args[0]
	wand = args[1]
	game_map = kwargs.get('game_map')
	direction = kwargs.get('direction')
	max_range = kwargs.get('range')
	entities = game_map.entities

	wand.item.charges -= 1

	results = []
	
	x = caster.x
	y = caster.y
	dx, dy = get_dxdy(direction)

	if wand.item.charges > 0 :
		results.append({'charge_used': True, 'message': Message('A gust of wind blows {0}!'.format(direction), Colors.GRAY)})
	else:
		results.append({'consumed': True, 'message': Message('A gust of wind blows {0}! The wand crumbles to dust.'.format(direction), Colors.GRAY)})

	for i in range(max_range + 1):
		x += dx
		y += dy
		if (x > 0 and y > 0 and x < game_map.W - 1 and y < game_map.H - 1):
			for entity in entities:
				if entity.x == x and entity.y == y and not entity.stairs:
					#prevents monsters from pursuing player the round of activation
					if entity.ai and not isinstance(entity.ai, StunnedMonster):
						stunned_ai = StunnedMonster(prev_ai=entity.ai, duration=2)
						stunned_ai.owner = entity
						entity.ai = stunned_ai
						results.append({'message': Message('{0} is dazed by the force of the wind.'.format(entity.name), Colors.GRAY)})
					if game_map.walkable[x+dx, y+dy] and not get_impassable_entities_at(entities, x+dx, y+dy):
						entity.x += dx
						entity.y += dy

	return results

def cast_dig(*args, **kwargs):
	caster = args[0]
	wand = args[1]
	game_map = kwargs.get('game_map')
	direction = kwargs.get('direction')
	max_range = kwargs.get('range')

	wand.item.charges -= 1

	results = []

	x = caster.x
	y = caster.y

	dx, dy = get_dxdy(direction)

	for i in range(max_range):
		x += dx
		y += dy
		if (x >= 1 and y >= 1 and x < game_map.W-1 and y < game_map.H-1):
			game_map.walkable[x, y] = True
			game_map.transparent[x, y] = True

	if wand.item.charges > 0 :
		results.append({'charge_used': True, 'message': Message('A giant shovel flies {0}!'.format(direction), Colors.GRAY)})
	else:
		results.append({'consumed': True, 'message': Message('A giant shovel flies {0}! The wand crumbles to dust.'.format(direction), Colors.GRAY)})

	return results

def get_dxdy(direction):
	if direction == 'N':
		return (0, -1)
	elif direction == 'E':
		return (1, 0)
	elif direction == 'W':
		return (-1, 0)
	if direction == 'S':
		return (0, 1)
	elif direction == 'NE':
		return (1, -1)
	elif direction == 'NW':
		return (-1, -1)
	if direction == 'SE':
		return (1, 1)
	elif direction == 'SW':
		return (-1, 1)

	return (0, 0)