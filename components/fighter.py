from game_messages import Message
from random import randint

class Fighter:

	MAX_HIT_PERCENT = 98
	MIN_HIT_PERCENT = 2
	BASE_HIT_PERCENT = 50

	def __init__(self, hp, defense, power, accuracy, armor=0, xp=0):
		self.base_max_hp = hp
		self.hp = hp
		self.base_defense = defense
		self.base_power = power
		self.base_accuracy = accuracy
		self.base_armor = armor
		self.xp = xp

	@property
	def max_hp(self):
		bonus = 0
		if self.owner and self.owner.equipment:
			bonus += self.owner.equipment.max_hp_bonus
		return self.base_max_hp + bonus

	@property
	def power(self):
		bonus = 0
		if self.owner and self.owner.equipment:
			bonus += self.owner.equipment.power_bonus
		return self.base_power + bonus

	@property
	def defense(self):
		bonus = 0
		if self.owner and self.owner.equipment:
			bonus += self.owner.equipment.defense_bonus
		return self. base_defense + bonus

	@property
	def accuracy(self):
		bonus = 0
		if self.owner and self.owner.equipment:
			bonus += self.owner.equipment.accuracy_bonus
		return self.base_accuracy + bonus

	@property
	def armor(self):
		bonus = 0
		if self.owner and self.owner.equipment:
			bonus += self.owner.equipment.armor_bonus
		return self.base_armor + bonus

	def take_damage(self, damage):
		results = []

		self.hp -= damage
		if self.hp <= 0:
			results.append({'dead' : self.owner, 'xp': self.xp})

		return results

	def heal(self, amount):
		self.hp += amount
		if self.hp > self.max_hp:
			self.hp = self.max_hp

	def attack(self, target):

		results = []

		if self.roll_to_hit(target):
			damage = self.power - target.fighter.armor
			if damage > 0:
				results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(self.owner.name.capitalize(), target.name, str(damage)))})
				results.extend(target.fighter.take_damage(damage))
			else:
				results.append({'message': Message('{0} attacks {1}. It\'s not very effective...'.format(self.owner.name.capitalize(), target.name))})
		else:
			results.append({'message': Message('{0} misses {1}.'.format(self.owner.name.capitalize(), target.name))})
		return results

	def roll_to_hit(self, target):

		hit_percent = self.BASE_HIT_PERCENT + 3 * (self.accuracy - target.fighter.defense)
		if hit_percent < self.MIN_HIT_PERCENT:
			hit_percent = self.MIN_HIT_PERCENT
		elif hit_percent > self.MAX_HIT_PERCENT:
			hit_percent = self.MAX_HIT_PERCENT

		attack_roll = randint(0, 100)

		return attack_roll <= hit_percent
