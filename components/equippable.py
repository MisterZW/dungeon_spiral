from components.equipment_slots import EquipmentSlots

class Equippable:
	def __init__(self, slot, power_bonus=0, defense_bonus=0, accuracy_bonus=0, armor_bonus=0, max_hp_bonus=0,
		carry_capacity_bonus=0, fov_bonus=0, stealth_bonus=0):
		self.slot = slot
		self.power_bonus = power_bonus
		self.defense_bonus = defense_bonus
		self.accuracy_bonus = accuracy_bonus
		self.armor_bonus = armor_bonus
		self.max_hp_bonus = max_hp_bonus
		self.carry_capacity_bonus = carry_capacity_bonus
		self.fov_bonus = fov_bonus
		self.stealth_bonus = stealth_bonus