class Item:
	def __init__(self, use_function=None, targeting=False, directional_targeting=False, targeting_msg=None, charges=0, price=1, **kwargs):
		self.use_function = use_function
		self.targeting = targeting
		self.directional_targeting = directional_targeting
		self.targeting_msg = targeting_msg
		self.function_kwargs = kwargs
		self.charges = charges
		self.price = price