from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment
from entity import Entity, RenderOrder
from colors import Colors

def initialize_player(name):
    fighter_component = Fighter(hp=30, defense=2, power=5, accuracy=3)
    inventory_component = Inventory(8)
    level_component = Level()
    equipment_component = Equipment()

    player = Entity(0, 0, '@', Colors.WHITE, name, impassable=True, render_order=RenderOrder.ACTOR,
    	fighter=fighter_component, inventory=inventory_component, level=level_component, equipment=equipment_component,
    	description = 'an intrepid adventurer')

    return player