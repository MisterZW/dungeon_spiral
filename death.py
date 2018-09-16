from game_states import GameStates
from entity import RenderOrder
from game_messages import Message
from colors import Colors

def kill_player(player):
	player.char = '%'
	player.color = Colors.DARK_RED
	player.name = 'A hero formerly known as ' + player.name

	return Message('YOU DIED!', Colors.LIGHT_RED), GameStates.PLAYER_DEAD

def kill_monster(monster, game_map):
	death_message = Message('{0} is killed!'.format(monster.name.capitalize()), Colors.ORANGE)

	monster.char = '%'
	monster.color = Colors.DARK_RED
	monster.impassable = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'A ' + monster.name + ' corpse'
	monster.render_order = RenderOrder.CORPSE

	#monsters drop inventory when slain
	if monster.inventory:
		for item in monster.inventory.items:
			item.x = monster.x
			item.y = monster.y
			game_map.entities.append(item)
		monster.inventory = None

	return death_message