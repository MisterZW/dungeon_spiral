from entity import Entity, RenderOrder
from item_functions import heal, gain_level, cast_fireball, cast_confuse, cast_lightning, cast_arcane_storm, cast_gust_of_wind, cast_dig, cast_leech
from random import randint
from generators.random_utils import get_random_key
from colors import Colors
from game_messages import Message

from components.item import Item
from components.equipment_slots import EquipmentSlots
from components.equippable import Equippable

class ItemGenerator:

	item_type_chances = {'potion': 30, 'scroll': 30, 'wand': 8, 'equippable': 30, 'amulet': 2, 'ring': 2}

	potions = {'healing potion': 95, 'knowledge potion': 5}
	scrolls = {'scroll of fireball': 25, 'scroll of confusion': 25, 'scroll of lightning': 25, 'scroll of arcane storm': 25}
	wands = {'wand of wind': 40, 'wand of digging': 40, 'wand of blood': 20}
	amulets = {'daylight brooch': 40}
	rings = {'ring of protection': 40, 'ring of stealth': 40}

	equippables = {'sword': 7, 'hammer': 7, 'shield': 7, 'leather cap': 10, 'steel visor': 3, 'leather armor': 10,
		'chain mail': 3, 'leather boots': 10, 'greaves': 3, 'cloak of displacement': 1, 'gauntlets of dexterity': 1,
		'gauntlets of power': 1, 'bracers of defense': 2, 'lantern': 5, 'elven cloak': 1}

	ilvl = {'1': 50, '2': 30, '3': 10, '4':7, '5': 3}

	def __init__(self, game_map):
		self.gmap = game_map
		self.player = game_map.player
		self.entities = game_map.entities
		self.dlvl = game_map.dlvl

	def make_random_item(self, x, y):

		random_item_type = get_random_key(self.item_type_chances)
		if random_item_type == 'potion':
			return self.make_random_potion(x, y)
		elif random_item_type == 'wand':
			return self.make_random_wand(x, y)
		elif random_item_type == 'equippable':
			return self.make_random_equippable(x, y)
		elif random_item_type == 'amulet':
			return self.make_random_amulet(x, y)
		elif random_item_type == 'ring':
			return self.make_random_ring(x, y)
		else:
			return self.make_random_scroll(x, y)

		return None


	def make_random_potion(self, x, y):
		random_potion_type = get_random_key(self.potions)

		if random_potion_type == 'healing potion':
			item_component = Item(use_function=heal)
			item = Entity(x, y, '!', Colors.DARK_RED, 'healing potion', render_order=RenderOrder.ITEM, item=item_component)
		else:
			item_component = Item(use_function=gain_level)
			item = Entity(x, y, '!', Colors.GREEN, 'knowledge potion', render_order=RenderOrder.ITEM, item=item_component)

		return item

	def make_random_scroll(self, x, y):
		random_scroll_type = get_random_key(self.scrolls)
		
		if random_scroll_type == 'scroll of fireball':
			item_component = Item(use_function=cast_fireball, targeting=True, targeting_msg=Message(
				'Left click to select a target, or right click to cancel.', Colors.LIGHT_CYAN), damage=18, radius=3)
			item = Entity(x, y, '?', Colors.RED, 'scroll of fireball', render_order=RenderOrder.ITEM, item=item_component)
		elif random_scroll_type == 'scroll of confusion':
			item_component = Item(use_function=cast_confuse, targeting=True, targeting_msg=Message(
				'Left click to select a target, or right click to cancel.', Colors.LIGHT_CYAN), radius=1)
			item = Entity(x, y, '?', Colors.GREEN, 'scroll of confusion', render_order=RenderOrder.ITEM, item=item_component)
		elif random_scroll_type == 'scroll of lightning':
			item_component = Item(use_function=cast_lightning, damage=25, max_range=5)
			item = Entity(x, y, '?', Colors.YELLOW, 'scroll of lightning', render_order=RenderOrder.ITEM, item=item_component)
		else:
			item_component = Item(use_function=cast_arcane_storm, radius=4)
			item = Entity(x, y, '?', Colors.PURPLE, 'scroll of arcane storm', render_order=RenderOrder.ITEM, item=item_component)

		return item

	def make_random_wand(self, x, y):
		random_wand_type = get_random_key(self.wands)

		if random_wand_type == 'wand of digging':
			item_component = Item(use_function=cast_dig, directional_targeting=True, targeting_msg=Message(
					'In which direction? (ESC to cancel)', Colors.WHITE), range=7, charges=5)
			item = Entity(x, y, '/', Colors.BROWN, 'wand of digging', render_order=RenderOrder.ITEM, item=item_component)
		elif random_wand_type == 'wand of blood':
			item_component = Item(use_function=cast_leech, directional_targeting=True, targeting_msg=Message(
					'In which direction? (ESC to cancel)', Colors.WHITE), range=4, charges=3)
			item = Entity(x, y, '/', Colors.DARK_RED, 'wand of blood', render_order=RenderOrder.ITEM, item=item_component)
		else:	
			item_component = Item(use_function=cast_gust_of_wind, directional_targeting=True, targeting_msg=Message(
					'In which direction? (ESC to cancel)', Colors.WHITE), range=6, charges=5)
			item = Entity(x, y, '/', Colors.WHITE, 'wand of wind', render_order=RenderOrder.ITEM, item=item_component)

		return item

	def make_random_amulet(self, x, y):
		random_amulet_type = get_random_key(self.amulets)

		equippable_component = Equippable(EquipmentSlots.NECK, fov_bonus=3, accuracy_bonus=1)
		item = Entity(x, y, '"', Colors.YELLOW, 'daylight brooch', equippable=equippable_component)

		return item

	def make_random_ring(self, x, y):

		random_ring_type = get_random_key(self.rings)
		if random_ring_type == 'ring of protection':
			equippable_component = Equippable(EquipmentSlots.L_FINGER, armor_bonus=1, defense_bonus=1)
			item = Entity(x, y, '=', Colors.VIOLET, 'ring of protection', equippable=equippable_component)
		else:
			equippable_component = Equippable(EquipmentSlots.R_FINGER, stealth_bonus=3)
			item = Entity(x, y, '=', Colors.VIOLET, 'ring of stealth', equippable=equippable_component)

		return item


	def make_random_equippable(self, x, y):
		random_equip_type = get_random_key(self.equippables)
		
		if random_equip_type == 'sword':
			equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3, accuracy_bonus=1)
			item = Entity(x, y, '|', Colors.SKY, 'sword', equippable=equippable_component)
		elif random_equip_type == 'hammer':
			equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=4, accuracy_bonus=-1)
			item = Entity(x, y, '|', Colors.DARK_ORANGE, 'hammer', equippable=equippable_component)
		elif random_equip_type == 'shield':
			equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=2)
			item = Entity(x, y, '[', Colors.BROWN, 'shield', equippable=equippable_component)
		elif random_equip_type == 'lantern':
			equippable_component = Equippable(EquipmentSlots.OFF_HAND, fov_bonus=3)
			item = Entity(x, y, '(', Colors.YELLOW, 'lantern', equippable=equippable_component)
		elif random_equip_type == 'leather cap':
			equippable_component = Equippable(EquipmentSlots.HEAD, defense_bonus=2)
			item = Entity(x, y, '^', Colors.BROWN, 'leather cap', equippable=equippable_component)
		elif random_equip_type == 'steel visor':
			equippable_component = Equippable(EquipmentSlots.HEAD, defense_bonus=2, armor_bonus=1, max_hp_bonus=5, accuracy_bonus=-2)
			item = Entity(x, y, '^', Colors.GRAY, 'steel visor', equippable=equippable_component)
		elif random_equip_type == 'leather armor':
			equippable_component = Equippable(EquipmentSlots.BODY, defense_bonus=3, max_hp_bonus=5)
			item = Entity(x, y, '#', Colors.BROWN, 'leather armor', equippable=equippable_component)
		elif random_equip_type == 'chain mail':
			equippable_component = Equippable(EquipmentSlots.BODY, defense_bonus=1, armor_bonus=2, max_hp_bonus=10, accuracy_bonus=-2)
			item = Entity(x, y, '#', Colors.GOLD, 'chain mail', equippable=equippable_component)
		elif random_equip_type =='leather boots':
			equippable_component = Equippable(EquipmentSlots.FEET, defense_bonus=1, max_hp_bonus=3)
			item = Entity(x, y, ')', Colors.BROWN, 'leather boots', equippable=equippable_component)
		elif random_equip_type =='greaves':
			equippable_component = Equippable(EquipmentSlots.FEET, defense_bonus=1, armor_bonus=1, max_hp_bonus=5, accuracy_bonus=-1)
			item = Entity(x, y, ')', Colors.GOLD, 'greaves', equippable=equippable_component)
		elif random_equip_type == 'gauntlets of dexterity':
			equippable_component = Equippable(EquipmentSlots.HANDS, accuracy_bonus=5)
			item = Entity(x, y, ':', Colors.DARK_GREEN, 'gauntlets of dexterity', equippable=equippable_component)
		elif random_equip_type == 'gauntlets of power':
			equippable_component = Equippable(EquipmentSlots.HANDS, power_bonus=1, carry_capacity_bonus=6)
			item = Entity(x, y, ':', Colors.DARK_RED, 'gauntlets of power', equippable=equippable_component)
		elif random_equip_type == 'bracers of defense':
			item_level = int(get_random_key(self.ilvl))
			DR = 0
			if item_level > 3:
				DR = 1
			equippable_component = Equippable(EquipmentSlots.HANDS, defense_bonus=item_level, armor_bonus=DR)
			item = Entity(x, y, ':', Colors.VIOLET, 'bracers of defense +{0}'.format(item_level), equippable=equippable_component)
		elif random_equip_type == 'elven cloak':
			equippable_component = Equippable(EquipmentSlots.CLOAK, stealth_bonus=3)
			item = Entity(x, y, '&', Colors.GREEN, 'elven cloak', equippable=equippable_component)
		else:
			equippable_component = Equippable(EquipmentSlots.CLOAK, defense_bonus=3, accuracy_bonus=3)
			item = Entity(x, y, '&', Colors.BLUE, 'displacement cloak', equippable=equippable_component)

		return item