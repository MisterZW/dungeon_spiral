from random import randint

from tdl.map import Map
from entity import Entity, RenderOrder
from components.stairs import Stairs
from components.vendor import Vendor
from components.inventory import Inventory
from colors import Colors

from game_messages import Message
from generators.item_gen import ItemGenerator
from generators.monster_gen import MonsterGenerator
from generators.vendor_gen import VendorGenerator
from generators.random_utils import from_dlvl

class GameMap(Map):
	W = 80
	H = 40
	MAX_ROOMS = 25
	MAX_ROOM_SIZE = 12
	MIN_ROOM_SIZE = 5

	FOV_RADIUS = 6
	ENEMY_FOV_RADIUS = 9
	FOV_ALGORITHM = 'BASIC'
	FOV_LIGHT_WALLS = True

	def __init__(self, player, entities, dlvl=1):
		super().__init__(self.W, self.H)
		self.player = player
		self.entities = entities
		self.dlvl = dlvl
		self.item_gen = ItemGenerator(self)
		self.monster_gen = MonsterGenerator(self)
		self.vendor_gen = VendorGenerator(self, self.item_gen)

		self.MAX_MONSTERS_PER_ROOM = from_dlvl([[2,1], [3,3], [4,5], [5,7], [6,9]], self.dlvl)
		self.MAX_ITEMS_PER_ROOM = from_dlvl([[1,1], [2,2], [3,4], [4,6]], self.dlvl)

		self.explored = [[False for y in range(self.H)] for x in range(self.W)]
		self.make_map()

	def player_FOV(self):
		radius = self.FOV_RADIUS + self.player.equipment.fov_bonus
		self.compute_fov(self.player.x, self.player.y, fov=self.FOV_ALGORITHM, radius=radius, light_walls=self.FOV_LIGHT_WALLS)

	def enemy_FOV(self):
		radius = self.ENEMY_FOV_RADIUS - self.player.equipment.stealth_bonus
		self.compute_fov(self.player.x, self.player.y, fov=self.FOV_ALGORITHM, radius=radius, light_walls=self.FOV_LIGHT_WALLS)

	def place_entities(self, room):	
		self.place_monsters(room)
		self.place_items(room)
		self.place_vendors(room)

	def place_vendors(self, room):
		vendor_present = randint(0, 10) > 8
		if vendor_present:
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
				vendor = self.vendor_gen.make_random_vendor(x, y)
				self.entities.append(vendor)

	def place_monsters(self, room):
		enemy_count = randint(0, self.MAX_MONSTERS_PER_ROOM)

		for i in range(enemy_count):
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
				monster = self.monster_gen.make_random_monster(x, y)
				self.entities.append(monster)

	def place_items(self, room):
		item_count = randint(0, self.MAX_ITEMS_PER_ROOM)

		for i in range(item_count):
			x = randint(room.x1 + 1, room.x2 - 1)
			y = randint(room.y1 + 1, room.y2 - 1)

			if not any([entity for entity in self.entities if entity.x == x and entity.y == y]):
				item = self.item_gen.make_random_item(x, y)
				self.entities.append(item)


	def make_map(self):
		rooms = []
		room_count = 0

		stairs_x = None
		stairs_y = None

		for r in range(self.MAX_ROOMS):
			w = randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
			h = randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
			x = randint(0, self.W - w - 1)
			y = randint(0, self.H - h - 1)

			#generate a new random candidate room
			new_room = Rectangle(x, y, w, h)

			for room in rooms:
				if new_room.intersect(room):
					break  #skip any invalid rooms
			else:
				self.create_room(new_room)
				(new_x, new_y) = new_room.center()

				#stairs will be placed in the last room
				stairs_x = new_x
				stairs_y = new_y

				#place the player in the first room generated
				if(room_count) == 0:
					self.player.x = new_x
					self.player.y = new_y
					self.place_items(new_room)
				#tunnel connect all subsequent rooms to previous room
				else:
					(prev_x, prev_y) = rooms[room_count-1].center()
					#randomly select tunneling order (horoz/vert)
					if randint(0, 1) == 0:
						self.create_tunnel_h(prev_x, new_x, prev_y)
						self.create_tunnel_v(prev_y, new_y, new_x)
					else:
						self.create_tunnel_v(prev_y, new_y, prev_x)
						self.create_tunnel_h(prev_x, new_x, new_y)

					self.place_entities(new_room)

				rooms.append(new_room)
				room_count += 1

		#place the downstairs in the center of the last room		
		stairs_component = Stairs(self.dlvl + 1)
		downstairs = Entity(stairs_x, stairs_y, '>', Colors.WHITE, 'Stairs to level {0}'.format(
			self.dlvl + 1), render_order=RenderOrder.STAIRS, stairs = stairs_component)
		self.entities.append(downstairs)

	def create_room(self, room):
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.walkable[x, y] = True
				self.transparent[x, y] = True


	def create_tunnel_v(self, y1, y2, x):
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.walkable[x, y] = True
			self.transparent[x, y] = True


	def create_tunnel_h(self, x1, x2, y):
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.walkable[x, y] = True
			self.transparent[x, y] = True

def next_floor(player, display, dlvl):
	entities = [player]
	new_map = GameMap(player, entities, dlvl)
	display.clear_new_level()
	display.gmap = new_map

	player.fighter.heal(player.fighter.max_hp // 2)

	display.write(Message('You take a moment to rest and recover your strength.', Colors.LIGHT_VIOLET))

	return new_map, entities

class Rectangle:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h

	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2
		return (center_x, center_y)

	#check if this rectangle intesects with another
	def intersect(self, other):
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
			self.y1 <= other.y2 and self.y2 >= other.y1)