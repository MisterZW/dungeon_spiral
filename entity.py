import math
from enum import Enum
from random import randint

from components.item import Item

class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    VENDOR = 4
    ACTOR = 5

class Entity:

	"""
	A generic object class which represents players, enemies, items, etc.
	It represents anything with an (x, y) coordinate, char symbol, and color
	"""
	
	def __init__(self, x, y, char, color, name, impassable=False, render_order=RenderOrder.CORPSE, fighter=None, ai=None, 
		item=None, inventory=None, stairs=None, level=None, equipment=None, equippable=None, regeneration=None, vendor=None,
		description=None):

		#BASE TRAITS WHICH ALL ENTITIES POSSESS	
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.description = description
		self.impassable = impassable
		self.render_order = render_order

		#OPTIONAL COMPONENTS
		self.fighter = fighter
		self.ai = ai
		self.item = item
		self.inventory = inventory
		self.stairs = stairs
		self.level = level
		self.equipment = equipment
		self.equippable = equippable
		self.regeneration = regeneration
		self.vendor = vendor

		if self.fighter:
			self.fighter.owner = self

		if self.ai:
			self.ai.owner = self

		if self.item:
			self.item.owner = self

		if self.inventory:
			self.inventory.owner = self

		if self.stairs:
			self.stairs.owner = self

		if self.vendor:
			self.vendor.owner = self

		if self.level:
			self.level.owner = self

		if self.equipment:
			self.equipment.owner = self

		if self.equippable:
			self.equippable.owner = self

			#all equippables must possess item components to be carried in inventory
			if not self.item:
				self.item = Item()
				self.item.owner = self

		if self.regeneration:
			self.regeneration.owner = self


	def move(self, dx, dy):
		self.x += dx
		self.y += dy

	def move_to(self, abs_x, abs_y):
		self.x = abs_x
		self.y = abs_y

	def move_towards(self, target_x, target_y, game_map):
		entities = game_map.entities
		path = game_map.compute_path(self.x, self.y, target_x, target_y)

		if path:
			dx = path[0][0] - self.x
			dy = path[0][1] - self.y

			if game_map.walkable[path[0][0], path[0][1]] and not get_impassable_entities_at(entities, self.x + dx, self.y + dy):
				self.move(dx, dy)

	#compute the distance between this Entity and another using the distance formula
	def distance_to(self, other):
		x_dist = other.x - self.x
		y_dist = other.y - self.y
		return math.sqrt(x_dist ** 2 + y_dist ** 2)

	#same as distance_to, but for an absolute position rather than a relative distance
	def distance(self, x, y):
		x_dist = x - self.x
		y_dist = y - self.y
		return math.sqrt(x_dist ** 2 + y_dist ** 2)

	def teleport(self, game_map):
		entities = game_map.entities
		valid_destination = False

		while not valid_destination:
			new_x = randint(0, game_map.W - 1)
			new_y = randint(0, game_map.H - 1)
			if game_map.walkable[new_x, new_y]:
				for entity in entities:
					if entity.impassable and entity.x == new_x and entity.y == new_y:
						continue
				valid_destination = True

		self.move_to(new_x, new_y)

def get_impassable_entities_at(entities, x, y):
	for entity in entities:
		if entity.impassable and entity.x == x and entity.y == y:
			return entity
	return None