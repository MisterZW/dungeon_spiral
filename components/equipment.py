from components.equipment_slots import EquipmentSlots

class Equipment:
	def __init__(self, main_hand=None, off_hand=None, head=None, body=None, feet=None, hands=None, neck=None,
		l_finger=None, r_finger=None, cloak=None):

		#first element is None so that the EquipmentSlots enum matches the array indices exactly
		self.equipment = [None, main_hand, off_hand, head, body, feet, hands, neck, l_finger,
			r_finger, cloak]

	@property
	def max_hp_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.max_hp_bonus
		return bonus

	@property
	def power_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.power_bonus
		return bonus

	@property
	def defense_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.defense_bonus
		return bonus

	@property
	def accuracy_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.accuracy_bonus
		return bonus

	@property
	def armor_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.armor_bonus
		return bonus

	@ property
	def carry_capacity_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.carry_capacity_bonus
		return bonus

	@ property
	def fov_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.fov_bonus
		return bonus

	@ property
	def stealth_bonus(self):
		bonus = 0
		for gear in self.equipment:
			if gear and gear.equippable:
				bonus += gear.equippable.stealth_bonus
		return bonus

	#removes or equips target item, or swaps items if slot is in use
	def toggle_equip(self, equippable_entity):
		results = []

		slot_index = (equippable_entity.equippable.slot.value)

		if self.equipment[slot_index] == equippable_entity:
			self.equipment[slot_index] = None
			results.append({'removed' : equippable_entity})
		else:
			if self.equipment[slot_index]:
				results.append({'removed': self.equipment[slot_index]})
			self.equipment[slot_index] = equippable_entity
			results.append({'equipped': equippable_entity})

		return results


	