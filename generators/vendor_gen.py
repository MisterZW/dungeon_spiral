from components.vendor import Vendor
from entity import Entity, RenderOrder

from colors import Colors
from random import randint
from components.item import Item

class VendorGenerator:

	def __init__(self, game_map, item_generator):
		self.gmap = game_map
		self.player = game_map.player
		self.entities = game_map.entities
		self.dlvl = game_map.dlvl
		self.item_gen = item_generator
		self.vender_count = 0

	def make_random_vendor(self, x, y):
		vendor_component = Vendor(self.item_gen)

		vendor = Entity(x, y, '@', Colors.BLUE, 'Vendor {0}'.format(self.vender_count),
			 render_order=RenderOrder.VENDOR, vendor = vendor_component)

		self.vender_count += 1

		return vendor