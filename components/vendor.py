class Vendor:
	def __init__(self, item_gen, stock_capacity=26):
		self.stock = []
		self.capacity = stock_capacity
		self.item_gen = item_gen
		for i in range(0, 5):
			self.stock.append(self.item_gen.make_random_item(0, 0))

	def get_price(self, index):
		price = None
		if index < len(self.stock):
			price = self.stock[index].item.price
		return price

	def sell(self, index):
		item = None
		if index < len(self.stock):
			item = self.stock[index]
			self.stock.remove(item)
		return item

	def purchase(self, item):
		if len(self.stock) < self.capacity:
			self.stock.append(item)
