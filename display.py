from game_messages import MessageLog, Message
from map_utils import GameMap
from entity import RenderOrder
from colors import Colors
from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen, vendor_main_menu, vendor_buy_menu, vendor_sell_menu
import tdl
import math

class Display:

    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50

    PANEL_HEIGHT = 10
    BAR_WIDTH = 20
    PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

    MESSAGE_X = BAR_WIDTH + 2
    MESSAGE_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
    MESSAGE_HEIGHT = PANEL_HEIGHT - 1

    def __init__(self, gmap=None):
        self.root_console = tdl.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title='Dungeon Spiral')
        self.con = tdl.Console(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.panel = tdl.Console(self.SCREEN_WIDTH, self.PANEL_HEIGHT)
        self.log = MessageLog(self.MESSAGE_X, self.MESSAGE_WIDTH, self.MESSAGE_HEIGHT)
        self.gmap = gmap

    def write(self, msg):
        self.log.write(msg)


    def render_all(self, mouse_xy, game_state, targeting_item):

        if game_state == GameStates.TARGETING:
            self.con.clear(fg=Colors.WHITE, bg=Colors.BLACK)
        
        for x, y in self.gmap:
            wall = not self.gmap.transparent[x, y]

            if self.gmap.fov[x,y]:
                if wall:
                    self.con.draw_char(x, y, None, fg=None, bg=Colors.LIGHT_WALL)
                else:
                    dist = dist_to(mouse_xy, x, y)
                    if game_state == GameStates.TARGETING and dist <= targeting_item.item.function_kwargs['radius']:
                        red_component = round(180 + (20*dist))
                        g_b = round(20 * dist)
                        color = (red_component, g_b, g_b)

                        self.con.draw_char(x, y, None, fg=None, bg=color)
                    else:
                        self.con.draw_char(x, y, None, fg=None, bg=Colors.LIGHT_GROUND)

                self.gmap.explored[x][y] = True
                
            elif self.gmap.explored[x][y]:
                if wall:
                    self.con.draw_char(x, y, None, fg=None, bg=Colors.DARK_WALL)
                else:
                    self.con.draw_char(x, y, None, fg=None, bg=Colors.DARK_GROUND)

        render_ordered_entities = sorted(self.gmap.entities, key=lambda x: x.render_order.value)

        for entity in render_ordered_entities:
            draw_entity(self.con, entity, self.gmap)

        self.root_console.blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0)

        self.panel.clear(fg=Colors.WHITE, bg=Colors.BLACK)
        self.con.clear(fg=Colors.WHITE, bg= Colors.BLACK)


        log_y = 1
        for message in self.log.messages:
            self.panel.draw_str(self.log.x, log_y, message.text, bg=None, fg=message.color)
            log_y += 1

        player = self.gmap.player

        render_bar(self.panel, 1, 1, self.BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, Colors.DARK_RED, Colors.DARKEST_RED, Colors.WHITE)
        render_bar(self.panel, 1, 3, self.BAR_WIDTH, 'EXP', player.level.current_xp, player.level.exp_to_next_level, Colors.BLUE, Colors.PURPLE, Colors.WHITE)

        self.panel.draw_str(1, 0, '{0}'.format(player.name), fg=Colors.WHITE, bg=None)
        self.panel.draw_str(1, 5, 'DUNGEON LEVEL: {0}'.format(self.gmap.dlvl), fg=Colors.WHITE, bg=None)
        self.panel.draw_str(1, 6, 'CASHOLA: {0}'.format(player.inventory.cashola), fg=Colors.YELLOW, bg=None)
        self.con.draw_str(1, 1, self.get_mouse_targets(mouse_xy))

        self.root_console.blit(self.panel, 0, self.PANEL_Y, self.SCREEN_WIDTH, self.PANEL_HEIGHT, 0, 0)

        if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
            if game_state == GameStates.SHOW_INVENTORY:
                prompt = 'Select an item to use, or press ESC to cancel.\n'
            else: 
                prompt = 'Select an item to drop, or press ESC to cancel.\n'
            inventory_menu(self, prompt, player)

        elif game_state == GameStates.CHARACTER_SCREEN:
            character_screen(self, player)

        elif game_state == GameStates.LEVEL_UP:
            level_up_menu(self, 'LEVEL UP! CHOOSE WHICH STAT TO ADVANCE:', player)

        elif game_state == GameStates.VENDOR_SELECT:
            vendor_main_menu(self, 'HOW CAN I HELP YOU TODAY?', player)

        elif game_state == GameStates.VENDOR_SELL:
            vendor = None
            for entity in render_ordered_entities:
                if entity.vendor and entity.x == player.x and entity.y == player.y:
                    vendor = entity
            vendor_sell_menu(self, 'WHAT WOULD YOU LIKE TO BUY?', player, vendor)

        elif game_state == GameStates.VENDOR_BUY:
            vendor = None
            for entity in render_ordered_entities:
                if entity.vendor and entity.x == player.x and entity.y == player.y:
                    vendor = entity
            vendor_buy_menu(self, 'WHAT WOULD YOU LIKE TO SELL?', player, vendor)

    #get the name of entities selected by the cursor
    def get_mouse_targets(self, mouse_coordinates):
        x, y = mouse_coordinates

        matches = [entity.name for entity in self.gmap.entities if self.gmap.fov[entity.x, entity.y] and entity.x == x and entity.y == y]
        names = ', '.join(matches)

        return names.capitalize()

    def clear_all(self):
        clear(self.con, self.gmap.entities)

    def clear_new_level(self):
        self.con = tdl.Console(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

#render an HP/EXPERIENCE/MANA etc bar
def render_bar(console, x, y, total_width, name, value, maximum, bar_color, back_color, text_color):
    bar_width = round((value / maximum) * total_width)

    if bar_width < 0:
        bar_width = 0

    #background
    console.draw_rect(x, y, total_width, 1, None, bg=back_color)

    #draw bar in the foreground
    console.draw_rect(x, y, bar_width, 1, None, bg=bar_color)

    text = name + ": " + str(value) + "/" + str(maximum)
    midpoint = x + (total_width - len(text)) // 2

    #label the bar in the middle with name, current, and max values
    console.draw_str(midpoint, y, text, fg=text_color, bg=None)


def clear(console, entities):
    for entity in entities:
        clear_entity(console, entity)

def draw_entity(console, entity, game_map):
    if game_map.fov[entity.x, entity.y] or (entity.stairs and game_map.explored[entity.x][entity.y]):
        console.draw_char(entity.x, entity.y, entity.char, entity.color, bg=None)

def clear_entity(console, entity):
    console.draw_char(entity.x, entity.y, ' ', entity.color, bg=None)

def dist_to(origin, x, y):
    start_x, start_y = origin
    x_dist = x - start_x
    y_dist = y - start_y
    return math.sqrt(x_dist ** 2 + y_dist ** 2)
