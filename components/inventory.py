from game_messages import Message
from colors import Colors
from random import randint

class Inventory:
	def __init__(self, capacity):
		self.base_capacity = capacity
		self.items = []

	@property
	def capacity(self):
		total = self.base_capacity
		if self.owner and self.owner.equipment:
			total += self.owner.equipment.carry_capacity_bonus
		if total > 26:
			total = 26
		return total

	def add(self, item):
		results = []

		if len(self.items) >= self.capacity:
			results.append({
				'item_added': None,
				'message': Message('You cannot carry more -- your inventory is full.', Colors.YELLOW)
			})
		else:
			results.append({
				'item_added': item,
				'message': Message('You pick up the {0}.'.format(item.name), Colors.WHITE)	
			})

			self.items.append(item)

		return results

	def silent_add(self, item):
		self.items.append(item)

	def use(self, item_entity, **kwargs):
		results = []

		item_component = item_entity.item

		if item_component.use_function is None:
			if item_entity.equippable:
				results.append({'equip': item_entity})
			else:
				results.append({'message': Message('The {0} has no obvious use right now.'.format(item_entity.name), Colors.YELLOW)})

		else:
			if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
				results.append({'targeting': item_entity})
			elif item_component.directional_targeting and not kwargs.get('direction'):
				results.append({'directional_targeting': item_entity})
			else:
				kwargs = {**item_component.function_kwargs, **kwargs}
				item_use_results = item_component.use_function(self.owner, item_entity, **kwargs)

				for result in item_use_results:
					if result.get('consumed'):
						self.remove_item(item_entity)

				results.extend(item_use_results)

		return results

	def drop(self, item):
		results = []

		#remove items being dropped if currently equipped
		eq = self.owner.equipment
		if item in eq.equipment:
			self.owner.equipment.toggle_equip(item)

		item.x = self.owner.x
		item.y = self.owner.y

		self.remove_item(item)
		results.append({'item_dropped': item, 'message': Message('You dropped the {0}'.format(item.name))})

		return results

	def relinquish(self):
		random_item = None
		if len(self.items) > 0:
			random_index = randint(0, len(self.items) - 1)
			random_item = self.items[random_index]
			#remove items being stolen if currently equipped
			eq = self.owner.equipment
			if random_item in eq.equipment:
				self.owner.equipment.toggle_equip(random_item)
			self.remove_item(random_item)
		return random_item

	def remove_item(self, item):
		self.items.remove(item)
