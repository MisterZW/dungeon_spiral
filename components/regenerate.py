class Regeneration:
	def __init__(self, fighter, permanent=False, duration=10, amount=1):
		self.fighter = fighter
		self.permanent = permanent
		self.duration = duration
		self.amount = amount
		
	def regen(self):
		if self.permanent:
			self.fighter.hp += self.amount
			if self.fighter.hp > self.fighter.max_hp:
				self.fighter.hp = self.fighter.max_hp
		if self.duration > 0:
			self.duration -= 1
			self.fighter.hp += self.amount
			if self.fighter.hp > self.fighter.max_hp:
				self.fighter.hp = self.fighter.max_hp
		else:
			self.owner.regeneration = None