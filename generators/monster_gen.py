from entity import Entity, RenderOrder
from components.fighter import Fighter
from components.ai import BasicMonster, SuicideMonster, ThiefMonster, SpyMonster
from components.inventory import Inventory
from components.item import Item
from components.regenerate import Regeneration
from random import randint
from generators.random_utils import get_random_key, from_dlvl
from colors import Colors
from game_messages import Message
import math

from item_functions import cast_fireball


class MonsterGenerator:

	def __init__(self, game_map):
		self.gmap = game_map
		self.player = game_map.player
		self.entities = game_map.entities
		self.dlvl = game_map.dlvl

		self.monsters = {
			'Garden Gnome': from_dlvl([[50, 1], [30, 3], [20, 5], [10, 7], [5, 9]], self.dlvl),
			'Hill Dwarf': from_dlvl([[20, 1], [30, 3], [50, 5], [30, 7], [10, 9]], self.dlvl),
		 	'Gnomish Firebomber': from_dlvl([[2,1], [5, 2], [10,3], [15, 6]], self.dlvl),
			'Orcish Spy': from_dlvl([[5,2], [10, 4], [15, 6]], self.dlvl), 
			'Obnoxious Nymph': from_dlvl([[5,2], [10, 4], [15, 6]], self.dlvl),
			'Behemoth Troll': from_dlvl([[5,3], [10, 4], [25, 5], [50, 7]], self.dlvl)
		}
		

	def make_random_monster(self, x, y):

		random_monster =  get_random_key(self.monsters)

		if random_monster == 'Garden Gnome':
			fighter_component = Fighter(hp=10, defense=0, power=3, accuracy=0, xp=25)
			ai_component = BasicMonster()
			monster = Entity(x, y, 'g', Colors.GREEN, 'Garden Gnome', impassable=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, 
				ai=ai_component)
		elif random_monster == 'Hill Dwarf':
			fighter_component = Fighter(hp=16, defense=1, power=4, accuracy=1, xp=75)
			ai_component = BasicMonster()
			monster = Entity(x, y, 'h', Colors.BLUE, 'Hill Dwarf', impassable=True, render_order=RenderOrder.ACTOR,
				fighter=fighter_component, ai=ai_component)
		elif random_monster == 'Behemoth Troll':
			fighter_component = Fighter(hp=32, defense=4, power=8, accuracy=6, armor=2, xp=250)
			ai_component = BasicMonster()
			regen_component = Regeneration(fighter_component, permanent=True)
			monster = Entity(x, y, 'T', Colors.DARK_GREEN, 'Behemoth Troll', impassable=True, render_order=RenderOrder.ACTOR,
				fighter=fighter_component, ai=ai_component, regeneration = regen_component)
		elif random_monster == 'Gnomish Firebomber':	
			fighter_component = Fighter(hp=10, defense=3, power=0, accuracy=0, xp=50)
			ai_component = SuicideMonster()
			item_component = Item(use_function=cast_fireball, targeting=True, targeting_msg=Message(
				'Left click to select a target, or right click to cancel.', Colors.LIGHT_CYAN), damage=18, radius=3)
			item = Entity(x, y, '?', Colors.RED, 'scroll of fireball', render_order=RenderOrder.ITEM, item=item_component)
			inventory_component = Inventory(1)
			inventory_component.silent_add(item)
			monster = Entity(x, y, 'g', Colors.RED, 'Gnomish Firebomber', impassable=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, 
				ai=ai_component, inventory=inventory_component)
		elif random_monster == 'Orcish Spy':
			fighter_component = Fighter(hp=16, defense=1, power=1, accuracy=2, xp=100)
			ai_component = SpyMonster()
			monster = Entity(x, y, 'o', Colors.BLACK, 'Orcish Spy', impassable=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, 
				ai=ai_component)
		else:
			fighter_component = Fighter(hp=20, defense=0, power=0, accuracy=2, xp=100)
			inventory_component = Inventory(3)
			ai_component = ThiefMonster()
			monster = Entity(x, y, 'n', Colors.BROWN, 'Obnoxious Nymph', impassable=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, 
				ai=ai_component, inventory=inventory_component)

		return monster
