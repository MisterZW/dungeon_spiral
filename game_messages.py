import textwrap
from colors import Colors

class Message:
	def __init__(self, text, color=Colors.WHITE):
		self.text = text
		self.color = color

class MessageLog:
	def __init__(self, x, width, height):
		self.messages = []
		self.x = x
		self.width = width
		self.height = height

	def write(self, message):
		lines = textwrap.wrap(message.text, self.width)

		for line in lines:
			if len(self.messages) == self.height:
				del self.messages[0]
			self.messages.append(Message(line, message.color))